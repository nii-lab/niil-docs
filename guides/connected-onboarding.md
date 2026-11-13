# 개인 GitHub 공간을 연구실에 연결하기

웹 로그인·현재 연구·본인 과업 확인은 [로그인부터 내 다음 과업까지](https://github.com/nii-lab/niil-docs/blob/main/guides/login-and-next-task.md)를 따릅니다.

처음 참여하는 사람은 START-HERE.md의 한 문장으로 시작한다. 이 문서는 agent가 M6에서
필요한 단계만 읽는 실행 안내다. 개인 연구를 위한 공통 파일 편집이나 PR은 요구하지 않는다.

## 1. 사람·개인 공간·접근 확인

기존 GitHub 인증으로 실제 login과 numeric ID를 확인한다. workspace.json의 owner_id를
그 login과 맞춘다. 개인 연구 repository는 nii-lab 아래의 독립 Private 저장소를 기본으로 한다.
교수 Admin/담당자 Write/기타 조직 멤버 Read를 실제 권한으로 확인한다. repo owner가 nii-lab이어도
기록 owner_id는 사람의 실제 GitHub login이다. private fork를 개인 연구 정본으로 쓰지 않는다.
[저장소·권한 안내](repository-access.md)에 따라 관리자에게 생성/담당자 연결을 요청한다.

처음 참여하거나 담당자를 모르면 [참여 접수 안내](https://github.com/nii-lab/niil-docs/blob/main/guides/participation.md)의 공개 경로로 연결을 요청한다.
조직 멤버십, 공용 허브 읽기, 참여할 project 등록은 별개다. 초대/등록이 없으면 운영자에게
실제 login·project만 전달하고 needs_access로 멈춘다. 운영자는 멤버십·프로젝트 책임을 확인한 뒤
numeric ID와 project를 registry에 PR로 등록한다. 학생 agent가 임의 초대·등록·권한 확대를 하지 않는다.
졸업생도 같은 절차를 사용한다. 혼자만 볼 자료는 로컬에 보존하고 연구실 저장소에는 멤버 열람을
전제로 기록한다. agent 집계는 저장소 전체를 수집하지 않고 공유 승인한 Issue만 읽는다.

## 2. 필요한 연결 도구만 준비

공개 niil-docs의 tools/install_hub_client.py를 일반 Python으로 실행한다. 한국어 문서는 UTF-8로 유지한다.
Windows에서는 실제 설치된 Python launcher(예: py -3)를 사용하고, 기존 진단·초기화 도구에도
-X utf8 옵션을 사용해 locale에 따라 파일 인코딩이 달라지지 않게 한다.

```sh
python3 tools/install_hub_client.py --workspace /실제/개인/공간
```

hub-client-release.json이 가리키는 immutable commit의 participant.py/hub.py만 받는다.
registry는 최신 main commit에서 별도로 받는다. actual login·멤버십·Read 접근·등록 ID와
Git의 .local/ 제외를 확인하고 Git blob checksum을 대조한다. 전체 private repo는 clone하지 않는다.
출력은 개인 .local/niil-client/ 아래며 이전 버전과 개인 파일·정책을 덮어쓰지 않는다.
설치는 agent를 실행하거나 원격에 글을 쓰지 않는다. receipt.json과 current.json은 설치 근거다.
설치했다고 실제 요청·승인·예약 실행까지 완료로 보고하지 않는다.

Agent는 current.json의 client_directory를 읽어 다음 명령의 CLIENT 부분에 실제 경로를 사용한다.

```sh
python3 CLIENT/participant.py --workspace /실제/개인/공간 --registry CLIENT/participants.json inbox
python3 CLIENT/participant.py --workspace /실제/개인/공간 --registry CLIENT/participants.json outbox
```

설치 후 새 참여자/프로젝트가 추가되면 설치 명령을 다시 실행해 registry snapshot을 갱신한다.
코드 버전은 공개 release pin을 따르고, 임의 수정한 client는 자동으로 덮어쓰지 않는다.

복귀 시 initializer를 기존 폴더에 재실행하지 않는다. 다른 로그인은 owner_id 변경으로
맞추지 않고 실제 인증을 바로잡는다. 수정된 client는 설치가 중단되며 변경 내용을 보존하고
본인이 검토·복원/업데이트를 선택한 뒤 재시도한다. 정책/결정 파일은 Git에 없으므로 본인의
안전한 백업으로 복구하거나 다시 선택한다. 재설치가 개인 승인을 복원했다고 보고하지 않는다.

## 3. 본인이 승인·처리 주기 선택

agent-policy.example.json을 설명하고 본인이 선택한 값을 로컬 agent-policy.local.json에 저장한다.
mode는 manual / allowlist / auto_within_scope 중 본인의 선택이다. configured_by_owner=true는
실제로 선택한 후에만 기록한다. 자동 실행은 repository·project_ids·allowed_senders·automatic_actions를
모두 만족해야 한다. 각 범위는 문자열 목록이며 빈 범위를 전체 허용으로 해석하지 않는다.

행동 이름: read_shared(공유 문서 읽기), respond(범위 내 응답·상태 기록), share_result(본인이
lab 공유 확정한 records/ 문서 발행). 발신자의 accept_response는 검토한 답변을 수용하는 추가
위임이므로 별도로 선택한다. 수신자가 발신자의 수용을 대신하지 않는다. 어떤 선택도 새 비용,
계정 권한, 연구 결론의 학술적 타당성을 자동 승인하지 않는다.

처리 주기는 본인이 정한다. 수동/하루 두 번 같은 선택도 가능하다. 상시 push나 개인 daemon은
첫 결과 공유의 필수 조건이 아니다. 계정 결제만으로 기기·앱·권한·자동 실행이 준비되는 것은 아니다.

## 4. 작은 공유·요청부터 확인

개인 records/의 본인 결과 하나를 골라 공유 scope, 원본 commit, 관찰·해석·한계·다음 행동을
확인한다. visibility=lab/status=accepted는 공유 확정의 뜻이며 학술 결과 입증 완료가 아니다.
첫 공유의 version은 1이다. share로 같은 owner/id의 공유 Issue를 만들고 갱신할 때 version을 올린다. 원본 개인 note는 유지한다.

manual에서 현재 client의 share는 일회 결정 옵션을 지원하지 않아 게시를 거절한다.
이때 정확한 기록·대상 Issue와 공개 범위를 먼저 본인에게 보여 주고, **이번 전송을 실제로
승인받은 후** 일반 GitHub Issue 도구로 같은 niil-record 형식을 게시/갱신한다. 게시 전 실제
저장소·작성자·owner/id를 대조해 기존 Issue가 있으면 재사용하고, 내용이 같으면 생략한다.
응답이 끊겨도 생성 여부를 다시 조회한 뒤 재시도한다. 지원 도구가 없으면 초안을 보존하고
needs_access로 남긴다. manual을 자동 모드로 변경해 우회하지 않는다. 요청 event는 실제
본인 결정을 받은 뒤 이 안내의 --decision 경로를 사용할 수 있으며 기존 정책은 유지한다.

새 요청은 사용자가 이번 전송을 직접 요청했거나 본인 정책의 전송 범위에 들어갈 때만 보낸다.
실제 수신자·project·audience를 확인하고 GitHub 도구로 Issue를 생성한다. 이 허브는 lab 공유만
집계하므로 project-private 자료를 임의로 lab으로 바꾸지 않는다. 다음 JSON은 실제 값을 확인한 뒤
Issue 본문의 niil-work-order 코드 블록에 넣는 형식이다. placeholder를 그대로 게시하지 않는다.

```json
{
  "schema_version": 1,
  "request_id": "REPLACE-WITH-UNIQUE-ID",
  "from_owner": "REPLACE-WITH-ACTUAL-SENDER",
  "to_owner": "REPLACE-WITH-REGISTERED-RECIPIENT",
  "project_id": "REPLACE-WITH-REGISTERED-PROJECT",
  "visibility": "lab",
  "title": "요청 제목",
  "task_definition": "목적, 제공 자료와 버전, 수행할 작업과 범위",
  "expected_output": "산출물, 검증 방법과 완료 기준",
  "guide_revision": "v1",
  "requested_actions": ["read_shared", "respond"]
}
```

기존 work-order.example.json은 로컬 계획·진단용이다. 실제 Issue로 보낼 때 task_id는 request_id,
goal/inputs는 task_definition, deliverables/definition_of_done/verification은 expected_output으로
연결하고 guide_revision은 유지한다. 예시를 실제 요청으로 간주하지 않는다. 전송 저장소는 등록된
허브와 실제 프로젝트 범위를 확인하며, 비공개 개인 대화나 정책 파일을 복사하지 않는다. 본문은
구조화된 도구 인자 또는 UTF-8 body 파일로 전달하고 셸 코드로 이어 붙이지 않는다.

요청을 받으면 guide SHA와 실제 발신자·project·요청 행동을 확인한다. 자동 범위가 부족하면
needs_owner로 남기고 본인에게 필요한 결정만 묻는다. manual에서는 원격 기록도 먼저 확인받는다.
사용자 답변 없이 승인 파일이나 승인 이력을 만들지 않는다. 일회 결정은 그 요청/guide/행동/이벤트에
묶어 .local/decisions/에 보관하고 event의 --decision으로 재개한다. 공통 정책을 자동 확대하지 않는다.

수신→진행→응답은 수신자, 수용/취소는 발신자가 기록한다. inbox와 outbox를 구분한다.
승인 대기 뒤 재개는 새 event, 현재 상태를 재전송하면 no-op다. 원본 guide가 바뀌면 재검토한다.

요청 guide가 바뀌면 예전 결정·응답을 새 guide에 재사용하지 않는다. 원래 댓글은 보존되지만
현재 진행 상태에서 제외되고 stale 진단이 표시될 수 있다. 새 범위를 읽고 필요한 새 결정을
받아 재개한다. 원본/해석/웹의 갱신은 순차적이다: 공유 Issue → GitHub Actions 집계 →
source-bound 해석 → 선택한 주기의 web 반영. 화면 지연을 권한 문제로 단정하지 않는다.

## 5. 준비 상태와 완료 보고

먼저 tools/doctor.py --workspace /실제/개인/공간 --live-readonly로 진단한다. 연결 도구 설치,
개인 정책 선택, 실제 공유, 요청/응답, Wiki 반영, 자동 실행 관찰을 각각 구분한다.
선택하지 않은 상시 push를 성공으로 표시하거나 첫 공유의 필수 장애로 취급하지 않는다.

M0~M8의 실제 근거를 남기며 passed_local과 passed_live를 나눈다. 계정이 다른 두 역할의
로컬/API fixture 검사는 실제 두 참여자의 승인을 대신하지 않는다. 실제 다른 참여자의 응답은
그 계정이 합류한 뒤에만 검증 완료로 보고한다. 웹에는 공유한 요약·상태·원본 링크만 반영한다.

## 로그인 후 내 Issue 연결

포털 로그인과 참여자 등록은 별도다. 최초 등록 때 실제 GitHub 계정과 본인 Access 세션을
관리자와 확인해 연결하면 이후 본인 Issue가 기본으로 열린다. 이메일·표시 이름으로 다른 사람을
추정하지 않는다. 학생/졸업생은 동료를 선택할 수 있고 교수의 개인 Issue 대상은 목록에서 제외한다.
교수는 본인과 학생 현황을 선택한다. 화면 표시 규칙과 GitHub의 실제 Read 권한은 구분한다.
