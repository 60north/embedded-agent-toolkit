import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from doctor import installer,inspect
import experience
import check
from update_superpowers import merge,update

class ToolkitTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.base=Path(self.temp.name).resolve();self.home=self.base/'home with spaces';self.home.mkdir()
        self.project=self.base/'project';self.project.mkdir()
        self.root=self.base/'toolkit';self.root.mkdir()
        shutil.copytree(ROOT/'skills',self.root/'skills')
        shutil.copytree(ROOT/'policies',self.root/'policies')
        self.env=patch.dict(os.environ,{'CLAUDE_CONFIG_DIR':str(self.home/'.claude'),'CODEX_HOME':str(self.home/'.codex')})
        self.env.start();self.addCleanup(self.env.stop)

    def install(self,**kw):return installer.install(self.home,root=self.root,**kw)

    def test_one_directory_live_changes_both_clients(self):
        self.install()
        a=self.home/'.claude/skills';b=self.home/'.agents/skills'
        self.assertTrue(os.path.samefile(a,b));self.assertTrue(os.path.samefile(a,self.root/'skills'))
        f=Path('engineering-python/SKILL.md');(self.root/'skills'/f).write_text('changed live')
        self.assertEqual((a/f).read_text(),'changed live');self.assertEqual((b/f).read_text(),'changed live')
        fresh=self.root/'skills/new-skill';fresh.mkdir();(fresh/'SKILL.md').write_text('new')
        self.assertTrue((a/'new-skill/SKILL.md').is_file());self.assertTrue((b/'new-skill/SKILL.md').is_file())

    def test_idempotent_and_preserves_configuration(self):
        p=self.home/'.claude/CLAUDE.md';p.parent.mkdir();p.write_text('My rules\n')
        settings=p.parent/'settings.json';settings.write_text('{"model":"custom"}')
        self.install();before=p.read_bytes();again=self.install()
        self.assertEqual(again['links'],[]);self.assertEqual(again['writes'],[])
        self.assertEqual(p.read_bytes(),before);self.assertTrue(before.startswith(b'My rules'))
        self.assertEqual(json.loads(settings.read_text())['model'],'custom')
        self.assertEqual(json.loads(settings.read_text())['permissions']['additionalDirectories'],[str(self.root/'experience')])

    def test_permission_configuration_preserves_existing_rules(self):
        from permissions import codex_memory
        import tomllib
        original='model = "keep"\n[sandbox_workspace_write]\nnetwork_access = false\nwritable_roots = ["/existing"] # keep\n[other]\nvalue = 1\n'
        updated=codex_memory(original,'/new memory')
        parsed=tomllib.loads(updated)
        self.assertEqual(parsed['sandbox_workspace_write']['writable_roots'],['/existing','/new memory'])
        self.assertFalse(parsed['sandbox_workspace_write']['network_access'])
        self.assertEqual(parsed['other']['value'],1)
        self.assertEqual(codex_memory(updated,'/new memory'),updated)
        with self.assertRaises(ValueError):codex_memory('[permissions.custom]\n','/memory')

    def test_dry_run_no_files(self):
        self.install(dry_run=True);self.assertEqual(list(self.home.iterdir()),[])

    def test_conflict_and_migration(self):
        p=self.home/'.claude/skills';p.mkdir(parents=True);(p/'custom.txt').write_text('keep')
        with self.assertRaises(ValueError):self.install()
        self.assertFalse((self.home/'.agents').exists())
        actions=self.install(migrate=True)
        backup=Path(actions['backups'][str(p)])
        self.assertEqual((backup/'custom.txt').read_text(),'keep')
        self.assertTrue(os.path.samefile(p,self.root/'skills'))

    def test_legacy_policy_archived(self):
        p=self.home/'.claude/CLAUDE.md';p.parent.mkdir();p.write_text('TypeScript strict mode always\nTDD non-negotiable')
        with self.assertRaises(ValueError):self.install()
        result=self.install(migrate=True)
        self.assertIn(str(p),result['backups']);self.assertNotIn('TypeScript strict',p.read_text())

    def test_malformed_instruction_no_mutations(self):
        p=self.home/'.claude/CLAUDE.md';p.parent.mkdir();p.write_text(installer.BEGIN)
        with self.assertRaises(ValueError):self.install()
        self.assertFalse((self.home/'.agents').exists())

    def test_rollback_links_and_backup(self):
        original=self.home/'.claude/skills';original.mkdir(parents=True);(original/'old').write_text('old')
        real=installer.directory_link;count=0
        def fail(path,target):
            nonlocal count
            count+=1
            if count==2:raise OSError('link failure')
            real(path,target)
        with patch.object(installer,'directory_link',fail):
            with self.assertRaises(OSError):self.install(migrate=True)
        self.assertEqual((original/'old').read_text(),'old')
        self.assertFalse((self.home/'.agents/skills').exists())

    def test_project_scope_and_doctor(self):
        self.install(project=self.project)
        result=inspect(self.home,self.project)
        self.assertEqual(result['filesystem'],'PASS');self.assertEqual(result['live_clients'],'NOT RUN')
        self.assertTrue((self.project/'AGENTS.md').exists())
        self.assertFalse((self.home/'.claude').exists())

    def test_concurrent_memory_and_scope(self):
        root=self.base/'memory'
        # Initialize once; then multiple independent connections write concurrently.
        experience.add(root,'p','python','initial','start')
        with ThreadPoolExecutor(max_workers=8) as pool:
            ids=list(pool.map(lambda n:experience.add(root,'p','python',str(n),'lesson'),range(40)))
        self.assertEqual(len(set(ids)),40)
        self.assertEqual(len(experience.recall(root,'p',limit=100)),41)
        self.assertEqual(experience.recall(root,'other'),[])

    def test_observation_promotion_integrity_and_supersession(self):
        root=self.base/'memory'
        obs=experience.add(root,'p','python','hypothesis','not yet verified')
        with self.assertRaises(ValueError):experience.add(root,'p','python','claim','detail',kind='practice')
        data,report=check.run([sys.executable,'-c','print("ok")'],self.project,root,'python','command exits zero')
        self.assertEqual(data['status'],'PASS')
        practice=experience.add(root,'p','python','narrow practice','command exits zero',kind='practice',evidence=report,supersedes=obs)
        rows=experience.recall(root,'p');self.assertEqual(rows[0]['id'],practice);self.assertTrue(rows[0]['evidence_current'])
        Path(data['log']).write_text('tampered')
        self.assertFalse(experience.recall(root,'p')[0]['evidence_current'])

    def test_missing_failing_and_timeout_checks_recorded(self):
        root=self.base/'memory'
        for cmd,status,timeout in [(['surely-missing-engineering-tool'],'BLOCKED',10),
                ([sys.executable,'-c','raise SystemExit(3)'],'FAIL',10),
                ([sys.executable,'-c','import time; time.sleep(3)'],'FAIL',0.05)]:
            result,_=check.run(cmd,self.project,root,'test','test claim',timeout)
            self.assertEqual(result['status'],status)
        scope=experience.project_id(self.project)
        # Runs are evidence, not lessons: they never crowd recall.
        self.assertEqual(experience.recall(root,scope),[])
        self.assertEqual(experience.curation_status(root,scope)['pending_runs'],3)

    def test_shared_lessons_visible_across_projects(self):
        root=self.base/'memory'
        experience.add(root,experience.SHARED,'engineering-kicad-pcb','kicad-cli flag','DRC flag missing in this version',kind='failure')
        experience.add(root,'a','engineering-kicad-pcb','private','project fact')
        rows=experience.recall(root,'b')
        self.assertEqual([r['title'] for r in rows],['kicad-cli flag']);self.assertTrue(rows[0]['shared'])

    def test_curation_review_finish_and_prune(self):
        root=self.base/'memory';scope=experience.project_id(self.project)
        ok=[sys.executable,'-c','pass'];bad=[sys.executable,'-c','raise SystemExit(1)']
        reports={}
        for claim,cmd in [('fixed',bad),('fixed',ok),('repeated',bad),('repeated',bad),('green',ok)]:
            data,reports[claim]=check.run(cmd,self.project,root,'test',claim)
        experience.add(root,scope,'test','practice','cites the passing run',kind='practice',evidence=reports['fixed'])
        later=experience.now_utc()+timedelta(days=8)
        self.assertTrue(experience.curation_status(root,scope,now=later)['due'])
        self.assertFalse(experience.curation_status(root,scope)['due'])
        summary=experience.review(root,scope)
        self.assertEqual({c['claim']:c['signal'] for c in summary['candidates']},{'fixed':'fixed','repeated':'repeated'})
        self.assertEqual(summary['claims_only_passed'],1);self.assertEqual(summary['broken_practices'],[])
        check.run(ok,self.project,root,'test','after review')
        result=experience.finish(root,scope,summary['until'],now=experience.now_utc()+timedelta(days=40))
        self.assertEqual(result,{'reviewed':5,'pruned':4})
        self.assertTrue(reports['fixed'].is_file())
        self.assertFalse(reports['green'].exists());self.assertFalse(reports['green'].parent.exists())
        self.assertEqual(experience.curation_status(root,scope)['pending_runs'],1)
        self.assertEqual(experience.finish(root,scope,None),{'reviewed':0,'pruned':0})

    def test_robot_empty_skip_and_success(self):
        p=self.base/'output.xml'
        for text,ok in [('<robot/>',False),('<robot><suite><test><status status="SKIP"/></test></suite></robot>',False),
                        ('<robot><suite><test><status status="PASS"/></test></suite></robot>',True)]:
            p.write_text(text)
            if ok:check.validate_robot(p)
            else:
                with self.assertRaises(ValueError):check.validate_robot(p)

    def test_missing_artifact_fails(self):
        data,_=check.run([sys.executable,'-c','print(1)'],self.project,self.base/'memory','test','artifact',artifacts=[self.base/'missing'])
        self.assertEqual(data['status'],'FAIL')

    def test_three_way_update_preserves_local_changes(self):
        self.assertEqual(merge(b'a\nlocal\n',b'a\nb\n',b'a\nb\n'),b'a\nlocal\n')
        self.assertEqual(merge(b'a\nb\n',b'a\nb\n',b'upstream\nb\n'),b'upstream\nb\n')
        with self.assertRaises(ValueError):merge(b'ours\n',b'base\n',b'theirs\n')

    def test_skill_inventory_and_condensed_delegation(self):
        names={p.parent.name for p in (ROOT/'skills').glob('*/SKILL.md')}
        self.assertTrue({'engineering-stm32','engineering-freertos','engineering-hardware-review','using-superpowers','delegating-work'} <= names)
        self.assertFalse({'subagent-driven-development','dispatching-parallel-agents','typescript-strict','tdd'} & names)
        for p in (ROOT/'skills').glob('*/SKILL.md'):
            text=p.read_text();self.assertTrue(text.startswith('---\nname: '+p.parent.name+'\n'))
            self.assertIn('\ndescription:',text);self.assertNotIn('superpowers:',text)

if __name__=='__main__':unittest.main()
