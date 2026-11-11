"""Prepare a pinned NiiL client for the signed-in owner. Does not execute it."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[1]
REPOSITORY='nii-lab/niil-internal'
FILES={'hub.py':'services/github_hub/hub.py','participant.py':'services/github_hub/participant.py'}


def gh(path):
    return json.loads(subprocess.check_output(['gh','api',path],text=True,encoding='utf-8',stderr=subprocess.DEVNULL))


def fetch_file(path,revision):
    value=gh(f'repos/{REPOSITORY}/contents/{path}?ref={revision}')
    if value.get('encoding')!='base64':raise ValueError('GitHub file encoding not supported')
    data=base64.b64decode(value['content'])
    if len(data)>300000:raise ValueError('client file size limit')
    identity=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
    if identity!=value.get('sha'):raise ValueError('GitHub blob checksum mismatch')
    return data


def install(workspace,revision):
    workspace=Path(workspace).resolve()
    if not re.fullmatch('[a-f0-9]{40}',revision):raise ValueError('an immutable 40-character release commit is required')
    config=json.loads((workspace/'workspace.json').read_text(encoding='utf-8'))
    profile=gh('user');owner=profile['login']
    if config.get('kind')!='member' or config.get('owner_id')!=owner:
        raise ValueError('workspace owner must match the actual signed-in GitHub account')
    privacy=subprocess.run(['git','-C',str(workspace),'check-ignore','--no-index','--quiet','--','.local/niil-client/probe'],capture_output=True,timeout=5)
    if privacy.returncode!=0:raise ValueError('.local/niil-client must be Git-ignored before preparation')
    membership=gh('user/memberships/orgs/nii-lab')
    if membership.get('state')!='active':raise ValueError('active nii-lab membership is required; do not create or accept an invitation automatically')
    repository=gh(f'repos/{REPOSITORY}')
    if repository.get('private') is not True or repository.get('permissions',{}).get('pull') is not True:
        raise ValueError('read access to the private shared hub is required')
    if gh(f'repos/{REPOSITORY}/commits/{revision}').get('sha')!=revision:
        raise ValueError('release commit could not be verified')
    registry_revision=gh(f'repos/{REPOSITORY}/commits/main')['sha']
    if not re.fullmatch('[a-f0-9]{40}',registry_revision):raise ValueError('registry revision')
    registry_bytes=fetch_file('ops/live/participants.json',registry_revision)
    registry=json.loads(registry_bytes)
    entry=registry.get('participants',{}).get(owner,{})
    if registry.get('repository')!=REPOSITORY or entry.get('github_id')!=profile['id'] or not entry.get('projects'):
        raise ValueError('operator registration is required; submit the owner ID/project for review instead of self-registering')
    client_root=workspace/'.local/niil-client'
    if not client_root.resolve().is_relative_to(workspace):raise ValueError('client output must remain inside the personal workspace')
    target=client_root/(revision[:12]+'-'+registry_revision[:12])
    for relative in [str((target/name).relative_to(workspace)) for name in (*FILES,'participants.json','receipt.json')]+['.local/niil-client/current.json']:
        tracked=subprocess.run(['git','-C',str(workspace),'ls-files','--error-unmatch','--',relative],capture_output=True,timeout=5)
        ignored=subprocess.run(['git','-C',str(workspace),'check-ignore','--no-index','--quiet','--',relative],capture_output=True,timeout=5)
        if tracked.returncode!=1 or ignored.returncode!=0:
            raise ValueError('every client output must be untracked and Git-ignored; check negation rules')
    files={name:fetch_file(source,revision) for name,source in FILES.items()}
    files['participants.json']=registry_bytes
    checksums={name:hashlib.sha256(data).hexdigest() for name,data in files.items()}
    client_root.mkdir(parents=True,exist_ok=True,mode=0o700)
    receipt={'schema_version':1,'owner_id':owner,'github_id':profile['id'],'repository':REPOSITORY,
      'code_revision':revision,'registry_revision':registry_revision,'sha256':checksums,
      'client_executed':False,'policy_changed':False,'remote_writes':False}
    if target.is_symlink():raise ValueError('client target must not be a symlink')
    if target.exists():
        existing=json.loads((target/'receipt.json').read_text(encoding='utf-8'))
        if existing!=receipt or any((target/name).is_symlink() or hashlib.sha256((target/name).read_bytes()).hexdigest()!=value for name,value in checksums.items()):
            raise ValueError('existing client differs; preserve it and request review')
        unchanged=True
    else:
        with tempfile.TemporaryDirectory(dir=client_root) as temporary:
            stage=Path(temporary)/'client';stage.mkdir(mode=0o700)
            for name,data in files.items():
                path=stage/name;path.write_bytes(data);path.chmod(0o600)
            (stage/'receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
            (stage/'receipt.json').chmod(0o600)
            stage.rename(target)
        unchanged=False
    pointer={'schema_version':1,'owner_id':owner,'client_directory':str(target),
             'code_revision':revision,'registry_revision':registry_revision}
    with tempfile.NamedTemporaryFile(mode='w',dir=client_root,delete=False,encoding='utf-8') as temp:
        json.dump(pointer,temp,ensure_ascii=False,indent=2);temp.write('\n');temp_name=temp.name
    os.replace(temp_name,client_root/'current.json')
    return {**pointer,'unchanged':unchanged,'client_executed':False,'policy_changed':False,
      'next_action':'Read the pinned client and choose your own policy; run inbox/outbox before any share/event.'}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--workspace',type=Path,required=True);p.add_argument('--ref')
    a=p.parse_args()
    try:
        revision=a.ref or json.loads((ROOT/'hub-client-release.json').read_text(encoding='utf-8'))['revision']
        print(json.dumps(install(a.workspace,revision),ensure_ascii=False,indent=2))
    except (ValueError,OSError,KeyError,subprocess.SubprocessError) as exc:
        # Never print GitHub response bodies, authentication state, tokens or policy contents.
        raise SystemExit('Client preparation needs attention: '+str(exc) if isinstance(exc,ValueError) else 'Client preparation stopped; verify login, membership, registration and local prerequisites.')
