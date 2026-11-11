import base64
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
from install_hub_client import install,REPOSITORY

CODE='a'*40
REGISTRY='b'*40


class Install(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
        subprocess.run(['git','init',str(self.root)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        (self.root/'.gitignore').write_text('.local/\nagent-policy.local.json\n')
        (self.root/'workspace.json').write_text(json.dumps({'kind':'member','owner_id':'alice'}))
        (self.root/'notes').mkdir();(self.root/'notes/private.txt').write_text('PRIVATE-SOURCE-MUST-NOT-BE-READ')
        (self.root/'agent-policy.local.json').write_text('PRIVATE-POLICY-MUST-NOT-CHANGE')
        self.registry={'repository':REPOSITORY,'participants':{'alice':{'github_id':101,'projects':['p']}}}
        self.rev=REGISTRY;self.seen=[];self.mutations={}
    def gh(self,path):
        self.seen.append(path)
        if path in self.mutations:return self.mutations[path]
        if path=='user':return {'login':'alice','id':101}
        if path=='user/memberships/orgs/nii-lab':return {'state':'active'}
        if path==f'repos/{REPOSITORY}':return {'private':True,'permissions':{'pull':True}}
        if path==f'repos/{REPOSITORY}/commits/{CODE}':return {'sha':CODE}
        if path==f'repos/{REPOSITORY}/commits/main':return {'sha':self.rev}
        if '/contents/ops/live/participants.json?' in path:data=json.dumps(self.registry).encode()
        elif '/contents/services/github_hub/' in path:data=b'raise RuntimeError("Downloaded client must not execute during installation")\n'
        else:raise AssertionError(path)
        return {'encoding':'base64','content':base64.b64encode(data).decode(),
                'sha':hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()}
    def run_install(self):
        with patch('install_hub_client.gh',side_effect=self.gh):return install(self.root,CODE)
    def test_pinned_install_preserves_personal_files_and_executes_nothing(self):
        result=self.run_install();p=Path(result['client_directory'])
        self.assertTrue((p/'participant.py').is_file());self.assertFalse(result['client_executed']);self.assertFalse(result['policy_changed'])
        self.assertEqual((self.root/'agent-policy.local.json').read_text(),'PRIVATE-POLICY-MUST-NOT-CHANGE')
        self.assertEqual((self.root/'notes/private.txt').read_text(),'PRIVATE-SOURCE-MUST-NOT-BE-READ')
        self.assertFalse(any('/contents/notes/' in x for x in self.seen))
    def test_same_release_and_registry_are_idempotent(self):
        first=self.run_install();second=self.run_install();self.assertTrue(second['unchanged']);self.assertEqual(first['client_directory'],second['client_directory'])
    def test_registry_refresh_preserves_previous_client(self):
        first=self.run_install();self.rev='c'*40;second=self.run_install()
        self.assertNotEqual(first['client_directory'],second['client_directory']);self.assertTrue(Path(first['client_directory']).exists())
    def test_modified_client_is_not_overwritten(self):
        first=self.run_install();p=Path(first['client_directory'])/'participant.py';p.write_text('local edits')
        with self.assertRaisesRegex(ValueError,'existing client differs'):self.run_install()
        self.assertEqual(p.read_text(),'local edits')
    def test_account_mismatch_writes_no_client(self):
        self.mutations['user']={'login':'bob','id':102}
        with self.assertRaisesRegex(ValueError,'workspace owner'):self.run_install()
        self.assertFalse((self.root/'.local/niil-client').exists())
    def test_missing_membership_or_registration_cannot_be_silently_added(self):
        self.mutations['user/memberships/orgs/nii-lab']={'state':'pending'}
        with self.assertRaisesRegex(ValueError,'membership'):self.run_install()
        self.mutations.clear();self.registry['participants']={}
        with self.assertRaisesRegex(ValueError,'operator registration'):self.run_install()
        self.assertFalse((self.root/'.local/niil-client').exists())
    def test_private_repo_access_required(self):
        self.mutations[f'repos/{REPOSITORY}']={'private':True,'permissions':{'pull':False}}
        with self.assertRaisesRegex(ValueError,'read access'):self.run_install()
    def test_unignored_output_rejected(self):
        (self.root/'.gitignore').write_text('agent-policy.local.json\n')
        with self.assertRaisesRegex(ValueError,'Git-ignored'):self.run_install()
    def test_negated_code_path_cannot_pass_a_generic_ignore_probe(self):
        (self.root/'.gitignore').write_text('.local/*\n!.local/niil-client/\n.local/niil-client/*\n!.local/niil-client/*/\n.local/niil-client/*/*\n!.local/niil-client/*/participant.py\n')
        with self.assertRaisesRegex(ValueError,'every client output'):self.run_install()
        self.assertFalse((self.root/'.local/niil-client').exists())
    def test_already_tracked_pointer_is_not_marked_private(self):
        self.run_install()
        subprocess.run(['git','-C',str(self.root),'add','-f','.local/niil-client/current.json'],check=True)
        with self.assertRaisesRegex(ValueError,'every client output'):self.run_install()
    def test_bad_blob_hash_is_rejected_before_install(self):
        path=f'repos/{REPOSITORY}/contents/services/github_hub/hub.py?ref={CODE}'
        self.mutations[path]={'encoding':'base64','content':base64.b64encode(b'code').decode(),'sha':'0'*40}
        with self.assertRaisesRegex(ValueError,'checksum'):self.run_install()
    def test_moving_branch_is_not_a_release(self):
        with self.assertRaisesRegex(ValueError,'immutable'):install(self.root,'main')


if __name__=='__main__':unittest.main()
