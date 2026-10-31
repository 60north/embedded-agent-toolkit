#!/usr/bin/env python3
"""Check canonical filesystem discovery. This is NOT a live-client test."""
import argparse
import json
import os
from pathlib import Path
import shutil
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import importlib.util
spec=importlib.util.spec_from_file_location('installer',Path(__file__).resolve().parents[1]/'install-embedded.py')
installer=importlib.util.module_from_spec(spec);spec.loader.exec_module(installer)

def inspect(home,project=None):
    links,configs,manifest=installer.layout(Path(home).resolve(),project)
    result={'filesystem':'FAIL','live_clients':'NOT RUN','tools':{name:shutil.which(name) for name in ('claude','codex','kicad-cli','renode','renode-test')},'warnings':[]}
    if not manifest.is_file():result['reason']='Not installed';return result
    cfg=json.loads(manifest.read_text());canonical=Path(cfg['toolkit'])/'skills'
    result['canonical']=str(canonical);result['memory']=cfg['memory']
    if not all(installer.same(link,canonical) for link in links):result['reason']='Discovery paths are not the same directory';return result
    names=[]
    for file in sorted(canonical.glob('*/SKILL.md')):
        if not all(os.path.samefile(link/file.relative_to(canonical),file) for link in links):raise ValueError('Different skill files')
        names.append(file.parent.name)
    result['skills']=names;result['filesystem']='PASS'
    settings=links[0].parent/'settings.json'
    if settings.is_file():
        s=settings.read_text()
        if 'superpowers' in s or 'prettier' in s or 'eslint' in s:result['warnings'].append('Existing Claude plugins/web hooks may conflict; inspect settings.json')
    for f in configs:
        if not f.is_file() or installer.BEGIN not in f.read_text():result['filesystem']='FAIL';result['warnings'].append(f'Missing bootstrap: {f}')
    return result
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--home',type=Path,default=Path.home());p.add_argument('--project');a=p.parse_args()
    result=inspect(a.home,a.project);print(json.dumps(result,indent=2));sys.exit(0 if result['filesystem']=='PASS' else 1)
