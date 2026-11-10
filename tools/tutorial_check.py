"""Read local tutorial artifacts; never authenticate, execute agents or send messages."""
import argparse,json
from pathlib import Path

def check(root):
    root=Path(root)
    required=['environment.md','contract-readback.md','task-plan.md','receive-decision.json','import-check.md','result-envelope.json','state.json']
    missing=[p for p in required if not (root/p).is_file()]
    if missing:return {'status':'incomplete','missing':missing}
    state=json.loads((root/'state.json').read_text())
    if state.get('status') not in ['not_started','in_progress','passed_local','passed_live','needs_owner','needs_access']:
        raise ValueError('Unknown tutorial state')
    decision=json.loads((root/'receive-decision.json').read_text())
    if decision.get('decision') not in ['eligible','needs_owner','needs_access','declined']:
        raise ValueError('Receive decision must be explicit')
    if not decision.get('reason'):raise ValueError('Decision requires a reason')
    return {'status':'artifacts_present','mission_status':state['status'],'note':'File presence does not prove live authentication or execution. Verify evidence separately.'}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--target',required=True);a=p.parse_args()
    print(json.dumps(check(a.target),ensure_ascii=False,indent=2))
