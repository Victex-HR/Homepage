# 01. 현행 홈페이지 구조 분석 — www.victex.co.kr

> 분석 기준일: 2026-10-02 · 대상: http://www.victex.co.kr/ (국문 사이트)
> 영문 사이트(`victex.co.kr/eng`)는 이번 범위에서 제외했습니다.

---

## 1. 한눈에 보기

| 항목 | 내용 |
|---|---|
| 사이트 성격 | 기업 홍보 사이트 — "친환경 TOTAL SOLUTION COMPANY (주)빅텍스" |
| CMS / 서버 | **그누보드5(G5)** 기반 PHP 사이트, Apache, 테마명 `vict` |
| 접속 프로토콜 | **HTTP만 지원** (`https://www.victex.co.kr` 연결 불가) |
| 메인 페이지 방식 | **fullPage.js** 기반 원페이지 스크롤 (섹션 7개, 휠 1회 = 1섹션) |
| 페이지 수 | 정적 콘텐츠 16페이지, 게시판 3개(공지/동영상/제품자료), 문의 폼 1개 |
| 반응형 | 적용됨 — 1600 / 1024 / 640 / 480px에서 크게 바뀜 (§5 참고) |
| 다국어 | 국문 + 영문(별도 사이트 `/eng`) |

---

## 2. 정보 구조(IA) / 사이트맵

GNB는 메뉴 7개이고, PC(>1024px)에서는 마우스를 올리면 전체 2차 메뉴가 메가 드롭다운으로 펼쳐집니다.
우측 상단에는 `ENG` 링크와 사이트맵(9-dot) 버튼이 있습니다.

| 1차 메뉴 | 2차 메뉴 | 3차 메뉴 | 원본 URL | 로컬 복제본 |
|---|---|---|---|---|
| **CCUS/블루수소** | 빅텍스 CCU Solution | | `/s1/s1_3.php` | `original/s1/s1_3.html` |
| | CO₂ Revert Recovery System | | `/s1/s1_2.php` | `original/s1/s1_2.html` |
| **원전해체/원자력산업** | 원전 해체 및 원격로봇 시스템 | | `/s2/s2_4.php` | `original/s2/s2_4.html` |
| | 중이온 가속기 | | `/s2/s2_5.php` | `original/s2/s2_5.html` |
| | 방사능 제염 | | `/s2/s2_6.php` | `original/s2/s2_6.html` |
| **드라이아이스** | 드라이아이스 | | `/s1/s1_6.php` | `original/s1/s1_6.html` |
| **드라이아이스 제조기/세척기** | 드라이아이스너겟제조기 | 드라이아이스너겟제조기 | `/s1/s1_1_1.php` | `original/s1/s1_1_1.html` |
| | | 펠릿제조기 | `/s1/s1_1_2.php` | `original/s1/s1_1_2.html` |
| | 드라이아이스 세척기 | CHALLENGER-AS | `/s1/s1_4_1.php` | `original/s1/s1_4_1.html` |
| | | CHALLENGER-ES | `/s1/s1_4_2.php` | `original/s1/s1_4_2.html` |
| | | CHALLENGER-D | `/s1/s1_4_3.php` | `original/s1/s1_4_3.html` |
| | | CHALLENGER-ASG | `/s1/s1_4_4.php` | `original/s1/s1_4_4.html` |
| | 초임계 CO₂ 스노우젯 세정기 | | `/s1/s1_5.php` | `original/s1/s1_5.html` |
| **COMPANY** | 소개 | | `/s3/s3_1.php` | `original/s3/s3_1.html` |
| | 연혁 | | `/s3/s3_2.php` | `original/s3/s3_2.html` |
| | 오시는길 | | `/s3/s3_3.php` | `original/s3/s3_3.html` |
| **SUPPORT** | 공지사항 (게시판 `s4_1`) | | `/bbs/board.php?bo_table=s4_1` | `original/bbs/s4_1.html` (+ 게시글 `s4_1_<id>.html`) |
| | 제품자료 (게시판 `s4_3`) | | `/bbs/board.php?bo_table=s4_3` | `original/bbs/s4_3.html` |
| | 동영상 (게시판 `s4_2`) | | `/bbs/board.php?bo_table=s4_2` | `original/bbs/s4_2.html` (+ `s4_2_<id>.html`) |
| **CONTACT** | CONTACT (문의 글쓰기 폼) | | `/bbs/write.php?bo_table=s5_1` | `original/bbs/s5_1_write.html` |

**관찰 사항**
- URL 폴더(`s1`, `s2`, `s3`)와 메뉴 구분이 맞지 않습니다. 예를 들어 `s1` 폴더에 CCUS, 드라이아이스, 제조기/세척기 페이지가 섞여 있습니다. 리뉴얼할 때 URL 체계를 다시 잡을지 정해야 합니다.
- 메뉴 라벨에 국문과 영문 대문자가 섞여 있습니다(`CCUS/블루수소` vs `COMPANY`, `SUPPORT`).

---

## 3. 메인 페이지 구성 (`index.html`)

fullPage.js 섹션 7개로 이루어져 있습니다. 섹션마다 `data-anchor`가 있어 `#MAIN`, `#MCNT1` 같은 해시로 이동할 수 있습니다.

| # | anchor | 클래스 | 역할 | 주요 요소 / 라이브러리 |
|---|---|---|---|---|
| 1 | `MAIN` | `.section1 > .mv_sec` | **히어로(메인 비주얼)** | Owl Carousel 페이드 슬라이드 3장, 이전/다음 버튼·점 내비·재생/정지, SCROLL 아이콘 — 상세 내용은 [02-hero-renewal-brief.md](02-hero-renewal-brief.md) |
| 2 | `MCNT1` | `.mcnt1` | VICTEX — 드라이아이스 너겟 제조기 소개 | 좌: 라벨·제목·본문 / 우: YouTube 임베드(`ZYizun2skEA`) |
| 3 | `MCNT2` | `.mcnt2` | PRODUCT — 제품 캐러셀 | Owl Carousel (PC 3개·모바일 2개 노출), 제품 4종(너겟제조기, CO₂ RRS, CCU Solution, 스노우젯), `view more`, 이전/다음 |
| 4 | `MCNT3` | `.mcnt3` | COMPANY — 회사 소개 | 소개 문단 + 대표 이미지, `view more` |
| 5 | `MCNT4` | `.mcnt4` | NEWS — 공지사항 최신글 | Slick 세로 슬라이더(4개 노출), 공지 게시판 최신 10건이 **동적으로 출력**됨 |
| 6 | `MCNT5` | `.mcnt5` | 오시는 길 · 문의 · 납품처 | Google Maps iframe, LOCATION(인천 본사·울산 공장), CONTACT(TEL/FAX), 납품처 로고 15개 |
| 7 | `FOOTER` | `.footer.section7` | 푸터 | 회사 정보, 사업자번호, 주소, 개인정보처리방침·이메일무단수집거부 레이어 팝업, TOP 버튼 |

### 공통 레이아웃 요소
- **Header**: `position: fixed`, 높이 100px(≤480px에서는 80px), 흰 배경, 하단 보더 `#ddd`
  - 로고(`h1.hd_logo`, 배경 이미지 방식), GNB(`#clone_gnb`), ENG, 사이트맵 버튼
- **사이트맵 레이어**: 오른쪽에서 슬라이드되어 나오는 패널. GNB를 jQuery `clone()`으로 복제해서 만듭니다.
- **Quick 버튼**: 우측 하단에 고정된 빨간 원형 `Contact us` 버튼(이미지)
- **TOP 버튼**: 메인에서는 fullPage `moveTo(1)`, 서브에서는 `scrollTop: 0`
- **레이어 팝업**: 개인정보처리방침(textarea), 이메일무단수집거부

### 서브 페이지 공통 템플릿
```
#wrap.sub_wrap
 ├─ .sv_sec.svNN        서브 비주얼 (섹션별 배경 이미지 + 영문 대제목, 예: "COMPANY")
 ├─ location bar        홈 아이콘 / 1차 메뉴 select / 2차 메뉴 select
 ├─ 3차 메뉴 탭          (제조기/세척기 하위 페이지만)
 └─ .sub_layout         본문 (이미지·표·동영상 위주로 구성)
```

---

## 4. 기술 스택

| 구분 | 사용 기술 | 비고 |
|---|---|---|
| CMS | 그누보드5 (`g5_url`, `bbs/board.php`, `PHPSESSID`) | 게시판, 문의 폼, 팝업 레이어 관리 |
| JS 코어 | jQuery **1.11.1** (2014), jQuery UI | 오래된 버전이며 알려진 XSS 취약점이 있음 |
| 풀페이지 | fullPage.js (jQuery 버전) | 메인 전용. `$('#fullpage').fullpage()`가 **두 번 호출**됨 |
| 슬라이더 | Owl Carousel 2 (히어로, PRODUCT), Slick (NEWS) | Swiper, bxSlider도 로드하지만 페이지에서 호출하는 곳은 없음 |
| 애니메이션 | WOW.js + animate.css | `fadeInUp`, `fadeInRight` 등 스크롤 진입 효과 |
| 기타 | counterUp + waypoints 2.0.3, simplyScroll, printThis, modernizr | counterUp, simplyScroll, printThis는 페이지에서 호출하는 곳이 없음 |
| 웹폰트 | Noto Sans KR (Google), Montserrat (GNB), Play (라벨·버튼), Nanum Myeongjo, S-Core Dream(@font-face) | Noto Sans KR을 **3중으로 로드**함 (Google CSS2, earlyaccess, rawgit) |
| CSS 구성 | `common.css` · `layout.css` · `main.css` · `sub.css` · `template.css` · `media.css`(+`media_sub.css`) | 폴더명은 `css/mobile/`이지만 PC·모바일 공용으로 사용 |

메인 페이지 한 번에 **CSS 20개, JS 25개**를 `<head>`에서 불러옵니다(렌더링을 막는 리소스).

---

## 5. 디자인 시스템(현행 값)

> 리뉴얼 작업용 변수로 `Renewal_1/assets/css/tokens.css`(Renewal_2도 동일)에 정리해 두었습니다.

**컬러**
| 용도 | 값 |
|---|---|
| 브랜드 블루 (버튼, 활성 상태, 섹션 라벨) | `#014099` |
| 강조 블루 (본문 하이라이트) | `#115dc7` |
| 로고 레드 / Quick 버튼 | `#e8180c` 계열 |
| 제목 / 본문 / 보더 | `#333` / `#666` / `#ddd` |
| 다크 섹션 | PRODUCT·납품처 섹션은 남색 네트워크 패턴 이미지 배경 |

**타이포그래피** — 메인 섹션 제목 50px(`fz50`), 히어로 제목 60px(`fz60`, 굵기 600), 본문 18px. 자간은 전역 `-0.03em`입니다.

**레이아웃** — `.ct1` 1600px(헤더·푸터), `.ct2` 1500px(본문). 1600px 이하에서는 좌우 20px 여백을 줍니다.

**브레이크포인트** — `2000` / `1600` / `1500` / `1300` / **`1024`**(GNB를 숨기고 모바일 레이아웃으로 전환) / `640` / **`480`**(헤더 80px), 그리고 `max-height: 940px`

---

## 6. 발견된 문제점 · 리뉴얼 시 고려 사항

### 인프라 / 보안
1. **HTTPS 미지원** — 브라우저에 "주의 요함"이 표시되고, 검색 노출과 신뢰도에 불리합니다. 리뉴얼과 함께 SSL 적용을 권장합니다.
2. **jQuery 1.11.1** 등 오래된 라이브러리를 사용하고 있습니다. 보안 패치가 적용되지 않았습니다.
3. 서비스가 종료된 CDN(`cdn.rawgit.com`, 현재 301 리다이렉트)을 참조하고 있고, 서버에 없는 파일 **16개가 404**를 냅니다(slick 폰트, `ajax-loader.gif`, `images/template/*`, `ui_test.js` 등). 복제본에도 똑같이 없습니다.

### SEO / 메타
4. `h1`은 텍스트가 없는 로고 링크이고, 히어로 문구는 `h3`입니다. 그래서 페이지의 핵심 메시지가 문서 구조에 드러나지 않습니다.
5. `canonical` 및 `og:url` 값이 `www.victex.co.kr`로 스킴이 없어 유효하지 않습니다. `og:image`, `keywords`, 네이버 사이트 인증 값은 비어 있습니다.
6. meta description은 "**CCUS의 리더**"인데, 히어로 첫 슬라이드는 "드라이아이스 너겟 제조기"입니다. 회사가 내세우는 메시지가 서로 다릅니다.

### 접근성 / UX
7. 메인 이미지 **30개에 `alt`가 없습니다**. 링크 다수가 `href="#n"`입니다.
8. 히어로 자동재생은 꺼져 있는데(`autoplay:false`) 화면에는 **"일시정지(II)" 아이콘**이 보입니다. 재생 중인 것처럼 표시되는 상태 오류입니다.
9. 히어로·섹션 텍스트에 비표준 태그(`<text_wrap>`, `<text_box>`)를 사용합니다.
10. `prefers-reduced-motion`(움직임 줄이기 설정)에 대응하지 않습니다. Ken Burns 확대 효과(6초)와 fullPage 강제 스크롤이 항상 동작합니다.
11. 푸터 저작권 표기 연도가 2023입니다.

### 성능
12. 히어로 이미지 3장(각 380~480KB JPG)을 CSS 배경으로 넣어 preload, WebP/AVIF, 반응형 소스를 쓸 수 없습니다. 이 이미지가 LCP 요소인데도 우선 로딩이 되지 않습니다.
13. 서브 페이지에 20MB짜리 MP4(`s24_video.mp4`)를 직접 넣었습니다.

---

## 7. 복제본(`original/`) 생성 방법과 검증 결과

- `tools/mirror.py`로 페이지 41개와 에셋(CSS/JS/이미지/폰트/동영상)을 내려받았습니다. 전체 파일 464개, 약 54MB입니다.
- 링크는 모두 로컬 상대경로로 바꿔서 웹서버 루트 위치와 관계없이 동작합니다.
- 서버에서만 처리되는 기능(문의 폼 전송, 게시판 검색·페이지 이동, 첨부 다운로드)은 원본 사이트(`http://www.victex.co.kr/...`)로 연결되도록 남겨 두었습니다.
- **검증**: Playwright(Chromium)로 원본 사이트와 복제본을 같은 해상도에서 캡처해 비교했고, 메인 히어로·PRODUCT·NEWS·LOCATION·서브(COMPANY)·모바일(390px) 화면이 같게 렌더링되는 것을 확인했습니다.
- 복제본을 다시 만들려면 `python3 tools/mirror.py`를 실행합니다(이미 받은 파일은 건너뜁니다).
