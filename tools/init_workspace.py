"""Install a fresh student/project workspace without overwriting existing work."""
import argparse, json, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def create(kind, target, owner):
    target = Path(target).resolve()
    if target.exists() and any(target.iterdir()):
        raise ValueError('대상 폴더가 비어 있지 않습니다. 기존 작업을 덮어쓰지 않습니다.')
    if kind not in {'member', 'project'}:
        raise ValueError('Unknown workspace kind')
    target.mkdir(parents=True, exist_ok=True)
    for folder in ('common', kind):
        for p in (ROOT / 'templates' / folder).rglob('*'):
            if p.is_file():
                rel = p.relative_to(ROOT / 'templates' / folder)
                out = target / rel
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_text(p.read_text().replace('{{owner}}', owner))
    # Match the downloadable starter: reporting forms are available without another checkout.
    shutil.copytree(ROOT / 'templates' / 'reporting', target / 'reporting')
    pr = target / 'pull_request_template.md'
    (target / '.github').mkdir(exist_ok=True)
    shutil.move(pr, target / '.github' / 'pull_request_template.md')
    for name in ('notes', 'records', 'results'):
        (target / name).mkdir(exist_ok=True)
        (target / name / '.gitkeep').touch()
    (target / 'workspace.json').write_text(json.dumps({
        'schema_version': 1, 'template_version': '0.1',
        'kind': kind, 'owner_id': owner, 'default_visibility': 'personal' if kind == 'member' else 'project'
    }, ensure_ascii=False, indent=2) + '\n')
    return target

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--kind', choices=['member', 'project'], required=True)
    parser.add_argument('--target', required=True)
    parser.add_argument('--owner', required=True)
    args = parser.parse_args()
    try:
        print(create(args.kind, args.target, args.owner))
    except ValueError as exc:
        parser.exit(1, str(exc) + '\n')
