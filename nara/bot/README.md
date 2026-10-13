# NARA · 나라장터 입찰공고 자동 조회

홈페이지 저장소의 `nara/` 폴더입니다. 화면은 `nara/index.html`, `nara/admin/`, 수집·발송 코드는 `nara/bot/` 에 있습니다.

- **공개 화면**: `https://victex-hr.github.io/Homepage/nara/`. 로그인 없이 열립니다.
  기본은 가장 최근 공고일의 공고를 최신순으로 보여주고, 공고일 기간(갱신일·7일·30일·전체·직접 지정)으로 찾을 수 있습니다.
  '엑셀 다운로드'는 지금 보이는 검색·필터 결과를 그대로 받고, '갱신'은 가장 최근 수집 결과를 다시 불러옵니다.
- **관리 화면**: `https://victex-hr.github.io/Homepage/nara/admin/`. 별도로 로그인하며, 추천 기준(키워드·제외 키워드·발주처), 가입자 승인, 발송 일정, 메일 수신자를 관리합니다.
- **엑셀 메일**: 정한 요일·시각(한국시간)에 **전날 공고** 엑셀을 수신자에게 보냅니다.
  엑셀은 추천 공고, 진행 중 추천 전체, 전체 공고 세 개 시트로 되어 있습니다.

## 동작 방식
GitHub Actions(저장소 루트 `.github/workflows/nara.yml`)가 매시간 `nara/bot` 에서 `python nara.py tick` 을 실행합니다.
1. 하루 한 번(그날 첫 실행) 사흘 전~어제 공고를 다시 받아 늦게 올라온 공고를 채우고, 오늘 공고는 15분마다 새 공고를 덧붙이고 2시간마다 전체를 다시 받습니다 (최근 60일 보관).
2. Supabase에 저장된 발송 일정 중 시각이 된 것이 있으면 엑셀을 만들어 메일로 보내고, 결과를 발송 기록에 남깁니다.
   예정 시각부터 3시간 안에 실행되면 보냅니다. 하루에 한 번만 보냅니다.
3. 공고 데이터는 `nara-data` 브랜치에 덮어써서 올립니다. 홈페이지 이력에 데이터가 쌓이지 않고, 화면은 이 브랜치에서 데이터를 읽습니다.

추천 기준(키워드 그룹·발주처·제외어 등)은 관리 화면 '추천 기준' 탭에서 고칩니다(Supabase `settings` 표). Supabase 를 설정하기 전에는 `nara/bot/config.json` 을 씁니다. 기준을 바꾸면 다음 자동 실행 때 수집 없이 점수만 다시 매겨 공개 화면에 반영합니다. 형식과 점수 규칙은 아래와 같습니다.
- 키워드는 대소문자를 무시합니다. `^` 로 시작하면 단어 첫머리에서만 일치합니다(`^고리`). 4자 이하 영문 약어는 앞뒤가 영문자가 아닐 때만 일치합니다.
- 그룹별로 공고명에 있으면 30점, 키워드가 더 있으면 하나에 10점씩 최대 20점을 더합니다. 투찰가능업종에만 있으면 10점, 발주처가 일치하면 20점입니다.

## 처음 설정 순서
1. **Supabase**: 프로젝트를 만든 뒤 SQL Editor 에 `nara/bot/schema.sql` 을 붙여넣고 Run 합니다.
   Authentication > URL Configuration 의 Site URL 에 `https://victex-hr.github.io/Homepage/nara/admin/` 을 넣습니다.
2. **GitHub 저장소 Settings > Secrets and variables > Actions**
   - Variables: `SUPABASE_URL`, `SUPABASE_ANON_KEY` (Supabase > Project Settings > API 의 URL 과 anon public 키)
   - Secrets: `SUPABASE_SERVICE_KEY` (같은 화면의 service_role 키), `NARA_API_KEY`,
     `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `MAIL_FROM`
     - Gmail 예: `smtp.gmail.com` / `465` / 계정 주소 / 앱 비밀번호 / 계정 주소
3. Actions 탭에서 `NARA 입찰공고 수집·메일 발송` 을 한 번 수동 실행(Run workflow)합니다.
4. 관리 화면에서 **가장 먼저 가입한 사람이 관리자**가 됩니다. 이후 가입자는 관리자가 '가입자' 탭에서 승인합니다.

## 갱신 버튼으로 실시간 조회 (선택)
공개 페이지의 '갱신'을 누르면 Supabase Edge Function `nara-live` 가 마지막 수집 이후부터 지금까지의 오늘 공고를
나라장터에서 바로 받아 화면에 합칩니다. 인증키는 함수 비밀값에만 있고 브라우저로 나가지 않습니다.
설정하지 않으면 '갱신'은 마지막 자동 수집 결과(15분마다)를 다시 불러옵니다.

1. Supabase > Edge Functions > **Deploy a new function** > Via Editor 에서 이름을 `nara-live` 로 하고,
   `nara/bot/supabase/functions/nara-live/index.ts` 내용을 붙여넣어 Deploy 합니다.
   (CLI 를 쓰면 `nara/bot` 에서 `supabase functions deploy nara-live`)
2. Edge Functions > **Secrets** 에 `NARA_API_KEY` 를 추가합니다 (GitHub Secrets 에 넣은 것과 같은 키).
3. 위 2단계의 `SUPABASE_URL`, `SUPABASE_ANON_KEY` 가 들어가 있으면 다음 자동 수집 때부터 페이지가 함수를 찾습니다.

같은 시간대는 3분 동안 다시 조회하지 않아 여러 사람이 연달아 눌러도 API 호출 한도를 크게 쓰지 않습니다.

## Supabase 없이 메일만 먼저 받기
관리 화면을 설정하기 전에도 저장소 Variables 에 `MAIL_TO`(쉼표로 여러 주소)와 `MAIL_TIME`(예: `00:00`, 비우면 자정)을
넣으면 매일 그 시각에 보냅니다. Supabase 를 설정하면 관리 화면의 일정과 수신자가 대신 쓰입니다.

## 메일 발송 계정
- **Gmail**: 2단계 인증을 켠 뒤 Google 계정 > 보안 > 앱 비밀번호에서 16자리 비밀번호를 만들어 `SMTP_PASSWORD` 에 넣습니다.
  `SMTP_HOST=smtp.gmail.com`, `SMTP_PORT=465`. 하루 발송 한도는 약 500통입니다.
- **회사 메일**: 메일 서버의 SMTP 주소·포트(465 SSL 또는 587 STARTTLS)·계정·비밀번호를 넣습니다.
  해외(GitHub 서버)에서 로그인하는 것을 막는 메일 서비스는 해외 접속 허용이 필요합니다.
- 보내는 주소(`MAIL_FROM`)는 로그인 계정과 같은 주소로 두는 것이 스팸 분류를 피하기 좋습니다.

## 수동 실행
```
cd nara/bot
pip install openpyxl
python nara.py update-site --days-back 3   # 공고 수집 + nara/data 갱신
python nara.py excel --date 20261012       # out/ 에 엑셀 생성
python nara.py send-test --to a@b.com      # 어제 엑셀 시험 발송
```

## 참고
- 데이터: 조달청 나라장터 공공데이터개방표준서비스 `getDataSetOpnStdBidPblancInfo` (data.go.kr 15058815).
- 한 번에 많이 받으면 페이지가 밀려 공고가 빠지고 연결도 자주 끊겨서, 1시간 단위로 나눠 100건씩 받고 빠지면 다시 받습니다.
- 공개 화면은 주소를 아는 누구나 볼 수 있으므로 `config.json` 의 키워드와 발주처도 공개됩니다.
- 가입자를 삭제하면 관리 화면에 들어올 수 없게 됩니다. 로그인 계정 자체는 Supabase > Authentication 에서 지울 수 있습니다.
