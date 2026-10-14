# T07 Plan Do See 작업 일지

T06의 기존 다이어리에 공개 ChatGPT 로그인과 서버의 계정별 자료 보호를 붙인 전체 소스다.

공개 앱: https://t06-manor-diary.gkacksdnjs22.chatgpt.site/

- 소유자 계정은 기존 게임 일지, 다른 계정은 일반적인 내 작업 일지를 사용한다.
- 계획·할 일·실제 작업·돌아보기·계획 이력·완료 이력을 사용자별로 조회한다.
- 비로그인 첫 화면은 로그인 화면으로 이동한다. 내 계정에서 자기 자료만 JSON으로 내보낸다.
- 기존 정적 설계 이미지는 공개 자산이며 로그인 자료 보호와 구분한다.

## 문서와 근거

- [인증 구현 설명서](T07_인증구현설명서.md): 공개 ChatGPT 로그인 방식과 별도 로컬 비밀번호 시험의 구분, 여섯 항목과 한계.
- [5일 기록·완료율·규칙 변경](T07_관찰결과.md): 사후 복원 집계와 원래 대화 시각, 손계산 대조.
- `tests/hosted-ownership-results.json`: 별도 로컬 Worker의 합성 계정 권한 검사 7개 PASS.
- `tests/auth-results.json`: 별도 로컬 비밀번호 인증 검사 12개 PASS.
- `tests/branding-results.json`: 소유자·다른 계정·비로그인 제목 검사.

## 로컬 실행

Node.js 22.13 이상에서 `npm ci`, `npm run build`를 실행한다. 기존 마이그레이션을 새로 생성하지 않는다. `STARTER_RUNTIME.md`의 안내에 따라 `drizzle/*.sql`을 번호순으로 새 로컬 D1에 적용한 뒤 `npm run dev -- --port 5187`을 실행한다. 원본 자료가 있는 DB에 적용된 마이그레이션을 다시 실행하지 않는다.

공개 환경은 Sites가 제공하는 `DB` 바인딩, `DIARY_HOSTED_AUTH=chatgpt`, 비밀 설정 `DIARY_OWNER_EMAIL`을 사용한다. 실제 설정값·쿠키·토큰은 소스에 넣지 않는다. 로컬 기본 모드는 자체 비밀번호 시험이며 공개 인증 방식과 다르다.
