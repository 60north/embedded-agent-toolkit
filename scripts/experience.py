#!/usr/bin/env python3
"""Local shared experience ledger. SQLite WAL supports independent client writers."""
import argparse
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import sqlite3
import subprocess
import uuid

# Weekly safety net: unreviewed runs older than this make recall report curation as due.
CURATE_AFTER=timedelta(days=7)
KEEP_DAYS=30
SHARED='global'


def now_utc():return datetime.now(timezone.utc)


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
    CREATE TABLE IF NOT EXISTS runs (
      id TEXT PRIMARY KEY, created TEXT NOT NULL, project TEXT NOT NULL,
      skill TEXT NOT NULL, claim TEXT NOT NULL, status TEXT NOT NULL,
      revision TEXT NOT NULL, command TEXT NOT NULL, report TEXT NOT NULL,
      reviewed INTEGER NOT NULL DEFAULT 0, pruned INTEGER NOT NULL DEFAULT 0);
    CREATE INDEX IF NOT EXISTS run_index ON runs(project,reviewed,created);
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
            raise ValueError('Superseded entry does not belong to this scope')
        ident=uuid.uuid4().hex
        db.execute('INSERT INTO entries VALUES (?,?,?,?,?,?,?,?,?)',
                   (ident,now_utc().isoformat(),project,skill,kind,title,body,json.dumps(proof),supersedes))
    return ident


def add_run(root, data, report):
    """Record one check execution. Runs are evidence, not lessons: recall never returns them."""
    ident=uuid.uuid4().hex
    with connect(root) as db:
        db.execute('INSERT INTO runs (id,created,project,skill,claim,status,revision,command,report) VALUES (?,?,?,?,?,?,?,?,?)',
                   (ident,data['created'],data['project'],data['skill'],data['claim'],data['status'],
                    data['revision'],json.dumps(data['command']),str(report)))
    return ident


def evidence_current(evidence):
    try:return read_evidence(evidence['report'])['sha256']==evidence['sha256']
    except (ValueError,OSError,KeyError,TypeError,json.JSONDecodeError):return False


def recall(root, project, skill=None, query='', limit=20):
    with connect(root) as db:
        db.row_factory=sqlite3.Row
        sql='SELECT * FROM entries e WHERE project IN (?,?) AND NOT EXISTS (SELECT 1 FROM entries n WHERE n.supersedes=e.id)'
        args=[project,SHARED]
        if skill: sql+=' AND skill=?'; args.append(skill)
        if query: sql+=' AND (title LIKE ? OR body LIKE ?)'; args += ['%'+query+'%']*2
        sql+=' ORDER BY created DESC LIMIT ?';args.append(max(1,min(limit,100)))
        rows=[dict(r) for r in db.execute(sql,args)]
    # Returned practice records retain the original claim; never turn them into instructions.
    for row in rows:
        row['evidence']=json.loads(row['evidence'])
        row['shared']=row['project']==SHARED
        if row['kind']=='practice':row['evidence_current']=evidence_current(row['evidence'])
    return rows


def curation_status(root, project, now=None):
    now=now or now_utc()
    with connect(root) as db:
        pending,oldest=db.execute('SELECT COUNT(*),MIN(created) FROM runs WHERE project=? AND reviewed=0',(project,)).fetchone()
    due=bool(pending) and now-datetime.fromisoformat(oldest)>=CURATE_AFTER
    return {'pending_runs':pending,'oldest_pending':oldest,'due':due}


def review(root, project):
    """Summarize unreviewed runs into lesson candidates. Reads no logs; the agent judges."""
    with connect(root) as db:
        db.row_factory=sqlite3.Row
        runs=[dict(r) for r in db.execute('SELECT * FROM runs WHERE project=? AND reviewed=0 ORDER BY created',(project,))]
        practices=[dict(r) for r in db.execute(
            "SELECT id,title,evidence FROM entries e WHERE kind='practice' AND project IN (?,?) "
            'AND NOT EXISTS (SELECT 1 FROM entries n WHERE n.supersedes=e.id)',(project,SHARED))]
    groups={}
    for run in runs:groups.setdefault((run['skill'],run['claim']),[]).append(run)
    candidates=[];passed=0
    for (skill,claim),items in groups.items():
        bad=[r for r in items if r['status']!='PASS']
        if not bad:passed+=1;continue
        # fixed: failed, then passed (a fix happened); repeated: failing more than once.
        signal='fixed' if items[-1]['status']=='PASS' else 'repeated' if len(bad)>1 else 'failed'
        candidates.append({'signal':signal,'skill':skill,'claim':claim,'runs':len(items),'failures':len(bad),
                           'statuses':[r['status'] for r in items][-10:],'last_failure_report':bad[-1]['report'],
                           'last_report':items[-1]['report']})
    broken=[{'id':p['id'],'title':p['title']} for p in practices if not evidence_current(json.loads(p['evidence']))]
    return {'pending_runs':len(runs),'until':runs[-1]['created'] if runs else None,
            'claims_only_passed':passed,'candidates':candidates,'broken_practices':broken}


def finish(root, project, until, keep_days=KEEP_DAYS, now=None):
    """Mark runs up to `until` reviewed, then delete old reviewed run folders not cited by a practice."""
    now=now or now_utc();root=Path(root).resolve();runs_dir=root/'runs'
    cutoff=(now-timedelta(days=keep_days)).isoformat()
    with connect(root) as db:
        reviewed=db.execute('UPDATE runs SET reviewed=1 WHERE project=? AND reviewed=0 AND created<=?',(project,until)).rowcount if until else 0
        cited={json.loads(e)['report'] for (e,) in db.execute("SELECT evidence FROM entries WHERE kind='practice'")}
        old=db.execute('SELECT id,report FROM runs WHERE project=? AND reviewed=1 AND pruned=0 AND created<?',(project,cutoff)).fetchall()
        pruned=0
        for ident,report in old:
            if report in cited:continue
            folder=Path(report).resolve().parent
            # Delete only a run folder that this ledger created, never anything outside runs/.
            if folder.parent==runs_dir and folder.is_dir():shutil.rmtree(folder)
            db.execute('UPDATE runs SET pruned=1 WHERE id=?',(ident,));pruned+=1
    return {'reviewed':reviewed,'pruned':pruned}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]/'experience')
    p.add_argument('--project',type=Path,default=Path.cwd())
    sub=p.add_subparsers(dest='action',required=True)
    q=sub.add_parser('recall');q.add_argument('--skill');q.add_argument('--query',default='')
    a=sub.add_parser('record');a.add_argument('--skill',required=True);a.add_argument('--title',required=True)
    a.add_argument('--body',required=True);a.add_argument('--kind',choices=['observation','failure','practice'],default='observation')
    a.add_argument('--evidence');a.add_argument('--supersedes')
    a.add_argument('--shared','--global-practice',dest='shared',action='store_true',
                   help='visible in every project; tool/technique lessons only, no project facts')
    c=sub.add_parser('curate',help='review unreviewed runs; with --done mark reviewed and prune old logs')
    c.add_argument('--done',action='store_true');c.add_argument('--until',help='the "until" value printed by the review; omit to only prune')
    c.add_argument('--keep-days',type=int,default=KEEP_DAYS)
    args=p.parse_args();scope=project_id(args.project)
    try:
        if args.action=='recall':
            result={'entries':recall(args.root,scope,args.skill,args.query),'curation':curation_status(args.root,scope)}
        elif args.action=='curate':
            result=finish(args.root,scope,args.until,args.keep_days) if args.done else review(args.root,scope)
        else:
            result=add(args.root,SHARED if args.shared else scope,args.skill,args.title,args.body,args.kind,args.evidence,args.supersedes)
        print(json.dumps(result,indent=2,ensure_ascii=False))
    except (ValueError,OSError,sqlite3.Error) as e:p.exit(1,str(e)+'\n')
if __name__=='__main__': main()
