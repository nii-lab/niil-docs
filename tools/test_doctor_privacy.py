"""Read-only Git privacy checks with real isolated repositories and failure probes."""
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from doctor import policy_git_check

GIT = shutil.which('git')
POLICY = 'agent-policy.local.json'
CANARY = 'SYNTHETIC_POLICY_DO_NOT_LOG'


@unittest.skipUnless(GIT, 'Real Git fixtures require Git')
class PrivacyGitTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='niil privacy fixture ')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        (self.root / POLICY).write_text(CANARY)

    def git(self, *args):
        return subprocess.run([GIT, '-C', str(self.root), *args],
                              capture_output=True, text=True, check=True)

    def init(self):
        self.git('init', '--quiet')

    def state(self):
        result = policy_git_check(self.root)
        self.assertNotIn(CANARY, json.dumps(result))
        self.assertEqual((self.root / POLICY).read_text(), CANARY)
        return result[0]

    def test_real_ignore_and_untracked_is_ready(self):
        self.init()
        (self.root / '.gitignore').write_text(POLICY + '\n')
        before = self.git('ls-files', '--stage').stdout
        self.assertEqual(self.state(), 'ready')
        self.assertEqual(self.git('ls-files', '--stage').stdout, before)

    def test_comment_is_not_ignore(self):
        self.init()
        (self.root / '.gitignore').write_text('# ' + POLICY + '\n')
        self.assertEqual(self.state(), 'needs_setup')

    def test_negation_is_not_ignore(self):
        self.init()
        (self.root / '.gitignore').write_text('*.json\n!' + POLICY + '\n')
        self.assertEqual(self.state(), 'needs_setup')

    def test_tracked_policy_is_not_ready_even_with_ignore(self):
        self.init()
        (self.root / '.gitignore').write_text(POLICY + '\n')
        self.git('add', '--force', '--', POLICY)
        before = self.git('ls-files', '--stage').stdout
        self.assertEqual(self.state(), 'needs_setup')
        self.assertEqual(self.git('ls-files', '--stage').stdout, before)

    def test_nonrepository_is_unknown(self):
        (self.root / '.gitignore').write_text(POLICY + '\n')
        self.assertEqual(self.state(), 'unknown')


class PrivacyFailureTests(unittest.TestCase):
    def test_git_unavailable_is_unknown_without_subprocess(self):
        with patch('doctor.shutil.which', return_value=None), patch('doctor.subprocess.run') as run:
            self.assertEqual(policy_git_check('/unused/local/workspace')[0], 'unknown')
            run.assert_not_called()

    def test_timeout_is_unknown_and_does_not_log_command_or_output(self):
        with patch('doctor.shutil.which', return_value='/fixture/git'), patch(
                'doctor.subprocess.run', side_effect=subprocess.TimeoutExpired(
                    ['git'], 5, output=CANARY, stderr=CANARY)):
            result = policy_git_check('/unused/local/workspace')
        self.assertEqual(result[0], 'unknown')
        self.assertNotIn(CANARY, json.dumps(result))

    def test_commands_use_absolute_workspace_and_fixed_relative_policy(self):
        workspace = Path('/fixture/workspace with spaces')
        responses = [
            subprocess.CompletedProcess([], 0, 'true\n', ''),
            subprocess.CompletedProcess([], 1, '', CANARY),
            subprocess.CompletedProcess([], 0, '', ''),
        ]
        with patch('doctor.shutil.which', return_value='/fixture/git'), patch(
                'doctor.subprocess.run', side_effect=responses) as run:
            result = policy_git_check(workspace)
        self.assertEqual(result[0], 'ready')
        self.assertNotIn(CANARY, json.dumps(result))
        for call in run.call_args_list:
            args = call.args[0]
            self.assertEqual(args[:3], ['/fixture/git', '-C', str(workspace.resolve())])
            self.assertNotIn(CANARY, args)
            self.assertNotIn('shell', call.kwargs)
        self.assertEqual(run.call_args_list[1].args[0][-2:], ['--', POLICY])
        self.assertEqual(run.call_args_list[2].args[0][-2:], ['--', POLICY])

    def test_git_error_is_unknown_without_error_body(self):
        responses = [subprocess.CompletedProcess([], 0, 'true\n', ''),
                     subprocess.CompletedProcess([], 128, CANARY, CANARY)]
        with patch('doctor.shutil.which', return_value='/fixture/git'), patch(
                'doctor.subprocess.run', side_effect=responses):
            result = policy_git_check('/fixture/workspace')
        self.assertEqual(result[0], 'unknown')
        self.assertNotIn(CANARY, json.dumps(result))


if __name__ == '__main__':
    unittest.main(verbosity=2)
