"""Local record export/copy import. Never authenticates, fetches URLs or runs record text."""
import argparse
from contextlib import contextmanager
import datetime
import json
import os
import re
import tempfile
from pathlib import Path
from urllib.parse import urlsplit

MAX_BYTES = 2 * 1024 * 1024
MAX_RECORDS = 100
BUSY_MESSAGE = '다른 import가 사본 라이브러리를 사용 중입니다. 진행 작업을 확인하고 완료 후 재시도하세요. 잠금 파일을 자동 삭제하지 않습니다.'


class BundleError(ValueError):
    pass


def safe_path(value):
    path = Path(value).expanduser()
    if '..' in path.parts:
        raise BundleError('상위 경로 이동은 허용하지 않습니다.')
    path = path.absolute()
    if any(part.is_symlink() for part in [path, *path.parents]):
        raise BundleError('Symlink 경로는 허용하지 않습니다.')
    return path


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise BundleError('JSON에 중복 필드가 있습니다.')
        result[key] = value
    return result


def invalid_constant(_value):
    raise BundleError('JSON의 비정상 수치는 허용하지 않습니다.')


def read_json(path):
    path = safe_path(path)
    if not path.is_file() or path.stat().st_size > MAX_BYTES:
        raise BundleError('일반 JSON 파일과 2MiB 이하 크기가 필요합니다.')
    with path.open('rb') as stream:
        payload = stream.read(MAX_BYTES + 1)
    if len(payload) > MAX_BYTES:
        raise BundleError('JSON 파일은 2MiB 이하여야 합니다.')
    try:
        return json.loads(payload.decode('utf-8-sig'), object_pairs_hook=unique_object,
                          parse_constant=invalid_constant)
    except (UnicodeError, json.JSONDecodeError, RecursionError):
        raise BundleError('JSON 형식을 확인하세요.') from None


def valid_time(value):
    if not isinstance(value, str) or not re.search(r'(Z|[+-]\d{2}:\d{2})$', value):
        raise BundleError('Timezone을 포함한 시각이 필요합니다.')
    try:
        parsed = datetime.datetime.fromisoformat(value.replace('Z', '+00:00'))
        if parsed.utcoffset() is None:
            raise ValueError
    except ValueError:
        raise BundleError('시각 형식을 확인하세요.') from None


def valid_uri(value, required=False):
    if not isinstance(value, str):
        raise BundleError('출처 URL은 문자열이어야 합니다.')
    if not value and not required:
        return
    try:
        parsed = urlsplit(value)
        allowed = parsed.scheme in ('http', 'https') and bool(parsed.netloc)
    except ValueError:
        allowed = False
    if not allowed or any(c.isspace() or ord(c) < 32 for c in value):
        raise BundleError('출처는 유효한 HTTP(S) URL이어야 합니다.')


def validate_record(record, shared_export=False):
    if not isinstance(record, dict) or type(record.get('schema_version')) is not int or record['schema_version'] != 1:
        raise BundleError('schema_version=1 기록이 필요합니다.')
    for key in ('id', 'title', 'owner_id', 'updated_at', 'summary', 'body'):
        if not isinstance(record.get(key), str):
            raise BundleError('기록의 필수 문자열 필드를 확인하세요.')
    if not 1 <= len(record['id']) <= 120 or not 1 <= len(record['title']) <= 240 or len(record['body']) > 100000:
        raise BundleError('기록 ID·제목·본문 길이를 확인하세요.')
    if (record.get('type') not in ('note', 'experiment', 'decision', 'meeting', 'asset', 'wiki') or
            record.get('visibility') not in ('personal', 'project', 'lab') or
            record.get('status') not in ('draft', 'shared', 'accepted')):
        raise BundleError('기록 종류·공유 범위·상태를 확인하세요.')
    if 'project_id' not in record or (record['project_id'] is not None and not isinstance(record['project_id'], str)):
        raise BundleError('project_id를 확인하세요.')
    valid_time(record['updated_at'])
    source = record.get('source')
    if not isinstance(source, dict) or not isinstance(source.get('revision'), str):
        raise BundleError('출처와 revision이 필요합니다.')
    valid_uri(source.get('uri'), required=shared_export)
    if shared_export and not source['revision'].strip():
        raise BundleError('공유 내보내기에는 원본 revision이 필요합니다.')
    if 'example' in source and not isinstance(source['example'], bool):
        raise BundleError('출처 example 필드 형식을 확인하세요.')
    for key, fields in [('evidence', ('label', 'uri')), ('derived_from', ('id', 'source', 'revision'))]:
        if not isinstance(record.get(key), list):
            raise BundleError('근거·파생 출처 목록이 필요합니다.')
        for item in record[key]:
            if not isinstance(item, dict) or not all(isinstance(item.get(field), str) for field in fields):
                raise BundleError('근거·파생 출처 항목을 확인하세요.')
            if key == 'evidence':
                valid_uri(item['uri'])
    return record


def workspace_owner(workspace):
    root = safe_path(workspace)
    if not root.is_dir():
        raise BundleError('기존 개인 작업 공간이 필요합니다.')
    metadata = read_json(root / 'workspace.json')
    if (not isinstance(metadata, dict) or type(metadata.get('schema_version')) is not int or
            metadata['schema_version'] != 1 or not isinstance(metadata.get('owner_id'), str) or
            not metadata['owner_id'].strip()):
        raise BundleError('init_workspace가 만든 workspace.json의 owner_id를 확인하세요.')
    return root, metadata['owner_id']


def validate_bundle(bundle):
    if (not isinstance(bundle, dict) or type(bundle.get('schema_version')) is not int or
            bundle['schema_version'] != 1 or not isinstance(bundle.get('records'), list) or
            len(bundle['records']) > MAX_RECORDS):
        raise BundleError('schema_version=1, 최대 100개 기록의 bundle이 필요합니다.')
    valid_time(bundle.get('exported_at'))
    ids = set()
    for record in bundle['records']:
        validate_record(record)
        if record['id'] in ids:
            raise BundleError('Bundle에 중복 기록 ID가 있습니다.')
        ids.add(record['id'])
    return bundle['records']


def envelope(records):
    return {'schema_version': 1,
            'exported_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'records': records}


def encode(bundle):
    try:
        data = (json.dumps(bundle, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode('utf-8')
    except (UnicodeError, ValueError, RecursionError):
        raise BundleError('Bundle의 문자열·수치·중첩 형식을 확인하세요.') from None
    if len(data) > MAX_BYTES:
        raise BundleError('Bundle 또는 사본 라이브러리는 2MiB 이하여야 합니다.')
    return data


def same_record(left, right):
    # Dict equality would incorrectly treat an extra JSON boolean as the number 1.
    return json.dumps(left, sort_keys=True, ensure_ascii=False, allow_nan=False) == json.dumps(
        right, sort_keys=True, ensure_ascii=False, allow_nan=False)


def atomic_write(path, payload, replace):
    path = safe_path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    safe_path(path.parent)
    fd, temporary = tempfile.mkstemp(prefix='.niil-bundle-', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        safe_path(path)
        if replace:
            os.replace(temporary, path)
        else:
            # A fresh export must not overwrite an existing file, even after a race.
            os.link(temporary, path)
    finally:
        Path(temporary).unlink(missing_ok=True)


def export_records(workspace, output, audience, project_id=None, ids=None):
    root, owner = workspace_owner(workspace)
    if audience not in ('lab', 'project') or (audience == 'project' and not project_id):
        raise BundleError('project 내보내기에는 project_id가 필요합니다.')
    if audience == 'lab' and project_id is not None:
        raise BundleError('project_id는 project audience에만 지정하세요.')
    folder = safe_path(root / 'records')
    if not folder.is_dir():
        raise BundleError('개인 공간의 records 폴더가 필요합니다.')
    target = safe_path(output)
    if target.exists() or target.is_relative_to(folder) or target.is_relative_to(root / 'imports'):
        raise BundleError('원본과 imports 밖의 새 내보내기 파일을 지정하세요.')
    requested = None if ids is None else set(ids)
    if requested is not None and (not requested or len(requested) != len(ids)):
        raise BundleError('선택 ID는 중복 없이 지정하세요.')
    selected, seen = [], set()
    for path in sorted(folder.glob('*.json')):
        record = validate_record(read_json(path))
        if record['id'] in seen:
            raise BundleError('개인 records에 중복 ID가 있습니다.')
        seen.add(record['id'])
        shareable = (record['owner_id'] == owner and record['status'] in ('shared', 'accepted') and
                     record['visibility'] == audience and
                     (audience != 'project' or record['project_id'] == project_id))
        wanted = requested is None or record['id'] in requested
        if wanted and shareable:
            validate_record(record, shared_export=True)
            selected.append(record)
        elif wanted and requested is not None:
            raise BundleError('선택한 기록 중 본인·공유 범위·상태 조건을 충족하지 못한 기록이 있습니다.')
    if requested is not None and requested != {r['id'] for r in selected}:
        raise BundleError('선택한 기록을 본인의 records에서 찾지 못했습니다.')
    if len(selected) > MAX_RECORDS:
        raise BundleError('한 번에 최대 100개 기록을 내보낼 수 있습니다.')
    atomic_write(target, encode(envelope(selected)), replace=False)
    return {'exported': len(selected), 'audience': audience}


@contextmanager
def import_lock(root):
    folder = safe_path(root / 'imports')
    folder.mkdir(parents=True, exist_ok=True)
    safe_path(folder)
    lock = folder / '.bundle-import.lock'
    try:
        # O_EXCL also refuses an existing symlink; the lock's contents are never read.
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        raise BundleError(BUSY_MESSAGE) from None
    identity = None
    try:
        identity = os.fstat(fd)
        yield
    finally:
        os.close(fd)
        try:
            current = lock.lstat()
            if identity is not None and (current.st_dev, current.st_ino) == (identity.st_dev, identity.st_ino):
                lock.unlink()
        except FileNotFoundError:
            pass


def import_records(workspace, bundle_path):
    root, _owner = workspace_owner(workspace)
    with import_lock(root):
        incoming = validate_bundle(read_json(bundle_path))
        library = safe_path(root / 'imports' / 'records.json')
        existing = validate_bundle(read_json(library)) if library.exists() else []
        combined = {record['id']: record for record in existing}
        added, skipped = 0, 0
        for record in incoming:
            if record['id'] in combined:
                if not same_record(combined[record['id']], record):
                    raise BundleError('동일 ID의 다른 내용이 있어 bundle 전체를 반영하지 않았습니다.')
                skipped += 1
            else:
                combined[record['id']] = record
                added += 1
        if len(combined) > MAX_RECORDS:
            raise BundleError('사본 라이브러리는 최대 100개 기록까지 지원합니다.')
        if added:
            atomic_write(library, encode(envelope(list(combined.values()))), replace=True)
    return {'added': added, 'skipped': skipped, 'library': 'imports/records.json',
            'note': '로컬 사본이며 원본 소유권·원격 권한·공유 상태를 변경하지 않습니다.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    export = sub.add_parser('export')
    export.add_argument('--workspace', required=True)
    export.add_argument('--output', required=True)
    export.add_argument('--audience', choices=['lab', 'project'], required=True)
    export.add_argument('--project-id')
    export.add_argument('--ids', nargs='+')
    imports = sub.add_parser('import')
    imports.add_argument('--workspace', required=True)
    imports.add_argument('--bundle', required=True)
    args = parser.parse_args()
    try:
        result = (export_records(args.workspace, args.output, args.audience, args.project_id, args.ids)
                  if args.command == 'export' else import_records(args.workspace, args.bundle))
    except BundleError as exc:
        # BundleError messages are fixed explanations and contain no record values.
        parser.exit(1, str(exc) + '\n')
    except (OSError, RecursionError):
        # Bodies, paths, source text and OS error details may contain private material.
        parser.exit(1, 'Bundle 처리를 중단했습니다. 형식·경로·공유 범위·ID 충돌·크기와 새 출력 파일 여부를 확인하세요.\n')
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    main()
