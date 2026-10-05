# VICTEX Homepage Renewal

(주)빅텍스 홈페이지(http://www.victex.co.kr) 리뉴얼 저장소입니다.
현행 사이트를 그대로 복제한 버전과, 이를 바탕으로 만든 시안별 리뉴얼 작업본을 함께 관리합니다.

```
.
├── original/        현행 사이트 정적 복제본 (참조용 · 수정 금지)
│   ├── index.html   메인 (fullPage 7개 섹션)
│   ├── s1/ s2/ s3/  서브 페이지 16개
│   ├── bbs/         게시판 스냅샷 (공지·동영상·제품자료·문의 폼)
│   └── css/ js/ fonts/ theme/ data/   원본 에셋 (서버 경로 구조 그대로)
│
├── Renewal_1/       리뉴얼 시안 1 — 1-1안 "2부문 사업 메인 (화이트 블루)"
│   ├── index.html   메인 — 히어로 영역은 "HERO : START ~ END" 주석으로 구분
│   ├── assets/      ★ 리뉴얼 레이어
│   │   ├── css/tokens.css   디자인 변수
│   │   ├── css/hero.css     히어로 스타일
│   │   ├── js/hero.js       소개 영상 레이어
│   │   └── images/hero/     히어로 이미지
│   └── css/ js/ fonts/ theme/   legacy 에셋 (히어로 규칙은 제거됨)
│
├── Renewal_2/       리뉴얼 시안 2 — 2-1안 "EPC 환경/엔지니어링 전문기업 이미지"
│   ├── index.html   구조는 Renewal_1 과 같음 (히어로 블록만 다름)
│   └── assets/      css/tokens.css · css/hero.css · images/hero/ (로고, 플랜트 사진)
│
├── Renewal_4/       리뉴얼 시안 4 — 4안 (Renewal_1 구성 + 실크 물결 배경 · 원본 사진 · CO₂ 아이콘)
│   └── assets/      css/hero.css · js/hero.js · images/hero/ (hero-silk*.svg, 사진, icon-co2.png)
│
├── docs/
│   ├── 01-site-analysis.md       현행 사이트 구조·기술·문제점 분석
│   ├── 02-hero-renewal-brief.md  리뉴얼 전 히어로 사양, 결정 필요 항목, 체크리스트
│   ├── 03-hero-1-1.md            Renewal_1 (1-1안) 적용 내용, 오픈 전 확인 항목
│   ├── 04-hero-2-1.md            Renewal_2 (2-1안) 적용 내용, 오픈 전 확인 항목
│   └── 05-hero-4.md              Renewal_4 (4안) 적용 내용
│
└── tools/
    ├── mirror.py        현행 사이트 → original/ 복제 스크립트
    ├── silk_svg.py      Renewal_4 실크 물결 배경 SVG 생성
    └── screenshots.js   original / Renewal_1 / Renewal_2 / Renewal_4 화면 캡처 비교
```

## 실행

```bash
npm install
npm run dev        # http://localhost:8080 → original / Renewal_1 / Renewal_2 / Renewal_4 선택 화면
```

Node가 없다면 `python3 -m http.server 8080`으로도 열 수 있습니다.
반드시 **저장소 루트**에서 서버를 실행하세요. 각 Renewal 폴더의 서브 페이지 링크가 `../original/`을 가리키기 때문입니다.

## 작업 원칙

1. `original/`은 현행 사이트 기록용이므로 수정하지 않습니다. 다시 받아야 하면 `npm run mirror`를 실행합니다.
2. 리뉴얼은 시안별 폴더(`Renewal_1/`, `Renewal_2/`, `Renewal_4/`)에서 **섹션 단위로** 진행합니다. 새로 만드는 코드는 각 폴더의 `assets/`에 두고, 끝난 섹션의 legacy 규칙은 지웁니다.
3. 섹션을 바꾼 뒤에는 `npm run shots -- --sections`로 다른 섹션이 바뀌지 않았는지 확인합니다.

## 진행 현황

- [x] 현행 사이트 구조 분석 → [docs/01-site-analysis.md](docs/01-site-analysis.md)
- [x] 현행 사이트 복제 (`original/`, 페이지 41개, 원본과 같은 화면 확인)
- [x] 리뉴얼 작업본 생성 (원본과 픽셀 단위로 동일한 상태에서 출발)
- [x] 히어로 리뉴얼 준비 — 코드 분리 + 브리프 → [docs/02-hero-renewal-brief.md](docs/02-hero-renewal-brief.md)
- [x] Renewal_1 — 히어로 1-1안(2부문 사업 메인 · 화이트 블루) → [docs/03-hero-1-1.md](docs/03-hero-1-1.md)
- [x] Renewal_2 — 히어로 2-1안(EPC 환경/엔지니어링 전문기업 이미지) → [docs/04-hero-2-1.md](docs/04-hero-2-1.md)
- [x] Renewal_4 — 히어로 4안(Renewal_1 구성 + 시안 효과) → [docs/05-hero-4.md](docs/05-hero-4.md)
- [ ] 시안 확정 후 오픈 전 확인 (고해상도 사진, 지표 수치, 소개 영상) — 03·04 문서의 확인 항목
