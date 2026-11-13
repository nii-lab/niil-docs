# NiiL 처음 시작하기 · 사람과 agent의 공통 입구

연구실 배경지식이나 Git 경험 없이 시작할 수 있습니다. 각자 사용하는 Codex 또는
Claude Code에 아래 문장을 보내세요. 공통 매뉴얼을 읽고 첫 실습을 순서대로 안내합니다.

## 그대로 보낼 문장

나는 NiiL에 처음 참여합니다. 연구실과 Git에 대한 지식이 없습니다.
https://raw.githubusercontent.com/nii-lab/niil-docs/main/START-HERE.md 를 읽고 안내해 주세요.
설치·계정 상태를 확인하되 한 번에 필요한 질문만 하고, 로컬 개인 공간과 첫 기록부터
함께 만들어 주세요. 내 agent의 자동 실행·승인·알림 정책은 내가 선택하게 해 주세요.
모르는 계정·소속·권한은 추정하지 말고, 실제 연구실 참여 권한은 별도로 확인해 주세요.

## 문서 버전을 기록하기

평소에는 최신 main의 안내를 사용합니다. 검증·재현 목적으로 특정 commit의 이 문서를 받았다면,
공개 후속 매뉴얼도 같은 commit으로 읽고 그 revision을 보고합니다. 문서 내부 main 링크는
같은 repository/path의 고정 revision으로 바꿔 읽을 수 있습니다. 이미 폐기된 인계나 과거
문서를 현재 운영 지시로 삼지 않습니다. **연구 current·요청 상태는 이 공개 매뉴얼의 commit에
고정하지 않고**, 실제 승인된 프로젝트의 최신 원본/이벤트와 확인 시각을 별도로 대조합니다.

## Agent: 첫 실행 순서

1. 이 문서와 templates/common/AGENTS.md, templates/common/SYSTEM-PROTOCOL.md를 읽는다.
   공식 원본은 https://github.com/nii-lab/niil-docs 이다. raw 주소를 읽을 수 없으면 공개 본문
   https://github.com/nii-lab/niil-docs/blob/main/START-HERE.md 로 안내한다. 두 경로를 모두
   읽지 못하면 운영자에게 공통 매뉴얼을 요청하고, 읽지 못한 규약을 읽었다고 보고하지 않는다.
   조직 초대 전에는 멤버 전용 포털 접근을 온보딩의 선행 조건으로 삼지 않는다.
2. 사용자의 현재 환경에서 할 수 있는 일을 먼저 확인한다. 처음에는 사용 중인 agent와
   작업할 컴퓨터/OS만 확인하고, 알아낼 수 있는 정보를 다시 묻지 않는다. GitHub 계정은
   공동 참여가 필요할 때 확인한다. 계정 생성·로그인에서 사용자가 직접 해야 하는 단계를 안내한다.
3. 새 로컬 폴더에 개인 starter를 준비한다. 생성 전 개인 설정의 원본 위치는
   templates/member/LOCAL.md다(templates/common/LOCAL.md는 없다). 생성 후에만 내 LOCAL.md를 읽는다. 기존 파일을 덮어쓰지 않는다. 설치되지 않은
   프로그램을 먼저 잔뜩 요구하지 않는다. 가능하면 ZIP과 텍스트 편집만으로 시작한다.
4. owner_id와 실제 이름이 준비되지 않았다면 LOCAL-ONLY 임시 식별자로 로컬 실습한다.
   이 임시 ID를 운영 계정으로 등록하거나 외부에 게시하지 않는다. 나중에 GitHub 계정과 연결한다.
5. current.md에 사용자가 관심 있는 질문 한 가지와 다음 작은 작업을 적는다. 첫 기록은
   관심 주제·읽은 자료·다음 질문이면 충분하다. 실행하지 않은 실험 결과를 만들지 않는다.
6. 승인·자동 실행 정책은 본인이 선택하게 한다. 설명은 “받은 요청을 매번 확인”,
   “내가 고른 종류만 자동 처리”, “내가 정한 범위 안에서 자동 처리” 세 방식으로 시작한다.
   미선택 상태는 설정 대기다. 개인 정책과 실제 프로젝트 권한을 구분한다.
7. 공개 예시를 가져와 출처를 보존하는 실습을 한다. 연구실 초대 없이도 이 단계까지 할 수 있다.
8. 실제 참여할 때 guides/repository-access.md와 guides/connected-onboarding.md를 읽고 GitHub 계정·프로젝트 책임자·접근 범위를 연결한다. 비공개 연구는
   권한을 받은 후 읽는다. 모든 참여자는 신규·재학생·졸업생에 관계없이 같은 절차를 사용한다.
9. 마지막에 만든 폴더·읽은 계약·첫 기록·선택한 개인 정책·다음 단계만 짧게 보고한다.
   설치/초대/실시간 agent 연결이 준비되지 않았다면 남은 단계로 표시한다.

## 사람에게 보이는 첫날의 완료

내 공간이 생겼고, 다음에 할 일이 적힌 기록 하나가 있으며, 공유 전 내가 확인할 범위를
정했습니다. 실제 초대나 원격 실행은 다음 단계여도 됩니다. Agent 결제와 별개로 프로젝트
초대·GitHub 인증·컴퓨터 실행 환경은 본인에게 연결해야 합니다. Agent가 그 과정을 안내합니다.

## 계정이 없어도 시작하는 정확한 경로

공개 repository의 [공간 준비 안내](https://github.com/nii-lab/niil-docs/blob/main/guides/agent-onboarding.md)를 따라
공통 templates/common/과 개인 templates/member/를 함께 준비한다. init_workspace.py 한 파일만
받으면 상대 경로의 templates가 없어 실행되지 않는다. 공개 repo 전체를 clone하거나 GitHub의
Code → Download ZIP으로 받은 뒤, 그 안의 tools/init_workspace.py를 사용한다. Python/Git이
없으면 같은 두 template 폴더의 파일을 새 개인 폴더에 복사하고 실제 미완료 도구 검사는 남긴다.
GitHub 계정이 없을 때 owner는 LOCAL-ONLY로만 사용한다. 이것은 운영 등록이 아니다.

가입·초대나 담당자가 필요한 단계는 [참여 접수 안내](https://github.com/nii-lab/niil-docs/blob/main/guides/participation.md)를 따른다.
처음 보는 사람도 공개 접수 경로를 사용할 수 있지만 실제 승인은 운영자가 별도로 검토한다.
연결되지 않은 계정/권한을 성공으로 표시하지 않는다.

## 초대 수락 후 · 로그인과 내 다음 과업

[로그인부터 내 다음 과업까지](https://github.com/nii-lab/niil-docs/blob/main/guides/login-and-next-task.md)를 따릅니다.
웹 로그인·agent GitHub 인증·참여자 등록은 별개로 확인합니다. 현재 프로젝트와 본인 요청 원문을 읽고,
일이 없거나 연구가 종료됐을 때도 다음 행동을 정확히 보고합니다. 로그인 오류의 복구 순서도 이 안내에 있습니다.
이미 GitHub 도구가 연결된 agent는 같은 안내의 읽기 전용 registry·생성 branch 경로를 사용할 수 있습니다.
계정/초대/프로젝트가 없다면 비공개 연구·본인 요청은 미확인으로 남기고 참여 연결부터 요청합니다.

## 촘촘한 실습

guides/agent-tutorial.md의 M0~M8을 순서대로 수행한다. 각 단계에서 산출물을 검증하고,
사용자 결정이나 접근이 필요한 단계는 대기 상태로 보존한다. 첫 프롬프트 하나로 모든
연결이 완료됐다고 보고하지 않는다.

## 더 자세히

- guides/agent-onboarding.md: Codex·Claude Code 연결과 첫 세션
- templates/common/AGENTS.md: 짧은 공통 계약
- templates/common/SYSTEM-PROTOCOL.md: 작업 요청·응답·시스템 유지보수
- templates/common/agent-policy.example.json: 개인이 정하는 위임·승인 정책

환경 진단: guides/readiness.md와 tools/doctor.py를 참고해 부분별 준비 상태와 다음 대응을 제시한다.
