#!/usr/bin/env python3
"""Three-way update of selected vendored Superpowers files from a local Git checkout."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[1]

def git(source,*args):
    return subprocess.check_output(['git','-C',str(source),*args])

def digest(data):return hashlib.sha256(data).hexdigest()

def merge(ours,base,theirs):
    if ours==base:return theirs
    if theirs==base or ours==theirs:return ours
    with tempfile.TemporaryDirectory() as directory:
        paths=[Path(directory)/n for n in ('ours','base','theirs')]
        for path,data in zip(paths,(ours,base,theirs)):path.write_bytes(data)
        result=subprocess.run(['git','merge-file','-p',*[str(p) for p in paths]],capture_output=True)
        if result.returncode:raise ValueError('Three-way merge conflict; active files left unchanged')
        return result.stdout

def update(source,ref,root=ROOT,apply=False):
    if not re.fullmatch('[0-9a-f]{40}',ref):raise ValueError('Use an explicit reviewed 40-character commit')
    source=Path(source).resolve();root=Path(root)
    manifest_path=root/'vendor/superpowers.json'
    manifest=json.loads(manifest_path.read_text())
    if git(source,'rev-parse',ref).decode().strip()!=ref:raise ValueError('Commit mismatch')
    changes={};new={}
    # Only reviewed selected files are managed. Newly added upstream files need
    # explicit inspection, never silently activate more workflow instructions.
    for path,info in manifest['files'].items():
        local=root/path
        current=local.read_bytes()
        base=git(source,'show',manifest['revision']+':'+path)
        try:theirs=git(source,'show',ref+':'+path)
        except subprocess.CalledProcessError:raise ValueError(f'Upstream removed {path}; review migration manually')
        value=merge(current,base,theirs)
        changes[local]=value
        new[path]={'upstream_sha256':digest(theirs),'installed_sha256':digest(value)}
    license_data=git(source,'show',ref+':LICENSE')
    changes[root/'vendor/SUPERPOWERS-LICENSE']=license_data
    manifest.update(revision=ref,files=new)
    changes[manifest_path]=(json.dumps(manifest,indent=2)+'\n').encode()
    if apply:
        backups={p:p.read_bytes() for p in changes}
        written=[]
        try:
            for p,data in changes.items():written.append(p);p.write_bytes(data)
        except OSError:
            for p in reversed(written):p.write_bytes(backups[p])
            raise
    return {'status':'updated' if apply else 'preview','revision':ref,'files':len(new),
            'next':'Review upstream skill tree for new dependencies; run tests and live smoke before accepting.'}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',required=True,type=Path)
    p.add_argument('--ref',required=True);p.add_argument('--apply',action='store_true');a=p.parse_args()
    try:print(json.dumps(update(a.source,a.ref,apply=a.apply),indent=2))
    except (ValueError,OSError,subprocess.SubprocessError) as e:p.exit(1,str(e)+'\n')
if __name__=='__main__':main()
