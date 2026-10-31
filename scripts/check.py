#!/usr/bin/env python3
"""Run checks with durable evidence; missing tools and zero-test suites cannot pass."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import uuid
import xml.etree.ElementTree as ET
from experience import add_run, project_id


def revision(project):
    r=subprocess.run(['git','-C',str(project),'rev-parse','HEAD'],capture_output=True,text=True)
    head=r.stdout.strip() if r.returncode==0 else 'unversioned'
    r=subprocess.run(['git','-C',str(project),'status','--porcelain'],capture_output=True,text=True)
    return head+(' dirty' if r.stdout.strip() else '')


def run(command, project, root, skill, claim, timeout=300, artifacts=(), validator=None, inputs=(), folder=None):
    project=Path(project).resolve();root=Path(root).resolve()
    # One folder per run holds report, log and tool outputs, so pruning removes it whole.
    folder=Path(folder) if folder else root/'runs'/uuid.uuid4().hex;folder.mkdir(parents=True,exist_ok=True)
    log=folder/'output.log';report=folder/'report.json'
    data=dict(command=list(command),revision=revision(project),project=project_id(project),
              skill=skill,claim=claim,created=datetime.now(timezone.utc).isoformat(),artifacts={},inputs={},
              log=str(log),status='BLOCKED',exit_code=None)
    for path in inputs:
        path=Path(path).resolve()
        if path.is_file(): data['inputs'][str(path)]=hashlib.sha256(path.read_bytes()).hexdigest()
    if not command or not shutil.which(command[0]):
        output='Required executable not found: '+(command[0] if command else '(empty)')
    else:
        try:
            result=subprocess.run(command,cwd=project,capture_output=True,text=True,errors='replace',timeout=timeout)
            output=result.stdout+'\n'+result.stderr
            data['exit_code']=result.returncode
            data['status']='PASS' if result.returncode==0 else 'FAIL'
            if data['status']=='PASS':
                for path in artifacts:
                    path=Path(path).resolve()
                    if not path.is_file():raise ValueError(f'Missing expected artifact: {path}')
                    data['artifacts'][str(path)]=hashlib.sha256(path.read_bytes()).hexdigest()
                if validator: validator()
        except subprocess.TimeoutExpired as e:
            output=f'Timed out after {timeout}s\n{e.stdout or ""}\n{e.stderr or ""}';data['status']='FAIL'
        except (ValueError,OSError,ET.ParseError) as e:
            output=locals().get('output','')+'\n'+str(e);data['status']='FAIL'
    log.write_text(output,encoding='utf-8')
    data['log_sha256']=hashlib.sha256(log.read_bytes()).hexdigest()
    report.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
    add_run(root,data,report)
    return data, report


def validate_robot(path):
    tree=ET.parse(path)
    tests=tree.findall('.//test')
    if not tests: raise ValueError('No Robot tests executed')
    if any(t.find('status') is None or t.find('status').get('status')!='PASS' for t in tests):
        raise ValueError('Robot suite contains failed or skipped tests')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project',type=Path,default=Path.cwd())
    p.add_argument('--memory',type=Path,default=Path(__file__).resolve().parents[1]/'experience')
    p.add_argument('--timeout',type=int,default=300)
    sub=p.add_subparsers(dest='mode',required=True)
    g=sub.add_parser('run');g.add_argument('--skill',required=True);g.add_argument('--claim',required=True);g.add_argument('command',nargs=argparse.REMAINDER)
    k=sub.add_parser('kicad');k.add_argument('kind',choices=['erc','drc']);k.add_argument('file',type=Path)
    r=sub.add_parser('renode');r.add_argument('scenario',type=Path)
    a=p.parse_args();artifacts=[];validator=None;inputs=[]
    root=a.memory.resolve();project=a.project.resolve();folder=root/'runs'/uuid.uuid4().hex
    if a.mode=='run':
        cmd=a.command[1:] if a.command[:1]==['--'] else a.command;skill=a.skill;claim=a.claim
    elif a.mode=='kicad':
        source=a.file.resolve();inputs=[source]
        skill='engineering-kicad-schematic' if a.kind=='erc' else 'engineering-kicad-pcb'
        claim=f'KiCad {a.kind.upper()} CLI violations only; visual/electrical review separate'
        result=folder/'violations.json';artifacts=[result]
        cmd=['kicad-cli','sch' if a.kind=='erc' else 'pcb',a.kind,'--format','json','--exit-code-violations','--output',str(result)]
        if a.kind=='drc':cmd.append('--refill-zones')
        cmd.append(str(source))
        def validator():
            report=json.loads(result.read_text())
            # KiCad exit-code-violations is authoritative, also require a real JSON report.
            if not isinstance(report,dict) or not report:raise ValueError('Empty KiCad report')
        # Inspect supported options; unsupported versions remain BLOCKED with evidence.
        if shutil.which('kicad-cli'):
            help_run=subprocess.run(cmd[:3]+['--help'],capture_output=True,text=True,timeout=30)
            needed=['--format','--exit-code-violations','--output']+(['--refill-zones'] if a.kind=='drc' else [])
            if help_run.returncode or any(flag not in help_run.stdout+help_run.stderr for flag in needed):
                print('BLOCKED: installed KiCad CLI lacks required options',file=sys.stderr);return 2
    else:
        skill='engineering-renode';claim='Renode Robot scenario assertions (not physical hardware)'
        out=folder/'robot';out.mkdir(parents=True)
        result=folder/'robot_output.xml'
        scenario=a.scenario.resolve();inputs=[scenario]
        cmd=['renode-test','--results-dir',str(out),str(scenario)]
        def validator():
            candidates=list(out.rglob('*.xml'))
            valid=[]
            for candidate in candidates:
                try:
                    if ET.parse(candidate).getroot().tag=='robot': valid.append(candidate)
                except ET.ParseError: pass
            if not valid:raise ValueError('No Robot output XML produced')
            for candidate in valid: validate_robot(candidate)
            result.write_text(valid[0].read_text())
        # validator creates normalized report first; evidence is then added below.
    data,report=run(cmd,project,root,skill,claim,a.timeout,artifacts,validator,inputs,folder)
    if a.mode=='renode' and data['status']=='PASS':
        data['artifacts'][str(result)]=hashlib.sha256(result.read_bytes()).hexdigest()
        report.write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps({'status':data['status'],'report':str(report)},indent=2))
    return 0 if data['status']=='PASS' else 2 if data['status']=='BLOCKED' else 1
if __name__=='__main__':sys.exit(main())
