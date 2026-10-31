#!/usr/bin/env python3
"""Local shared experience ledger. SQLite WAL supports independent client writers."""
import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import uuid


def project_id(path):
    path=Path(path).resolve()
    p=subprocess.run(['git','-C',str(path),'rev-parse','--path-format=absolute','--git-common-dir'],capture_output=True,text=True)
    identity=p.stdout.strip() if p.returncode==0 else str(path)
    return hashlib.sha256(identity.encode()).hexdigest()[:24]


@contextmanager
def connect(root):
    root=Path(root); root.mkdir(parents=True,exist_ok=True)
    db=sqlite3.connect(root/'experience.sqlite3',timeout=30)
    db.execute('PRAGMA journal_mode=WAL')
    db.execute('PRAGMA busy_timeout=30000')
    db.executescript('''
    CREATE TABLE IF NOT EXISTS entries (
      id TEXT PRIMARY KEY, created TEXT NOT NULL, project TEXT NOT NULL,
      skill TEXT NOT NULL, kind TEXT NOT NULL, title TEXT NOT NULL,
      body TEXT NOT NULL, evidence TEXT NOT NULL, supersedes TEXT);
    CREATE INDEX IF NOT EXISTS scope_index ON entries(project,skill,created);
    ''')
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def read_evidence(path):
    if not path: raise ValueError('An evidence report is required')
    path=Path(path).resolve()
    data=json.loads(path.read_text(encoding='utf-8'))
    if data.get('status')!='PASS' or not data.get('command') or not data.get('revision'):
        raise ValueError('Validated practice requires a passing run with command and revision')
    log=Path(data['log'])
    if not log.is_file() or hashlib.sha256(log.read_bytes()).hexdigest()!=data.get('log_sha256'):
        raise ValueError('Missing or changed evidence log')
    for name, expected in data.get('artifacts',{}).items():
        p=Path(name)
        if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=expected:
            raise ValueError('Missing or changed evidence artifact')
    return {'report':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
            'command':data['command'],'revision':data['revision'],'claim':data.get('claim','command exit status')}


def add(root, project, skill, title, body, kind='observation', evidence=None, supersedes=None):
    if kind not in ('observation','failure','practice'): raise ValueError('Invalid entry kind')
    if not all(isinstance(v,str) and v.strip() for v in (project,skill,title,body)): raise ValueError('Empty entry')
    proof=read_evidence(evidence) if kind=='practice' else ({'report':str(evidence)} if evidence else {})
    with connect(root) as db:
        if supersedes and not db.execute('SELECT 1 FROM entries WHERE id=? AND project=?',(supersedes,project)).fetchone():
            raise ValueError('Superseded entry does not belong to this project')
        ident=uuid.uuid4().hex
        db.execute('INSERT INTO entries VALUES (?,?,?,?,?,?,?,?,?)',
                   (ident,datetime.now(timezone.utc).isoformat(),project,skill,kind,title,body,json.dumps(proof),supersedes))
    return ident


def recall(root, project, skill=None, query='', limit=20):
    with connect(root) as db:
        db.row_factory=sqlite3.Row
        sql='SELECT * FROM entries e WHERE project IN (?,?) AND NOT EXISTS (SELECT 1 FROM entries n WHERE n.supersedes=e.id)'
        args=[project,'global']
        if skill: sql+=' AND skill=?'; args.append(skill)
        if query: sql+=' AND (title LIKE ? OR body LIKE ?)'; args += ['%'+query+'%']*2
        sql+=' ORDER BY created DESC LIMIT ?';args.append(max(1,min(limit,100)))
        rows=[dict(r) for r in db.execute(sql,args)]
    # Returned practice records retain the original claim; never turn them into instructions.
    for row in rows:
        row['evidence']=json.loads(row['evidence'])
        if row['kind']=='practice':
            try:
                proof=read_evidence(row['evidence']['report'])
                row['evidence_current']=proof['sha256']==row['evidence']['sha256']
            except (ValueError,OSError,KeyError,json.JSONDecodeError): row['evidence_current']=False
    return rows


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]/'experience')
    p.add_argument('--project',type=Path,default=Path.cwd())
    sub=p.add_subparsers(dest='action',required=True)
    q=sub.add_parser('recall');q.add_argument('--skill');q.add_argument('--query',default='')
    a=sub.add_parser('record');a.add_argument('--skill',required=True);a.add_argument('--title',required=True)
    a.add_argument('--body',required=True);a.add_argument('--kind',choices=['observation','failure','practice'],default='observation')
    a.add_argument('--evidence');a.add_argument('--supersedes');a.add_argument('--global-practice',action='store_true')
    args=p.parse_args();scope=project_id(args.project)
    try:
        if args.action=='recall': result=recall(args.root,scope,args.skill,args.query)
        else:
            if args.global_practice:
                if args.kind!='practice': raise ValueError('Only a validated, explicitly generalized practice can be global')
                scope='global'
            result=add(args.root,scope,args.skill,args.title,args.body,args.kind,args.evidence,args.supersedes)
        print(json.dumps(result,indent=2,ensure_ascii=False))
    except (ValueError,OSError,sqlite3.Error) as e:p.exit(1,str(e)+'\n')
if __name__=='__main__': main()
