# 개인 연구와 공동 코드의 GitHub 운영

평소에는 개인 저장소에서 본인 agent와 연구하고, 공유할 결과와 요청만 Issue 문서로 전달한다.
Wiki/dashboard는 그 공유 입력의 파생물이다. 개인 연구 결과 공유에는 PR이 필요 없다.
아래 fork/PR 절차는 공동 코드·템플릿·규약 자체를 변경할 때 적용한다.

GitHub의 부여 가능한 기본 역할은 Read, Triage, Write, Maintain, Admin이다.
Contributor는 기여자를 설명하는 말이며 별도의 기본 부여 역할이 아니다.

| 역할 | 권장 권한 | 업무 |
|---|---|---|
| 일반 연구 참여자 | Read | 자기 공유 Issue·요청·댓글, 개인 저장소 연구 |
| 공동 코드 기여자 | 프로젝트별 승인 | 허용된 fork/branch에서 공동 코드 변경·PR |
| 검토자 | Write 이상 | required review의 유효한 검토, 코드 소유 범위 검토 |
| 프로젝트 maintainer | Write/Maintain | PR 통합과 release, 프로젝트 상태 수용 |
| 조직 관리자 | Admin/Owner | 계정·접근·조직 정책 |
| portal bot | 원본 Read + 포털 생성물 Write | 집계·링크 검증·생성물 갱신 |

Read/Triage 참여자의 의견도 유용하지만 GitHub required approval로 집계되는 검토자 권한은
별도 확인한다. Write를 부여하면 repository 전체 쓰기 권한이 생기므로 다른 학생의 개인
repository 격리와 같은 방식으로 취급하지 않는다. main은 PR과 필수 check, 독립 승인으로
보호하고 관리자 bypass 범위를 검토한다. 이 시안은 원격 권한·ruleset을 변경하지 않는다.

## 첫 PR 예시

아래 URL은 예시이므로 LOCAL.md의 실제 승인 URL로 바꾼다.

```sh
git clone https://github.com/MY-ACCOUNT/PROJECT.git
cd PROJECT
git remote add upstream https://github.com/LAB-ORG/PROJECT.git
git fetch upstream
git switch -c work/short-purpose upstream/main
# 필요한 수정과 프로젝트 문서의 검증 수행
git add FILES-REVIEWED-BY-YOU
git commit -m "Explain the resulting change"
git push -u origin work/short-purpose
```

PR base는 LAB-ORG/PROJECT의 main, head는 내 fork branch. 대용량 NAS 자산의 버전·checksum,
재현 명령과 검증을 PR에 연결한다. maintainer가 검토·merge하고 결과 기록에 merge commit을
연결한다. main 이름이 다르면 실제 default branch를 사용한다. 초기 clone/설치도
사용자의 작업 범위와 계정 정책에 맞춰 수행한다.

private fork는 조직·계정 정책에 따라 허용되지 않을 수 있다. 사용 가능 여부를 확인하고,
대안은 승인된 기관 내 fork 또는 공용 repo의 작업 branch다. private fork는 독립적인
개인 비공개 메모 공간이 아니다. 원본 접근 종료 때 fork가 영향을 받을 수 있다.

## 비용과 검토 부담

모든 메모를 maintainer PR에 몰아넣지 않는다. 개인 기록은 본인 공간에서 관리하고,
공동 원본 변경·결론 채택·공동 결과물은 PR로 통합한다. 정형식·링크 검증은 프로그램,
설명·맥락 정리는 LLM, 연구 판단과 채택은 사람/책임자에게 배정한다.

## 공식 근거 (2026-11-10 확인)

- https://docs.github.com/en/organizations/managing-user-access-to-your-organizations-repositories/managing-repository-roles/repository-roles-for-an-organization
- https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/about-forks
