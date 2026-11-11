# 연구실 소유 저장소와 담당자 권한

연구실 연구 자산은 nii-lab 조직에 두고, 각 참여자는 독립된 개인 연구 저장소에서 기록한다.
개인의 agent 승인·자동 실행 정책은 본인이 정하며 GitHub 권한과 별도로 유지한다.

| 대상 | 기본 설정 |
|---|---|
| 신규 개인·공동 연구 저장소 | nii-lab 소유, Private |
| 교수/연구실 소유자 | Admin / 조직 Owner |
| 해당 저장소 담당자 | Write |
| 나머지 조직 멤버 | Read |
| 공동 코드·규약 수정 | fork 또는 승인 branch → PR → 검토·check → merge |
| 개인 연구 기록 | 담당자가 자기 독립 저장소에 직접 commit/push |

공개 공통 매뉴얼과 이미 공개 승인한 자료는 별도 공개 저장소다. 일반 연구 저장소를 자동으로
공개하지 않는다. Private은 연구실 밖 비공개다. 조직 멤버에게 숨길 초안·개인 정책·자격증명은
ignored 로컬 공간에 두며 personal 파일 표시는 GitHub의 Read 권한을 차단하지 않는다.
포털/Wiki는 개인 원본을 순회하지 않고 공유 승인한 Issue만 요약한다.

## 새 참여자와 담당자 연결

1. 로컬 starter와 첫 기록은 초대 없이 준비할 수 있다.
2. 실제 GitHub login·참여할 프로젝트·담당 저장소를 관리자에게 연결한다.
3. 관리자가 nii-lab 아래 Private 독립 저장소(예: member-GITHUB-LOGIN)를 생성하고 담당자에게
   Write를 부여한다. 없는 계정을 추정해 초대하지 않는다. 교수는 Admin을 유지한다.
4. 실제 멤버십/Read·담당 repo Write를 확인하고 registry의 personal_repository를 연결한다.
   기록 owner_id는 조직명 대신 본인의 실제 GitHub login을 유지한다.
5. agent 정책의 repository 주소는 실제 대상만 등록하며 행동·발신자·실행 주기는 본인이 정한다.

관리자는 새 저장소를 생성할 때 반드시 Private을 명시한다. 담당자 배정이 확정된 후에만
해당 계정/팀에 Write를 부여한다. Read 참여자가 다른 사람의 저장소를 직접 수정하지는 않는다.
개인 연구 정본은 다른 공동 repo의 fork가 아닌 독립 repo로 생성한다.

## 기존 저장소 이관

관리자가 원래 저장소의 ID·HEAD·비공개 여부와 실제 권한을 확인한 뒤 nii-lab으로 transfer한다.
이관 뒤 같은 ID·commit 이력, 새 주소의 실제 접근과 권한을 확인한다. 기존 로컬 변경은 보존한다.

- 로컬 origin을 새 GitHub 주소로 변경한다.
- LOCAL/current·참여자 registry·포털 개인 연결을 새 주소로 바꾼다.
- 본인의 로컬 정책에 옛 주소가 있으면 같은 자산의 새 주소로만 바꾸고 자동 행동은 확대하지 않는다.
- 고정 버전 client/registry 캐시는 공식 installer로 갱신한다. 예전 snapshot을 수동 변조하지 않는다.
- 새 공유 기록은 새 repo 주소와 immutable commit을 source로 사용한다. 이전 원본 commit과
  과거 URL은 증거로 보존하며 GitHub redirect가 실제 접근되는지 확인한다.

## 공동 저장소의 fork와 PR

조직과 공동 repo가 private fork를 허용해야 한다. Read 참여자도 허용된 fork에서 branch를 만들고
원본에 PR을 보낼 수 있다. Private fork는 계속 Private이며 team 권한을 상속하므로 개인 독점 공간이 아니다.
개인 계정 fork와 nii-lab의 독립 개인 연구 repo는 용도가 다르다.

Fork PR의 Actions는 담당자의 실행 승인 후 read-only token으로 검증하며 쓰기 token/secrets/variables를
전달하지 않는다. check 통과 뒤 실제 merge 권한을 가진 담당자가 통합한다. 실행 승인과 코드 수용은 별개다.
본인에게 fork/Write/merge 권한이 없으면 가능한 것으로 보고하지 않고 필요한 범위를 관리자에게 연결한다.

- [GitHub fork와 권한](https://docs.github.com/en/pull-requests/reference/forks)
- [조직 기본 권한](https://docs.github.com/en/organizations/managing-user-access-to-your-organizations-repositories/managing-repository-roles/setting-base-permissions-for-an-organization)
