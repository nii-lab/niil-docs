"""Read-only readiness diagnosis. Does not install, invite, change policy or start an agent."""
import argparse,datetime,json,os,shutil,subprocess
from pathlib import Path

def policy_git_check(workspace):
    """Inspect only this workspace's policy path; never read policy contents here."""
    git=shutil.which('git')
    if not git:
        return ('unknown','Git이 없어 제외·추적 상태를 확인하지 못함',
                '로컬 실습은 계속할 수 있습니다. 공유 전 Git 환경에서 개인 정책의 제외·미추적 상태를 확인하세요.')
    root=str(Path(workspace).resolve())
    def run(*args):
        return subprocess.run([git,'-C',root,*args],capture_output=True,text=True,timeout=5)
    try:
        repo=run('rev-parse','--is-inside-work-tree')
        if repo.returncode!=0 or repo.stdout.strip()!='true':
            return ('unknown','Git 작업 트리를 확인하지 못해 개인 정책의 제외·추적 상태는 미확인',
                    'Git 미설정 상태에서도 로컬 실습은 계속할 수 있습니다. 공유할 repository를 정한 뒤 재진단하세요.')
        tracked=run('ls-files','--error-unmatch','--','agent-policy.local.json')
        if tracked.returncode==0:
            return ('needs_setup','agent-policy.local.json이 Git에서 추적 중임',
                    '공유 전 추적 상태와 이력을 확인하고 개인 정책을 공유하지 않도록 정리하세요. 진단은 추적 해제를 수행하지 않습니다.')
        if tracked.returncode!=1:
            return ('unknown','Git의 추적 상태를 확인하지 못함',
                    'Git 작업 트리와 접근 상태를 확인한 뒤 재진단하세요.')
        ignored=run('check-ignore','--no-index','--quiet','--','agent-policy.local.json')
        if ignored.returncode==0:
            return ('ready','Git 실제 판정으로 개인 정책의 제외·미추적 상태를 확인함',
                    '현재 repository의 제외·추적 검사 결과입니다. 변경 후나 공유 전에 재진단하세요.')
        if ignored.returncode==1:
            return ('needs_setup','agent-policy.local.json이 Git 제외 대상이 아님',
                    '.gitignore 등에 유효한 제외 규칙을 설정하고 부정 규칙이나 덮어쓰기도 확인한 뒤 재진단하세요.')
        return ('unknown','Git의 제외 판정을 확인하지 못함',
                'Git 설정과 작업 트리를 확인하고 공유 전에 재진단하세요.')
    except (OSError,subprocess.TimeoutExpired):
        return ('unknown','Git 읽기 검사가 실패했거나 시간 초과됨',
                '로컬 실습은 계속할 수 있습니다. 공유 전 Git 환경을 확인하고 재진단하세요.')

def diagnose(workspace,live=False):
    root=Path(workspace).resolve();checks=[]
    def add(id,title,status,evidence,action):checks.append(dict(id=id,title=title,status=status,evidence=evidence,action=action))
    add('workspace','개인 작업 공간','ready' if root.is_dir() and (root/'current.md').is_file() else 'needs_setup','current.md 존재 확인' if (root/'current.md').is_file() else '현재 상태 문서 없음','새 폴더에 starter를 준비하고 current.md에 목적과 다음 작업을 적으세요.')
    files=['AGENTS.md','SYSTEM-PROTOCOL.md','GOVERNANCE.md','LOCAL.md']
    missing=[x for x in files if not (root/x).is_file()]
    add('contract','공통 규약','ready' if not missing else 'needs_setup','파일 존재 확인. agent의 실제 로드 여부는 별도 확인.' if not missing else '없는 파일: '+', '.join(missing),'공통 starter의 계약 파일을 준비하고 agent에게 읽은 버전과 범위를 설명하게 하세요.')
    policy={};problem=''
    try:
        policy=json.loads((root/'agent-policy.local.json').read_text())
        if not isinstance(policy,dict) or policy.get('schema_version')!=1 or policy.get('mode') not in ['unconfigured','manual','allowlist','auto_within_scope']:raise ValueError('지원하지 않는 개인 정책')
    except FileNotFoundError:policy={};problem='개인 정책 미선택'
    except (ValueError,TypeError):policy={};problem='개인 정책 형식 확인 필요'
    configured=not problem and policy.get('configured_by_owner') is True and policy.get('mode')!='unconfigured'
    add('delegation','개인 위임·승인','ready' if configured else 'needs_owner',('본인이 선택한 '+policy['mode']+' 정책. 실제 권한과 별도.' if configured else problem or '정책이 아직 미선택 상태'),'본인이 승인 방식·허용 행동·발신자·프로젝트를 정하고 agent-policy.local.json에 저장하세요.')
    privacy_status,privacy_evidence,privacy_action=policy_git_check(root)
    add('private_policy','개인 정책 보관',privacy_status,privacy_evidence,privacy_action)
    gh=shutil.which('gh')
    if not live:
        add('github','GitHub 계정·프로젝트 접근','unknown','원격 조회를 수행하지 않음','공동 참여 시 --live-readonly로 본인 인증과 허용 repository 접근을 확인하세요. 로컬 실습은 먼저 진행할 수 있습니다.')
    elif not gh:
        add('github','GitHub 계정·프로젝트 접근','needs_setup','GitHub CLI 없음','본인의 GitHub 연결 도구로 로그인과 프로젝트 읽기를 확인하세요. CLI 설치는 선택 사항입니다.')
    else:
        try:
            p=subprocess.run([gh,'api','user','--jq','.login'],text=True,capture_output=True,timeout=15)
            login=p.stdout.strip() if p.returncode==0 else None
            repos=policy.get('allowed_repositories',[]);ok=bool(login)
            if policy.get('owner_id') and login!=policy['owner_id']:ok=False
            for repo in repos:
                if not isinstance(repo,str) or repo.count('/')!=1:ok=False;continue
                q=subprocess.run([gh,'api','repos/'+repo,'--jq','.permissions.pull'],capture_output=True,text=True,timeout=15)
                if q.returncode!=0 or q.stdout.strip()!='true':ok=False
            add('github','GitHub 계정·프로젝트 접근','ready' if ok and repos else 'needs_access','인증 계정·읽기 접근 확인' if ok and repos else '본인 계정 또는 참여 범위·읽기 접근 확인 필요','초대 수락과 본인 인증을 확인하고 실제 참여 repository만 정책에 등록하세요. 쓰기·fork·merge 권한은 별도 확인합니다.')
        except subprocess.TimeoutExpired:add('github','GitHub 계정·프로젝트 접근','unknown','원격 조회 시간 초과','네트워크를 확인한 뒤 재진단하세요. 실패를 권한 부재로 단정하지 마세요.')
    relay_env=bool(os.environ.get('NII_RELAY_URL')) and bool(os.environ.get('NII_AGENT_TOKEN'))
    add('realtime','실시간 도착 연결','unknown','연결 설정 존재, 수신 실습 미확인' if relay_env else '개인 연결기·수신 실습 확인 전','내부 운영자의 등록 후 가상 이벤트→실제 수신→오프라인 cursor 복구를 확인하세요. 설정 값의 존재만으로 정상 연결을 판정하지 않습니다.')
    add('runner','Agent 실행·재개','unknown','개인의 runner 기동·재개를 수행하지 않음','본인이 선택한 실행 환경에서 요청 도착 시 새 작업 시작과 사용자 결정 후 재개를 실습하세요. 현재 대화창이 자동으로 깨어난다고 가정하지 않습니다.')
    state=root/'.local/onboarding/state.json'
    add('tutorial','튜토리얼 근거','needs_setup' if not state.exists() else 'unknown','진행 상태 파일 없음' if not state.exists() else '진행 상태 파일 존재. 개별 근거 확인 필요.','M0~M8 산출물과 검증을 남기고 passed_local과 passed_live를 구분하세요.')
    return dict(schema_version=1,kind='niil-readiness',generated_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),checks=checks,note='진단은 읽기 전용이며 agent 실행·계정 초대·승인 정책을 변경하지 않습니다.')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--workspace',default='.');p.add_argument('--live-readonly',action='store_true');p.add_argument('--output');a=p.parse_args();s=json.dumps(diagnose(a.workspace,a.live_readonly),ensure_ascii=False,indent=2)
    if a.output:Path(a.output).write_text(s+'\n')
    else:print(s)
