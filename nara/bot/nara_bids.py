#!/usr/bin/env python3
"""나라장터 입찰공고 일일 수집 · 누적 · 정리 · 추천.

조달청 '나라장터 공공데이터개방표준서비스' getDataSetOpnStdBidPblancInfo 를 사용한다.
표준 라이브러리만 사용 (설치 불필요).

사용법
  export NARA_API_KEY='공공데이터포털 일반 인증키(Decoding)'
  python3 nara_bids.py collect                  # 어제 공고 수집 후 DB 누적
  python3 nara_bids.py collect --date 20261007  # 특정 날짜
  python3 nara_bids.py report  --date 20261007  # 일일 정리 + 추천 리포트 생성
  python3 nara_bids.py daily                    # collect + report (매일 실행용)
  python3 nara_bids.py build-web                # 웹 화면용 데이터 갱신
  python3 nara_bids.py serve                    # http://localhost:8000 에서 웹 화면 보기
  python3 nara_bids.py load-sample FILE.json    # API 없이 샘플 JSON 적재(테스트용)
"""
import argparse
import csv
import datetime as dt
import json
import os
import sqlite3
import sys
import time
import urllib.parse
import urllib.request

BASE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE, "data", "bids.sqlite")
REPORT_DIR = os.path.join(BASE, "reports")
CONFIG_PATH = os.path.join(BASE, "config.json")
API_URL = ("https://apis.data.go.kr/1230000/ao/PubDataOpnStdService/"
           "getDataSetOpnStdBidPblancInfo")
PAGE_SIZE = 100  # 500건씩 받으면 응답이 느려 중간 프록시에서 끊김

FIELDS = [
    "bidNtceNo", "bidNtceOrd", "refNtceNo", "refNtceOrd", "ppsNtceYn", "bidNtceNm",
    "bidNtceSttusNm", "bidNtceDate", "bidNtceBgn", "bsnsDivNm", "intrntnlBidYn",
    "cmmnCntrctYn", "cmmnReciptMethdNm", "elctrnBidYn", "cntrctCnclsSttusNm",
    "cntrctCnclsMthdNm", "bidwinrDcsnMthdNm", "ntceInsttNm", "ntceInsttCd",
    "ntceInsttOfclDeptNm", "ntceInsttOfclNm", "ntceInsttOfclTel",
    "ntceInsttOfclEmailAdrs", "dmndInsttNm", "dmndInsttCd", "dmndInsttOfclDeptNm",
    "dmndInsttOfclNm", "dmndInsttOfclTel", "dmndInsttOfclEmailAdrs",
    "presnatnOprtnYn", "presnatnOprtnDate", "presnatnOprtnTm", "presnatnOprtnPlce",
    "bidPrtcptQlfctRgstClseDate", "bidPrtcptQlfctRgstClseTm",
    "cmmnReciptAgrmntClseDate", "cmmnReciptAgrmntClseTm", "bidBeginDate",
    "bidBeginTm", "bidClseDate", "bidClseTm", "opengDate", "opengTm", "opengPlce",
    "asignBdgtAmt", "presmptPrce", "rsrvtnPrceDcsnMthdNm", "rgnLmtYn",
    "prtcptPsblRgnNm", "indstrytyLmtYn", "bidprcPsblIndstrytyNm", "bidNtceUrl",
    "dataBssDate",
]


# ---------------------------------------------------------------- 저장소
def db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    cols = ", ".join(f'"{f}" TEXT' for f in FIELDS)
    con.execute(f"""CREATE TABLE IF NOT EXISTS bids ({cols},
        first_seen TEXT, last_seen TEXT,
        PRIMARY KEY (bidNtceNo, bidNtceOrd))""")
    con.execute("CREATE INDEX IF NOT EXISTS ix_date ON bids(bidNtceDate)")
    return con


def upsert(con, items, seen_at):
    new = 0
    for it in items:
        row = {f: ("" if it.get(f) is None else str(it.get(f))) for f in FIELDS}
        if not row["bidNtceNo"]:
            continue
        exists = con.execute("SELECT 1 FROM bids WHERE bidNtceNo=? AND bidNtceOrd=?",
                             (row["bidNtceNo"], row["bidNtceOrd"])).fetchone()
        new += 0 if exists else 1
        cols = FIELDS + ["first_seen", "last_seen"]
        ph = ", ".join("?" for _ in cols)
        upd = ", ".join(f'"{f}"=excluded."{f}"' for f in FIELDS + ["last_seen"])
        con.execute(
            f'INSERT INTO bids ({", ".join(chr(34)+c+chr(34) for c in cols)}) VALUES ({ph}) '
            f"ON CONFLICT(bidNtceNo, bidNtceOrd) DO UPDATE SET {upd}",
            [row[f] for f in FIELDS] + [seen_at, seen_at])
    con.commit()
    return new


# ---------------------------------------------------------------- 수집
def fetch_page(key, begin, end, page):
    q = urllib.parse.urlencode({
        "ServiceKey": key, "numOfRows": PAGE_SIZE, "pageNo": page, "type": "json",
        "bidNtceBgnDt": begin, "bidNtceEndDt": end})
    # 연결이 수십 초~수 분씩 끊기는 때가 있어 최대 60초 간격으로 여러 번 재시도
    for attempt in range(12):
        try:
            with urllib.request.urlopen(f"{API_URL}?{q}", timeout=30) as r:
                raw = r.read().decode("utf-8")
            data = json.loads(raw)
            break
        except (OSError, ValueError) as e:
            if attempt == 11:
                raise SystemExit(f"API 호출 실패: {e}")
            time.sleep(min(60, 2 ** (attempt + 1)))
    resp = data.get("response", data)
    hdr = resp.get("header", {})
    if str(hdr.get("resultCode", "00")) not in ("00", "0"):
        raise SystemExit(f"API 오류 {hdr.get('resultCode')}: {hdr.get('resultMsg')}")
    body = resp.get("body", {})
    items = body.get("items") or []
    if isinstance(items, dict):
        items = items.get("item", [])
    if isinstance(items, dict):
        items = [items]
    return items, int(body.get("totalCount") or 0)


def fetch_window(key, begin, end):
    """한 시간대 공고를 모두 받는다. 페이지 순서가 조회마다 달라 일부가 빠질 수 있어,
    공고번호+차수 기준 고유 건수가 전체 건수에 못 미치면 다시 조회해 합친다."""
    got, total = {}, 0
    for _ in range(4):
        items, total = fetch_page(key, begin, end, 1)
        for p in range(2, (total + PAGE_SIZE - 1) // PAGE_SIZE + 1):
            more, _ = fetch_page(key, begin, end, p)
            items.extend(more)
            time.sleep(0.3)
        for it in items:
            got[(it.get("bidNtceNo"), it.get("bidNtceOrd"))] = it
        if len(got) >= total:
            break
    return list(got.values()), total


def collect(day):
    key = os.environ.get("NARA_API_KEY")
    if not key:
        raise SystemExit("NARA_API_KEY 환경변수에 공공데이터포털 인증키를 넣어주세요.")
    # 하루를 1시간 단위로 나눠 조회 (한 번에 받으면 페이지가 밀려 누락이 생김)
    items, total = [], 0
    for h in range(24):
        got, n = fetch_window(key, f"{day}{h:02d}00", f"{day}{h:02d}59")
        items.extend(got)
        total += n
    con = db()
    new = upsert(con, items, dt.datetime.now().isoformat(timespec="seconds"))
    print(f"[{day}] 조회 {len(items)}건 / 전체 {total}건 / 신규 저장 {new}건")
    return len(items)


# ---------------------------------------------------------------- 추천
def to_int(s):
    try:
        return int(float(s))
    except (TypeError, ValueError):
        return 0


def keyword_groups(cfg):
    """config 의 keyword_groups (없으면 예전 keywords 형식) 를 [{name, keywords}] 로."""
    if cfg.get("keyword_groups"):
        return cfg["keyword_groups"]
    kw = cfg.get("keywords", {})
    return [{"name": k, "keywords": v} for k, v in kw.items() if v]


def org_norm(s):
    return s.replace(" ", "").replace("재단법인", "").replace("(재)", "").replace("(주)", "")


def kw_hit(k, text):
    """키워드 포함 여부. 대소문자 무시. '^' 로 시작하면 단어 첫머리에서만 일치.
    짧은 영문 약어(4자 이하)는 앞뒤가 영문자가 아닐 때만 일치 (PWR, CCU, CO2 등)."""
    if not k or not text:
        return False
    head = k.startswith("^")
    kl, low = k.lstrip("^").lower(), text.lower()
    short_ascii = kl.isascii() and len(kl) <= 4
    i = low.find(kl)
    while i >= 0:
        before = low[i - 1] if i > 0 else ""
        after = low[i + len(kl)] if i + len(kl) < len(low) else ""
        ok = not (head and before.isalnum())
        if kl.isascii() and before.isascii() and before.isalpha():
            ok = False
        if short_ascii and after.isascii() and after.isalpha():
            ok = False
        if ok:
            return True
        i = low.find(kl, i + 1)
    return False


def score(b, cfg, today):
    """(점수, 사유 목록) 반환. 점수 None 이면 제외."""
    name = b["bidNtceNm"] or ""
    inds = b["bidprcPsblIndstrytyNm"] or ""
    reasons = []

    if any(x and x in name for x in cfg.get("exclude_keywords", [])):
        return None, ["제외 키워드"]
    types = cfg.get("business_types") or []
    if types and b["bsnsDivNm"] not in types:
        return None, ["업무구분 불일치"]
    if "취소" in (b["bidNtceSttusNm"] or ""):
        return None, ["취소공고"]

    close = b["bidClseDate"]
    if close:
        try:
            left = (dt.date.fromisoformat(close) - today).days
        except ValueError:
            left = None
        if left is not None and left < cfg.get("min_days_to_deadline", 0):
            return None, ["마감 임박/지남"]

    budget = to_int(b["asignBdgtAmt"]) or to_int(b["presmptPrce"])
    lo, hi = cfg.get("min_budget", 0), cfg.get("max_budget", 0)
    if lo and budget and budget < lo:
        return None, ["예산 미달"]
    if hi and budget and budget > hi:
        return None, ["예산 초과"]

    regions = cfg.get("regions") or []
    if b["rgnLmtYn"] == "Y" and regions:
        rg = b["prtcptPsblRgnNm"] or ""
        if rg and "이하생략" not in rg and not any(r in rg for r in regions if r != "전국"):
            return None, ["지역제한 불일치"]

    s = 0
    for g in keyword_groups(cfg):
        hits = [k for k in g["keywords"] if kw_hit(k, name)]
        if hits:
            s += 30 + 10 * min(len(hits) - 1, 2)
            reasons.append(f"{g['name']}: " + ", ".join(k.lstrip("^") for k in hits[:4]))
        elif any(kw_hit(k, inds) for k in g["keywords"]):
            s += 10
            reasons.append(f"{g['name']}: 투찰가능업종")
    insts = org_norm(f"{b['ntceInsttNm'] or ''}|{b['dmndInsttNm'] or ''}")
    ag = [a for a in cfg.get("agencies", []) if a and org_norm(a) in insts]
    if ag:
        s += 20
        reasons.append("발주처: " + ag[0])
    if s == 0:
        return None, ["키워드 없음"]

    allowed = cfg.get("allowed_industries") or []
    if b["indstrytyLmtYn"] == "Y":
        if allowed and any(a in inds for a in allowed):
            s += 10; reasons.append("보유 업종으로 투찰 가능")
        elif allowed and inds:
            return None, ["업종제한 불일치"]
        else:
            reasons.append("업종제한 있음(확인 필요)")
    if b["rgnLmtYn"] == "Y":
        reasons.append("지역제한 있음")
    return s, reasons


def won(n):
    n = to_int(n)
    if not n:
        return "-"
    return f"{n/1e8:,.1f}억원" if n >= 1e8 else f"{n/1e4:,.0f}만원"


def report(day):
    cfg = json.load(open(CONFIG_PATH, encoding="utf-8"))
    con = db()
    con.row_factory = sqlite3.Row
    iso = f"{day[:4]}-{day[4:6]}-{day[6:]}"
    rows = [dict(r) for r in con.execute(
        "SELECT * FROM bids WHERE bidNtceDate=? ORDER BY bidNtceBgn", (iso,))]
    today = dt.date.fromisoformat(iso)
    total_db = con.execute("SELECT COUNT(*) FROM bids").fetchone()[0]

    by_type = {}
    for r in rows:
        by_type[r["bsnsDivNm"] or "기타"] = by_type.get(r["bsnsDivNm"] or "기타", 0) + 1

    recs = []
    for r in rows:
        s, why = score(r, cfg, today)
        if s is not None:
            recs.append((s, why, r))
    recs.sort(key=lambda x: (-x[0], x[2]["bidClseDate"] or "9999"))
    top = recs[: cfg.get("top_n", 10)]

    os.makedirs(REPORT_DIR, exist_ok=True)
    csv_path = os.path.join(REPORT_DIR, f"{day}_공고목록.csv")
    with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["추천점수", "공고번호", "차수", "공고명", "업무구분", "공고기관", "수요기관",
                    "계약방법", "낙찰방법", "배정예산", "추정가격", "입찰마감", "개찰",
                    "지역제한", "참가가능지역", "업종제한", "투찰가능업종", "공고URL"])
        scored = {id(r): s for s, _, r in recs}
        for r in sorted(rows, key=lambda r: -scored.get(id(r), -1)):
            w.writerow([scored.get(id(r), ""), r["bidNtceNo"], r["bidNtceOrd"], r["bidNtceNm"],
                        r["bsnsDivNm"], r["ntceInsttNm"], r["dmndInsttNm"],
                        r["cntrctCnclsMthdNm"], r["bidwinrDcsnMthdNm"],
                        r["asignBdgtAmt"], r["presmptPrce"],
                        f'{r["bidClseDate"]} {r["bidClseTm"]}', f'{r["opengDate"]} {r["opengTm"]}',
                        r["rgnLmtYn"], r["prtcptPsblRgnNm"], r["indstrytyLmtYn"],
                        r["bidprcPsblIndstrytyNm"], r["bidNtceUrl"]])

    L = [f"# 나라장터 입찰공고 일일 정리 · {iso}", "",
         f"- 대상 회사: {cfg.get('company_name')}",
         f"- 이날 공고: **{len(rows)}건** ({', '.join(f'{k} {v}' for k, v in sorted(by_type.items()))})",
         f"- 기준 통과(추천 후보): **{len(recs)}건**, 상위 {len(top)}건 아래 정리",
         f"- 누적 DB: {total_db:,}건 · 전체 목록: `{os.path.basename(csv_path)}`", "",
         "## 추천 입찰공고", ""]
    if not top:
        L.append("오늘은 기준에 맞는 공고가 없습니다.")
    for i, (s, why, r) in enumerate(top, 1):
        L += [f"### {i}. {r['bidNtceNm']}  (점수 {s})",
              f"- {r['bsnsDivNm']} · {r['ntceInsttNm']}"
              + (f" (수요: {r['dmndInsttNm']})" if r['dmndInsttNm'] and r['dmndInsttNm'] != r['ntceInsttNm'] else ""),
              f"- 예산 {won(r['asignBdgtAmt'])} / 추정가격 {won(r['presmptPrce'])} · "
              f"{r['cntrctCnclsMthdNm']} · {r['bidwinrDcsnMthdNm']}",
              f"- 입찰마감 **{r['bidClseDate']} {r['bidClseTm']}** · 개찰 {r['opengDate']} {r['opengTm']}"
              + (f" · 참가등록마감 {r['bidPrtcptQlfctRgstClseDate']} {r['bidPrtcptQlfctRgstClseTm']}"
                 if r['bidPrtcptQlfctRgstClseDate'] else ""),
              f"- 추천 사유: {', '.join(why)}",
              f"- [나라장터 공고 보기]({r['bidNtceUrl']})", ""]
    md_path = os.path.join(REPORT_DIR, f"{day}_추천리포트.md")
    open(md_path, "w", encoding="utf-8").write("\n".join(L))
    print(f"리포트: {md_path}\n목록:   {csv_path}")
    return md_path


# ---------------------------------------------------------------- 웹 화면 데이터
WEB_DIR = os.path.join(BASE, "web")
SLIM = ["bidNtceNo", "bidNtceOrd", "bidNtceNm", "bidNtceSttusNm", "bidNtceDate", "bidNtceBgn",
        "bsnsDivNm", "cntrctCnclsMthdNm", "bidwinrDcsnMthdNm", "ntceInsttNm", "dmndInsttNm",
        "bidPrtcptQlfctRgstClseDate", "bidPrtcptQlfctRgstClseTm", "bidClseDate", "bidClseTm",
        "opengDate", "opengTm", "asignBdgtAmt", "presmptPrce", "rgnLmtYn", "prtcptPsblRgnNm",
        "indstrytyLmtYn", "bidprcPsblIndstrytyNm", "bidNtceUrl"]


def build_web(days=60, sample=False):
    """web/data/ 에 index.json, recs.json, days/YYYYMMDD.json 생성."""
    cfg = json.load(open(CONFIG_PATH, encoding="utf-8"))
    con = db()
    con.row_factory = sqlite3.Row
    dates = [r[0] for r in con.execute(
        "SELECT DISTINCT bidNtceDate FROM bids WHERE bidNtceDate<>'' "
        "ORDER BY bidNtceDate DESC LIMIT ?", (days,))]
    out = os.path.join(WEB_DIR, "data")
    os.makedirs(os.path.join(out, "days"), exist_ok=True)
    today = dt.date.today()
    index, recs = [], []
    for iso in dates:
        rows = [dict(r) for r in con.execute(
            "SELECT * FROM bids WHERE bidNtceDate=? ORDER BY bidNtceBgn", (iso,))]
        by_type, items, n_rec = {}, [], 0
        for r in rows:
            t = r["bsnsDivNm"] or "기타"
            by_type[t] = by_type.get(t, 0) + 1
            s, why = score(r, cfg, dt.date.fromisoformat(iso))
            it = {k: r[k] for k in SLIM}
            it["score"], it["why"] = s, why
            items.append(it)
            if s is not None:
                n_rec += 1
                s_now, why_now = score(r, cfg, today)
                if s_now is not None or sample:
                    recs.append(dict(it, score=s_now if s_now is not None else s,
                                     why=why_now if s_now is not None else why))
        day = iso.replace("-", "")
        json.dump(items, open(os.path.join(out, "days", f"{day}.json"), "w", encoding="utf-8"),
                  ensure_ascii=False, separators=(",", ":"))
        index.append({"date": iso, "total": len(rows), "byType": by_type, "recommended": n_rec})
    recs.sort(key=lambda x: (-x["score"], x["bidClseDate"] or "9999"))
    json.dump(recs, open(os.path.join(out, "recs.json"), "w", encoding="utf-8"),
              ensure_ascii=False, separators=(",", ":"))
    meta = {"generated": dt.datetime.now().isoformat(timespec="minutes"), "sample": sample,
            "company": cfg.get("company_name"), "criteria": cfg,
            "totalStored": con.execute("SELECT COUNT(*) FROM bids").fetchone()[0], "days": index}
    json.dump(meta, open(os.path.join(out, "index.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"웹 데이터: {out} ({len(index)}일, 추천 {len(recs)}건)")


def serve(port):
    import functools
    import http.server
    h = functools.partial(http.server.SimpleHTTPRequestHandler, directory=WEB_DIR)
    print(f"브라우저에서 http://localhost:{port} 를 여세요 (종료: Ctrl+C)")
    http.server.ThreadingHTTPServer(("127.0.0.1", port), h).serve_forever()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["collect", "report", "daily", "load-sample", "build-web", "serve"])
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--sample", action="store_true")
    ap.add_argument("file", nargs="?")
    ap.add_argument("--date", help="YYYYMMDD (기본: 어제)")
    a = ap.parse_args()
    day = a.date or (dt.date.today() - dt.timedelta(days=1)).strftime("%Y%m%d")
    if a.cmd == "load-sample":
        items = json.load(open(a.file, encoding="utf-8"))
        print(f"샘플 신규 저장 {upsert(db(), items, 'sample')}건")
    elif a.cmd == "collect":
        collect(day)
    elif a.cmd == "report":
        report(day)
    elif a.cmd == "build-web":
        build_web(sample=a.sample)
    elif a.cmd == "serve":
        serve(a.port)
    else:
        collect(day)
        report(day)
        build_web()


if __name__ == "__main__":
    main()
