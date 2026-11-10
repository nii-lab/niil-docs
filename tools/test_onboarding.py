import copy,json,tempfile,unittest
from pathlib import Path
from init_workspace import create
from doctor import diagnose
from policy_check import classify
from tutorial_check import check

class OnboardingTests(unittest.TestCase):
    def test_fresh_workspace_and_diagnostics(self):
        with tempfile.TemporaryDirectory() as tmp:
            target=create('member',Path(tmp)/'new','LOCAL-ONLY')
            self.assertIn('@AGENTS.md',(target/'CLAUDE.md').read_text())
            self.assertTrue((target/'SYSTEM-PROTOCOL.md').is_file())
            self.assertIn('agent-policy.local.json',(target/'.gitignore').read_text())
            report=diagnose(target);states={c['id']:c['status'] for c in report['checks']}
            self.assertEqual(states['contract'],'ready');self.assertEqual(states['delegation'],'needs_owner');self.assertEqual(states['github'],'unknown');self.assertEqual(states['runner'],'unknown')
            self.assertEqual(states['private_policy'],'unknown')
            (target/'agent-policy.local.json').write_text('[]')
            self.assertEqual(next(c for c in diagnose(target)['checks'] if c['id']=='delegation')['status'],'needs_owner')
            with self.assertRaises(ValueError):create('member',target,'other')
    def test_personal_policy_changes_decision_without_starting_execution(self):
        task={'protocol_version':'1.0','task_id':'example','guide_revision':'v1','to_owner':'a','from_owner':'pi','repository':'lab/proj','requested_actions':['read_shared']}
        policy={'owner_id':'a','configured_by_owner':True,'mode':'manual','allowed_repositories':['lab/proj'],'allowed_senders':['pi'],'automatic_actions':['read_shared']}
        self.assertEqual(classify(task,policy,True)['decision'],'needs_owner')
        policy['mode']='allowlist';r=classify(task,policy,True);self.assertEqual(r['decision'],'eligible');self.assertFalse(r['execution_started'])
        self.assertEqual(classify(task,policy,False)['decision'],'needs_access')
        modified=copy.deepcopy(task);modified['requested_actions']=['publish_public']
        self.assertEqual(classify(modified,policy,True)['decision'],'needs_owner')
    def test_empty_missions_are_incomplete(self):
        with tempfile.TemporaryDirectory() as tmp:self.assertEqual(check(tmp)['status'],'incomplete')

if __name__=='__main__':unittest.main(verbosity=2)
