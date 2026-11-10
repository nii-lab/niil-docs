"""Local preflight only: no model call, no execution and no permission grant."""
import argparse,json
from pathlib import Path


def classify(task,policy,read_access=False):
    def answer(status,reason):return {'decision':status,'reason':reason,'task_id':task.get('task_id'),'guide_revision':task.get('guide_revision'),'execution_started':False}
    if task.get('protocol_version','').split('.')[0]!='1':return answer('needs_owner','프로토콜 호환성 확인 필요')
    if not policy.get('configured_by_owner') or policy.get('mode')=='unconfigured':return answer('needs_owner','본인의 승인·위임 정책 미선택')
    if policy.get('owner_id')!=task.get('to_owner'):return answer('needs_owner','내 소유자와 수신자 불일치')
    if task.get('repository') not in policy.get('allowed_repositories',[]):return answer('needs_access','이 프로젝트가 내 허용 범위에 없음')
    if not read_access:return answer('needs_access','실제 원본 읽기 접근 미확인')
    if task.get('from_owner') not in policy.get('allowed_senders',[]):return answer('needs_owner','이 발신자의 자동 요청은 미위임')
    actions=task.get('requested_actions')
    if not isinstance(actions,list) or not actions:return answer('needs_owner','필요 행동이 구체적으로 정의되지 않음')
    if policy.get('mode')=='manual':return answer('needs_owner','본인이 요청마다 확인하기로 선택함')
    if policy.get('mode') not in ['allowlist','auto_within_scope']:return answer('needs_owner','알 수 없는 개인 정책')
    if not set(actions)<=set(policy.get('automatic_actions',[])):return answer('needs_owner','요청 행동이 자동 위임 범위를 넘음')
    return answer('eligible','개인 정책의 사전 조건 충족. 실제 guide 내용·원격 권한·자원 범위는 실행 전 확인')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--task',required=True);p.add_argument('--policy',required=True);p.add_argument('--read-access-verified',action='store_true');a=p.parse_args()
    print(json.dumps(classify(json.loads(Path(a.task).read_text()),json.loads(Path(a.policy).read_text()),a.read_access_verified),ensure_ascii=False,indent=2))
