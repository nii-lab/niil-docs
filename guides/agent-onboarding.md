# Codex·Claude Code로 NiiL 참여하기

웹 로그인·현재 연구·본인 과업 확인은 [로그인부터 내 다음 과업까지](https://github.com/nii-lab/niil-docs/blob/main/guides/login-and-next-task.md)를 따릅니다.

재학생과 졸업생, 승인된 협력자가 같은 계약과 문서 형식으로 참여합니다.
각자 Codex 또는 Claude Code를 이미 사용하고 있다고 가정합니다. 도구·구독은 개인이 선택합니다.

## 1. 참여와 접근 확인

공개 Wiki와 템플릿은 누구나 읽고 활용할 수 있습니다. 공개 문서 개선은 fork와 PR로 제안합니다.
비공개 프로젝트 참여는 책임자와 범위를 정한 후 해당 repository 접근을 받습니다.
졸업생도 기여자·검토자·멘토·공동연구자로 참여할 수 있으며 졸업 여부가 승인권을 정하지 않습니다.
권한은 현재 프로젝트 역할과 위임 설정으로 정합니다. 실제 초대는 관리자가 진행합니다.

## 2. 새 공간 준비

포털의 개인 공간 ZIP을 새 폴더에 풉니다. 또는 공개 문서 repository를 받아 생성 도구를 사용합니다.

```sh
git clone https://github.com/nii-lab/niil-docs.git
python3 niil-docs/tools/init_workspace.py --kind member --target ./my-niil-workspace --owner MY-GITHUB-ID
cd my-niil-workspace
```

GitHub 계정이 아직 없으면 MY-GITHUB-ID 대신 LOCAL-ONLY를 사용해 로컬만 진행합니다.
Git이 없다면 공개 repo의 Code → Download ZIP을 풀고 해당 폴더의 tools/init_workspace.py를 사용합니다.
생성 전 LOCAL 원본은 templates/member/LOCAL.md, 생성 후에는 개인 공간의 LOCAL.md입니다.
init_workspace.py만 단독 다운로드하면 templates 경로가 없어 동작하지 않습니다.

MY-GITHUB-ID를 본인 계정으로 바꿉니다. 생성 도구는 비어 있는 대상 폴더만 사용합니다.
공동 프로젝트 starter는 실제 프로젝트 책임자가 역할·검토자·위임 한도를 채워 사용합니다.

## 3. 내 agent에서 시작

Codex는 프로젝트 루트의 AGENTS.md를 읽습니다. 상위 지시와 override가 적용될 수 있으므로
첫 요청에서 읽은 계약과 실제 위임 범위를 확인합니다. 전역 설정을 바꿀 필요는 없습니다.

Claude Code용 CLAUDE.md는 공통 AGENTS.md를 import합니다. 일부 최신 버전의 자동 인식 여부와
관계없이 같은 계약을 읽도록 제공하는 호환 진입점입니다. 지시 본문은 AGENTS.md에서 관리합니다.

## 4. 첫 요청

AGENT-ONBOARDING.md의 첫 요청을 내 agent에 보냅니다. owner·역할·upstream·위임 범위와
연결 상태를 확인하고 기록 한 건, 공유 초안, 출처 있는 import를 연습합니다.
agent가 실제로 수행한 것과 준비만 한 것을 구분해 보고하게 합니다.

## 5. 졸업 후 다시 참여

과거에 받은 권한이나 저장해 둔 세션이 유효하다고 가정하지 않습니다. 현재 소속·참여 프로젝트·
기여 방식·연락 경로를 갱신하고 책임자에게 재참여 범위를 확인합니다. 이전 기여와 원본 출처는
유지하고 새 프로젝트의 접근은 별도로 확인합니다. 기관 자산을 새 소속으로 복사하기 전 사용 범위를 확인합니다.

## 6. 첫 기여

문서 정정은 공개 niil-docs에 PR로 제안하고, 비공개 연구 개선은 승인된 프로젝트에 PR로 보냅니다.
요청은 목적·근거·기대 산출물·기한을 적습니다. 연구 결론 채택·대외 공개·권한 변경은 현재
지정된 결정권자에게 연결합니다. agent 간 소통과 사람의 직접 질문을 모두 허용합니다.

[Agent 첫 세션 계약](https://github.com/nii-lab/niil-docs/blob/main/templates/common/AGENT-ONBOARDING.md)

[Codex 공식 안내](https://learn.chatgpt.com/docs/agent-configuration/agents-md)

[Claude Code 공식 안내](https://code.claude.com/docs/en/memory)
