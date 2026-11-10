# 공동 프로젝트 설정

- template_version: 0.1
- owner_id: {{owner}}
- workspace_kind: project
- upstream: 운영 전 실제 공용 repository URL 입력
- default_visibility: project
- maintainers: 실제 검토·merge 담당자 입력
- delegated_scope: fork에서 구현·검증·PR 초안. merge는 권한과 승인된 정책에 따름.
- nas_root: 프로젝트 ACL 확인 후 입력

일반 참여자는 Read 또는 Triage + fork/PR. required review를 담당할 검토자는 GitHub에서
유효한 Write 이상 권한을 가져야 한다. main은 PR·독립 검토·필수 check로 유지한다.
