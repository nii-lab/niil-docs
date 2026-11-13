# Agent 첫 세션 · 재학생·졸업생 공통

이 문서는 Codex 또는 Claude Code가 이미 설치된 참여자를 위한 실행 안내다.
공통 계약은 AGENTS.md, 위임은 GOVERNANCE.md, 개인 설정은 LOCAL.md가 소유한다.

## 첫 실행에서 할 일

1. 현재 디렉터리와 Git 원본을 확인하고 사용자의 기존 변경을 보존한다.
2. AGENTS.md, SYSTEM-PROTOCOL.md, GOVERNANCE.md, LOCAL.md와 current.md를 읽는다. 내 지시에서 보이는
   파일과 추가로 직접 읽은 파일을 구분한다. 자동 로드를 확인하지 못하면 확인했다고 쓰지 않는다.
3. owner_id, participant_type, 실제 참여 프로젝트, upstream, 위임 범위를 확인한다.
   미입력 owner나 권한은 사용자에게 필요한 항목만 묻는다. 신입·졸업 여부로 권한을 추정하지 않는다.
4. 기존 GitHub 연결이 있다면 인증된 계정과 승인 repository 읽기 여부를 확인한다.
   자격 증명·토큰을 출력하지 않는다. 원격에 쓰거나 Issue/PR을 보내기 전 대상·목적을 확인한다.
5. current.md에 목적과 다음 유용한 결과를 짧게 작성한다. 예제 결과를 실제 실행으로 바꾸지 않는다.
6. 최초 작업을 개인 로컬 기록 하나와 공유 초안으로 준비한다. 실제 전송 연결이 없으면 prepared로
   보고한다. 사용자가 승인한 범위 안의 전송은 기존 도구로 수행하고 결과 URL을 확인한다.
7. 공통 JSON 기록의 원본 ID·버전을 보존해 import를 연습한다. 수정한 파생 작업에는 새 ID를 준다.
8. 평소 개인 연구는 본인 GitHub 공간에서 하고, 공유 결과는 본인 Issue 문서로 전달한다. 공동 코드·템플릿을 변경할 때만 승인된 fork/branch와 PR을 사용한다.
9. 재개 시에는 과거 대화 대신 current와 연결된 정확한 근거를 먼저 읽는다.

## Codex

프로젝트 루트의 AGENTS.md를 공통 진입점으로 사용한다. 상위 디렉터리와 AGENTS.override.md 등
기존 지시가 함께 적용될 수 있다. 루트에서 새 세션을 시작하고 아래 확인 요청을 보낸다.
전역 Codex 설정이나 승인 정책을 온보딩 목적으로 변경하지 않는다.

## Claude Code

이 템플릿의 CLAUDE.md는 @AGENTS.md import로 같은 계약을 불러온다. 별도 공통 규약을
CLAUDE.md에 중복 작성하지 않는다. 최신 버전은 AGENTS.md를 직접 읽을 수도 있지만,
버전·상위 CLAUDE.md·설정에 따라 조건이 달라 wrapper를 제공한다. 실제 로드된 파일을
세션에서 확인하고, 읽지 않았다면 명시적으로 AGENTS.md를 열어 확인한다.

## 그대로 보낼 첫 요청

AGENTS.md, GOVERNANCE.md, LOCAL.md와 current.md를 읽어줘. 내가 재학생인지 졸업생인지와
무관하게 실제 승인된 역할·프로젝트 범위 안에서 작업해줘. 먼저 로드한 지시, 내 계정과
공간, 위임 범위, 연결 상태, 비어 있는 설정을 요약하고 첫 기록과 공유 초안을 준비해줘.
내 개인 메모와 credentials는 공유하지 말고, 연결되지 않은 기능은 완료했다고 쓰지 마.

## 첫 응답 형식

- 사용자/owner: 실제 확인 또는 미확인
- 참여 유형: student / alumni / collaborator
- 현재 공간과 upstream: 경로·원본과 확인 상태
- 적용 계약: 읽은 파일과 버전
- 위임 범위: 수행할 수 있는 일과 사람의 결정이 필요한 항목
- 연결: GitHub/NAS 등의 확인 결과, 비밀번호·토큰 제외
- 첫 작업: 목적·산출물·검증·다음 행동
- 필요한 사용자 입력: 아직 결정되지 않은 필수 항목만

## Agent 간 전달

목적·수신 담당자·기대 산출물·근거·기한·위임 범위를 포함하는 요청을 준비한다.
기존 GitHub Issue/PR 또는 승인된 연결을 사용하고, 상대 agent가 상주한다고 가정하지 않는다.
수신 확인과 최종 수용을 구분한다. 재위임으로 사용자 권한을 확대하지 않는다.

## 완료 판단

내 계정과 범위를 확인하고, 개인 기록 한 건·공유 초안·출처 있는 import를 준비했다.
원격 전송을 수행했다면 결과 URL을 읽어 확인했다. 이후 담당자가 current만으로 재개할 수 있다.

공식 근거 (2026-11-10 확인):
https://learn.chatgpt.com/docs/agent-configuration/agents-md
https://code.claude.com/docs/en/memory

연구실 정보가 전혀 없는 사용자는 원본 repository의 START-HERE.md에서 시작한다.

상세 미션은 공개 원본의 guides/agent-tutorial.md를 읽고 M0~M8 순서로 진행한다.


## 연결 후 현재 연구·본인 과업 확인

[로그인부터 내 다음 과업까지](https://github.com/nii-lab/niil-docs/blob/main/guides/login-and-next-task.md)의
일곱 줄 readback으로 웹 인증·API 인증·등록·현재 단계·본인 요청/guide·다음 행동·미검증을 구분한다.
로컬 생성 공간의 current는 개인 기록이고, 프로젝트 current는 참여 프로젝트의 원본이다.
종료된 cycle이나 빈 inbox를 새 실험 지시로 해석하지 않는다. 등록 미연결은 ‘요청 없음’이 아니다.

재개·첫 기여의 보고는 reporting/ 양식을 쓴다. 흐름 전환은 앞 결과/남은 의문/선택 이유와 인계 조건을 연결하고, 종료된 범위는 reporting/closeout.md와 current의 남은 정리만 확인한다. 이 읽기가 역할·권한·예약을 새로 부여하지 않는다.
