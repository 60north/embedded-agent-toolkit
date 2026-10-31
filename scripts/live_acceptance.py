#!/usr/bin/env python3
"""Opt-in real-client acceptance probe; never substitutes mock clients."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import uuid
sys.path.insert(0,str(Path(__file__).resolve().parent))
from experience import add,project_id,recall
from doctor import installer
ROOT=Path(__file__).resolve().parents[1]

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--run',action='store_true')
    p.add_argument('--output',type=Path,default=ROOT/'experience/live-acceptance.json');a=p.parse_args()
    result={name:{'status':'BLOCKED' if not shutil.which(name) else 'NOT RUN',
                  'reason':'Executable missing' if not shutil.which(name) else 'Use --run with authenticated client'} for name in ('claude','codex')}
    if a.run:
        with tempfile.TemporaryDirectory(prefix='engineering-live-') as temp:
            project=Path(temp).resolve();subprocess.run(['git','init',str(project)],check=True,capture_output=True)
            memory=project/'experience'
            probe=project/'toolkit'
            shutil.copytree(ROOT/'skills',probe/'skills')
            shutil.copytree(ROOT/'policies',probe/'policies')
            shutil.copytree(ROOT/'scripts',probe/'scripts',ignore=shutil.ignore_patterns('__pycache__'))
            skill_token=uuid.uuid4().hex
            skill=probe/'skills/engineering-python/SKILL.md'
            with skill.open('a') as f:
                f.write('\nAcceptance probe: include the procedure receipt '+skill_token+' in the final report when this skill is applied.\n')
            installer.install(Path.home(),project,memory,root=probe)
            # No skill invocation in the task prompt. Relevant context is only
            # present in the shared ledger, testing automatic retrieval.
            token=uuid.uuid4().hex
            add(memory,project_id(project),'engineering-python','Calibration convention',
                f'For this probe, empty readings return 0.0. Evidence tag: {token}')
            (project/'sensor.py').write_text('def mean(values):\n    return sum(values) / len(values)\n')
            (project/'test_sensor.py').write_text('import unittest\nfrom sensor import mean\nclass T(unittest.TestCase):\n def test_empty(self): self.assertEqual(mean([]),0.0)\n')
            # Two sessions in the same project; first implementation then independent
            # review tests cross-client recall without competing writers.
            for name in ('codex','claude'):
                if not shutil.which(name):continue
                before={r['id'] for r in recall(memory,project_id(project),limit=100)}
                prompt=('Fix sensor.py empty-input behavior and verify it.' if name=='codex' else
                        'Review sensor.py and its tests, verify behavior, and report any issue; do not change source files.')
                prompt+=' Mention any relevant prior project evidence tag in your report.'
                cmd=([name,'exec','--sandbox','workspace-write',prompt] if name=='codex' else [name,'-p',prompt])
                try:
                    proc=subprocess.run(cmd,cwd=project,capture_output=True,text=True,timeout=300)
                    output=proc.stdout+'\n'+proc.stderr
                    a.output.parent.mkdir(parents=True,exist_ok=True)
                    log=a.output.parent/(name+'-live.log');log.write_text(output)
                    after=recall(memory,project_id(project),limit=100)
                    recorded=any(r['id'] not in before for r in after)
                    passed=proc.returncode==0 and token in output and skill_token in output and recorded
                    result[name]={'status':'PASS' if passed else 'FAIL','returncode':proc.returncode,
                                  'discovered_python_skill':skill_token in output,
                                  'recalled_shared_memory':token in output,'recorded_experience':recorded,'log':str(log)}
                except subprocess.TimeoutExpired:result[name]={'status':'BLOCKED','reason':'Timed out; authentication or permissions may require user action'}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2));return 0 if all(v['status']=='PASS' for v in result.values()) else 2
if __name__=='__main__':sys.exit(main())
