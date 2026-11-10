import copy
import hashlib
import json
import multiprocessing
import os
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from init_workspace import create
import workspace_bundle as bundle


def record(identifier='asset-v1', owner='jun', visibility='lab', status='shared', project=None):
    return {'schema_version': 1, 'id': identifier, 'type': 'note', 'title': 'Synthetic interface note',
            'owner_id': owner, 'project_id': project, 'visibility': visibility, 'status': status,
            'updated_at': '2026-11-11T00:00:00+09:00', 'summary': 'Local test fixture only',
            'body': 'No robot or simulator was executed.',
            'source': {'uri': 'https://example.invalid/fixture', 'revision': 'fixture-v1'},
            'evidence': [], 'derived_from': []}


def import_in_process(workspace, incoming, results, ready=None, release=None):
    """A real independent process; pause the first writer while it holds its lock."""
    if ready is not None:
        original = bundle.atomic_write
        def paused(*args, **kwargs):
            ready.set()
            if not release.wait(10):
                raise RuntimeError('Test barrier timed out')
            return original(*args, **kwargs)
        bundle.atomic_write = paused
    try:
        result = bundle.import_records(workspace, incoming)
        results.put({'status': 'ok', 'added': result['added']})
    except bundle.BundleError as exc:
        results.put({'status': 'error', 'message': str(exc)})


class WorkspaceBundleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='niil bundle fixture ')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.workspace = create('member', self.root / 'jun', 'jun')
        self.library = self.workspace / 'imports' / 'records.json'

    def write_record(self, value, name=None):
        path = self.workspace / 'records' / (name or value['id'] + '.json')
        path.write_text(json.dumps(value, ensure_ascii=False))
        return path

    def incoming(self, records, name='incoming.json'):
        path = self.root / name
        path.write_text(json.dumps(bundle.envelope(records), ensure_ascii=False))
        return path

    def snapshot(self):
        return {str(p.relative_to(self.workspace)): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in self.workspace.rglob('*') if p.is_file()}

    def test_export_filters_private_draft_foreign_and_project_without_touching_originals(self):
        self.write_record(record())
        private = record('private', visibility='personal', status='draft')
        private['body'] = 'PRIVATE_CANARY_MUST_NOT_EXPORT'
        private['source'] = {'uri': '', 'revision': ''}
        self.write_record(private)
        self.write_record(record('draft-lab', status='draft'))
        self.write_record(record('foreign', owner='sol'))
        self.write_record(record('project', visibility='project', project='project-a'))
        before = self.snapshot()
        output = self.root / 'lab.json'
        self.assertEqual(bundle.export_records(self.workspace, output, 'lab')['exported'], 1)
        data = json.loads(output.read_text())
        self.assertEqual([r['id'] for r in data['records']], ['asset-v1'])
        self.assertNotIn('PRIVATE_CANARY', output.read_text())
        self.assertEqual(self.snapshot(), before)

    def test_project_selection_is_exact(self):
        self.write_record(record('a', visibility='project', project='project-a'))
        self.write_record(record('b', visibility='project', project='project-b'))
        output = self.root / 'project.json'
        bundle.export_records(self.workspace, output, 'project', 'project-a', ['a'])
        self.assertEqual(json.loads(output.read_text())['records'][0]['id'], 'a')
        with self.assertRaises(bundle.BundleError):
            bundle.export_records(self.workspace, self.root / 'bad.json', 'project')
        with self.assertRaises(bundle.BundleError):
            bundle.export_records(self.workspace, self.root / 'bad.json', 'project', 'project-a', ['b'])

    def test_selected_unshareable_missing_or_duplicate_id_fails_without_output(self):
        self.write_record(record('private', visibility='personal'))
        for ids in (['private'], ['missing'], ['private', 'private'], ['../outside']):
            with self.subTest(ids=ids), self.assertRaises(bundle.BundleError):
                bundle.export_records(self.workspace, self.root / 'blocked.json', 'lab', ids=ids)
            self.assertFalse((self.root / 'blocked.json').exists())

    def test_shared_export_requires_provenance_but_personal_draft_can_be_empty(self):
        draft = record('private', visibility='personal', status='draft')
        draft['source'] = {'uri': '', 'revision': ''}
        bundle.validate_record(draft)
        self.write_record(draft)
        for source in ({'uri': '', 'revision': 'v1'},
                       {'uri': 'https://example.invalid', 'revision': ''},
                       {'uri': 'file:///private/example', 'revision': 'v1'}):
            shared = record()
            shared['source'] = source
            self.write_record(shared)
            with self.subTest(source=source), self.assertRaises(bundle.BundleError):
                bundle.export_records(self.workspace, self.root / 'blocked.json', 'lab')

    def test_import_preserves_author_and_source_and_copies_do_not_auto_export(self):
        original = record(owner='ari')
        original['derived_from'] = [{'id': 'prior', 'source': 'source reference', 'revision': 'v0'}]
        before = self.snapshot()
        with patch('workspace_bundle.os.replace', wraps=bundle.os.replace) as replace:
            result = bundle.import_records(self.workspace, self.incoming([original]))
        self.assertEqual(replace.call_count, 1)
        self.assertEqual(result['added'], 1)
        self.assertEqual(json.loads(self.library.read_text())['records'], [original])
        for path, digest in before.items():
            self.assertEqual(hashlib.sha256((self.workspace / path).read_bytes()).hexdigest(), digest)
        self.assertEqual(list((self.workspace / 'records').glob('*.json')), [])
        exported = self.root / 'no-automatic-share.json'
        bundle.export_records(self.workspace, exported, 'lab')
        self.assertEqual(json.loads(exported.read_text())['records'], [])

    def test_duplicate_is_skipped_with_no_library_rewrite(self):
        item = record()
        path = self.incoming([item])
        bundle.import_records(self.workspace, path)
        before = self.library.read_bytes()
        reordered = dict(reversed(list(item.items())))
        with patch('workspace_bundle.os.replace', wraps=bundle.os.replace) as replace:
            result = bundle.import_records(self.workspace, self.incoming([reordered]))
        self.assertEqual((result['added'], result['skipped']), (0, 1))
        replace.assert_not_called()
        self.assertEqual(self.library.read_bytes(), before)

    def test_conflict_rejects_the_entire_bundle(self):
        item = record()
        bundle.import_records(self.workspace, self.incoming([item]))
        before = self.library.read_bytes()
        changed = copy.deepcopy(item)
        changed['body'] = 'Different content'
        with patch('workspace_bundle.os.replace', wraps=bundle.os.replace) as replace:
            with self.assertRaises(bundle.BundleError):
                bundle.import_records(self.workspace, self.incoming([record('new'), changed]))
        replace.assert_not_called()
        self.assertEqual(self.library.read_bytes(), before)

    def test_duplicate_incoming_ids_and_malformed_records_are_rejected(self):
        for records in ([record(), record()], [dict(record(), schema_version=True)],
                        [dict(record(), updated_at='2026-11-11T00:00:00')],
                        [dict(record(), body=[])], [dict(record(), evidence=[{}])]):
            with self.subTest(records=records), self.assertRaises(bundle.BundleError):
                bundle.import_records(self.workspace, self.incoming(records))
        self.assertFalse(self.library.exists())

    def test_export_rejects_symlinked_record_and_output_parent(self):
        outside = self.incoming([record()], 'outside.json')
        (self.workspace / 'records' / 'linked.json').symlink_to(outside)
        with self.assertRaises(bundle.BundleError):
            bundle.export_records(self.workspace, self.root / 'out.json', 'lab')
        (self.workspace / 'records' / 'linked.json').unlink()
        (self.root / 'linked-dir').symlink_to(self.root, target_is_directory=True)
        with self.assertRaises(bundle.BundleError):
            bundle.export_records(self.workspace, self.root / 'linked-dir/out.json', 'lab')

    def test_import_rejects_symlinked_bundle_workspace_and_library(self):
        incoming = self.incoming([record()])
        linked = self.root / 'linked.json'
        linked.symlink_to(incoming)
        with self.assertRaises(bundle.BundleError):
            bundle.import_records(self.workspace, linked)
        workspace_link = self.root / 'linked-workspace'
        workspace_link.symlink_to(self.workspace, target_is_directory=True)
        with self.assertRaises(bundle.BundleError):
            bundle.import_records(workspace_link, incoming)
        self.library.parent.mkdir(exist_ok=True)
        self.library.symlink_to(incoming)
        before = incoming.read_bytes()
        with self.assertRaises(bundle.BundleError):
            bundle.import_records(self.workspace, incoming)
        self.assertEqual(incoming.read_bytes(), before)

    def test_path_traversal_and_existing_export_are_rejected(self):
        source = self.write_record(record())
        before = source.read_bytes()
        with self.assertRaises(bundle.BundleError):
            bundle.export_records(self.workspace, source, 'lab')
        with self.assertRaises(bundle.BundleError):
            bundle.export_records(self.workspace, self.root / 'nested/../out.json', 'lab')
        with self.assertRaises(bundle.BundleError):
            bundle.import_records(self.workspace / '..' / 'jun', self.incoming([record()]))
        self.assertEqual(source.read_bytes(), before)

    def test_size_and_count_limits_preserve_existing_library(self):
        bundle.import_records(self.workspace, self.incoming([record()]))
        before = self.library.read_bytes()
        oversized = self.root / 'large.json'
        oversized.write_bytes(b' ' * (bundle.MAX_BYTES + 1))
        with self.assertRaises(bundle.BundleError):
            bundle.import_records(self.workspace, oversized)
        with self.assertRaises(bundle.BundleError):
            bundle.import_records(self.workspace, self.incoming([record(str(i)) for i in range(101)]))
        self.assertEqual(self.library.read_bytes(), before)

    def test_failed_replace_preserves_existing_library_and_cleans_temporary(self):
        bundle.import_records(self.workspace, self.incoming([record()]))
        before = self.library.read_bytes()
        with patch('workspace_bundle.os.replace', side_effect=OSError('synthetic write failure')):
            with self.assertRaises(OSError):
                bundle.import_records(self.workspace, self.incoming([record('new')]))
        self.assertEqual(self.library.read_bytes(), before)
        self.assertEqual(list(self.library.parent.glob('.niil-bundle-*')), [])
        self.assertFalse((self.library.parent / '.bundle-import.lock').exists())

    def test_simultaneous_process_import_is_busy_then_retry_preserves_both_records(self):
        context = multiprocessing.get_context('spawn')
        results = context.Queue()
        ready, release = context.Event(), context.Event()
        first = context.Process(target=import_in_process, args=(str(self.workspace),
            str(self.incoming([record('first')], 'first.json')), results, ready, release))
        second = context.Process(target=import_in_process, args=(str(self.workspace),
            str(self.incoming([record('second')], 'second.json')), results))
        processes = [first, second]
        try:
            first.start()
            self.assertTrue(ready.wait(5), 'First process did not reach the controlled write barrier')
            lock = self.library.parent / '.bundle-import.lock'
            self.assertTrue(lock.is_file())
            if os.name != 'nt':
                self.assertEqual(stat.S_IMODE(lock.stat().st_mode), 0o600)
            second.start()
            second.join(5)
            self.assertEqual(second.exitcode, 0)
            self.assertEqual(results.get(timeout=2), {'status': 'error', 'message': bundle.BUSY_MESSAGE})
            release.set()
            first.join(5)
            self.assertEqual(first.exitcode, 0)
            self.assertEqual(results.get(timeout=2), {'status': 'ok', 'added': 1})
            self.assertFalse(lock.exists())
            retry = context.Process(target=import_in_process, args=(str(self.workspace),
                str(self.root / 'second.json'), results))
            processes.append(retry)
            retry.start()
            retry.join(5)
            self.assertEqual(retry.exitcode, 0)
            self.assertEqual(results.get(timeout=2), {'status': 'ok', 'added': 1})
            self.assertEqual({r['id'] for r in json.loads(self.library.read_text())['records']},
                             {'first', 'second'})
            self.assertFalse(lock.exists())
        finally:
            release.set()
            for process in processes:
                if process.pid is not None:
                    process.join(2)
                    if process.is_alive():
                        process.terminate()
                        process.join(2)
            results.close()
            results.join_thread()

    def test_preexisting_lock_is_busy_and_is_not_removed(self):
        self.library.parent.mkdir()
        lock = self.library.parent / '.bundle-import.lock'
        lock.write_text('Unknown owner; do not automatically remove')
        before = lock.read_bytes()
        with self.assertRaises(bundle.BundleError) as caught:
            bundle.import_records(self.workspace, self.incoming([record()]))
        self.assertEqual(str(caught.exception), bundle.BUSY_MESSAGE)
        self.assertEqual(lock.read_bytes(), before)
        self.assertFalse(self.library.exists())

    def test_validation_failure_cleans_own_lock(self):
        with self.assertRaises(bundle.BundleError):
            bundle.import_records(self.workspace, self.incoming([record(), record()]))
        self.assertFalse((self.library.parent / '.bundle-import.lock').exists())
        self.assertFalse(self.library.exists())

    def test_lock_release_does_not_unlink_a_replaced_lock(self):
        lock = self.library.parent / '.bundle-import.lock'
        with bundle.import_lock(self.workspace):
            lock.unlink()
            lock.write_text('Synthetic replacement with a different inode')
        self.assertTrue(lock.exists())
        self.assertEqual(lock.read_text(), 'Synthetic replacement with a different inode')

    def test_combined_library_count_and_export_size_are_bounded(self):
        bundle.import_records(self.workspace, self.incoming([record(str(i)) for i in range(100)]))
        before = self.library.read_bytes()
        with self.assertRaises(bundle.BundleError):
            bundle.import_records(self.workspace, self.incoming([record('overflow')]))
        self.assertEqual(self.library.read_bytes(), before)
        for i in range(23):
            item = record(str(i))
            item['body'] = 'x' * 100000
            self.write_record(item)
        output = self.root / 'too-large-export.json'
        with self.assertRaises(bundle.BundleError):
            bundle.export_records(self.workspace, output, 'lab')
        self.assertFalse(output.exists())

    def test_json_boolean_and_number_metadata_are_not_silently_deduplicated(self):
        item = record()
        item['extra_metadata'] = True
        bundle.import_records(self.workspace, self.incoming([item]))
        changed = copy.deepcopy(item)
        changed['extra_metadata'] = 1
        before = self.library.read_bytes()
        with self.assertRaises(bundle.BundleError):
            bundle.import_records(self.workspace, self.incoming([changed]))
        self.assertEqual(self.library.read_bytes(), before)

    def test_json_duplicate_fields_nonfinite_and_code_text(self):
        invalid = self.root / 'invalid.json'
        for raw in ('{"schema_version":1,"schema_version":1}', '{"x":NaN}'):
            invalid.write_text(raw)
            with self.assertRaises(bundle.BundleError):
                bundle.import_records(self.workspace, invalid)
        item = record()
        marker = self.root / 'MUST_NOT_EXECUTE'
        item['body'] = '__import__("pathlib").Path(' + repr(str(marker)) + ').touch()'
        with patch('urllib.request.urlopen', side_effect=AssertionError('URL fetch forbidden')):
            bundle.import_records(self.workspace, self.incoming([item]))
        self.assertFalse(marker.exists())
        invalid_text = record('invalid-unicode')
        invalid_text['body'] = '\ud800'
        invalid_path = self.root / 'invalid-unicode.json'
        invalid_path.write_text(json.dumps(bundle.envelope([invalid_text]), ensure_ascii=True))
        before = self.library.read_bytes()
        with self.assertRaises(bundle.BundleError):
            bundle.import_records(self.workspace, invalid_path)
        self.assertEqual(self.library.read_bytes(), before)

    def test_cli_roundtrip_and_unshareable_error_do_not_log_private_body(self):
        self.write_record(record())
        tool = str(Path(bundle.__file__).resolve())
        output = self.root / 'cli-export.json'
        export = subprocess.run([sys.executable, tool, 'export', '--workspace', str(self.workspace),
                                 '--output', str(output), '--audience', 'lab'], capture_output=True, text=True)
        self.assertEqual(export.returncode, 0, export.stderr)
        self.assertEqual(json.loads(export.stdout)['exported'], 1)
        imported = subprocess.run([sys.executable, tool, 'import', '--workspace', str(self.workspace),
                                   '--bundle', str(output)], capture_output=True, text=True)
        self.assertEqual(imported.returncode, 0, imported.stderr)
        self.assertEqual(json.loads(imported.stdout)['added'], 1)
        private = record('private', visibility='personal', status='draft')
        private['body'] = 'PRIVATE_CLI_CANARY'
        self.write_record(private)
        denied = subprocess.run([sys.executable, tool, 'export', '--workspace', str(self.workspace),
                                 '--output', str(self.root / 'denied.json'), '--audience', 'lab',
                                 '--ids', 'private'], capture_output=True, text=True)
        self.assertEqual(denied.returncode, 1)
        self.assertIn('공유 범위', denied.stderr)
        self.assertNotIn('PRIVATE_CLI_CANARY', denied.stdout + denied.stderr)


if __name__ == '__main__':
    unittest.main(verbosity=2)
