#!/usr/bin/env python3
"""
빅텍스 현행 홈페이지(http://www.victex.co.kr) 정적 미러 생성기.

- 원본 PHP(그누보드5) 페이지를 그대로 받아와 정적 HTML로 저장한다.
- 절대/루트 경로 링크를 로컬 상대경로로 바꿔, 서버 없이도 열람 가능하게 만든다.
- 페이지·CSS 가 참조하는 이미지/폰트/스크립트를 함께 내려받는다.

사용법:
    python3 tools/mirror.py            # ./original 에 생성
    python3 tools/mirror.py --out DIR  # 다른 위치에 생성

파일명 규칙
    /                                   -> index.html
    /s1/s1_3.php                        -> s1/s1_3.html
    /bbs/board.php?bo_table=s4_1        -> bbs/s4_1.html
    /bbs/board.php?bo_table=s4_1&wr_id=23 -> bbs/s4_1_23.html
    /bbs/write.php?bo_table=s5_1        -> bbs/s5_1_write.html
"""
import argparse
import html
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

ORIGIN = "http://www.victex.co.kr"
HOSTS = {"www.victex.co.kr", "victex.co.kr"}
UA = "Mozilla/5.0 (X11; Linux x86_64) VictexMirror/1.0"

# 정적 메뉴 페이지 (GNB 기준)
SEED_PAGES = [
    "/",
    "/s1/s1_3.php", "/s1/s1_2.php",
    "/s2/s2_4.php", "/s2/s2_5.php", "/s2/s2_6.php",
    "/s1/s1_6.php",
    "/s1/s1_1_1.php", "/s1/s1_1_2.php",
    "/s1/s1_4_1.php", "/s1/s1_4_2.php", "/s1/s1_4_3.php", "/s1/s1_4_4.php",
    "/s1/s1_5.php",
    "/s3/s3_1.php", "/s3/s3_2.php", "/s3/s3_3.php",
    "/bbs/board.php?bo_table=s4_1",
    "/bbs/board.php?bo_table=s4_2",
    "/bbs/board.php?bo_table=s4_3",
    "/bbs/write.php?bo_table=s5_1",
]

ASSET_EXT = (".css", ".js", ".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp", ".ico",
             ".woff", ".woff2", ".ttf", ".eot", ".otf", ".mp4", ".webm", ".pdf")


def fetch(url, retries=3):
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            err = e
        except Exception as e:  # noqa: BLE001
            err = e
        time.sleep(2 ** i)
    print(f"  ! fetch failed: {url} ({err})", file=sys.stderr)
    return None


def page_local_path(u):
    """사이트 URL(파싱된) -> 로컬 HTML 경로. 페이지가 아니면 None."""
    path = u.path or "/"
    q = urllib.parse.parse_qs(u.query)
    if path in ("/", "/index.php"):
        return "index.html"
    if path == "/bbs/board.php" and "bo_table" in q:
        t = q["bo_table"][0]
        if q.get("wr_id"):
            return f"bbs/{t}_{q['wr_id'][0]}.html"
        if set(q) - {"bo_table", "page"}:
            return None
        return f"bbs/{t}.html"
    if path == "/bbs/write.php" and "bo_table" in q and set(q) == {"bo_table"}:
        return f"bbs/{q['bo_table'][0]}_write.html"
    if re.fullmatch(r"/s\d/[\w]+\.php", path) and not u.query:
        return path.lstrip("/")[:-4] + ".html"
    return None


def asset_local_path(u):
    path = urllib.parse.unquote(u.path)
    if path.lower().endswith(ASSET_EXT):
        return path.lstrip("/")
    return None


class Mirror:
    def __init__(self, out):
        self.out = out
        self.pages = {}       # local path -> url
        self.assets = set()   # local asset paths already handled
        self.queue = []

    # ---------- helpers ----------
    def rel(self, from_file, to_file):
        r = os.path.relpath(to_file, os.path.dirname(from_file) or ".")
        return r.replace(os.sep, "/")

    def is_site(self, u):
        return u.scheme in ("http", "https", "") and (u.netloc in HOSTS or u.netloc == "")

    def want_page(self, u):
        if u.netloc == "victex.co.kr" and u.path.startswith("/eng"):
            return None  # 영문 사이트는 범위 밖
        lp = page_local_path(u)
        if lp and lp not in self.pages:
            self.pages[lp] = urllib.parse.urlunparse(("http", "www.victex.co.kr", u.path, "", u.query, ""))
            self.queue.append(lp)
        return lp

    def get_asset(self, u):
        lp = asset_local_path(u)
        if not lp:
            return None
        dst = os.path.join(self.out, lp)
        if lp in self.assets:
            return lp if os.path.exists(dst) else None
        self.assets.add(lp)
        if not os.path.exists(dst):
            data = fetch(ORIGIN + urllib.parse.quote(u.path))
            if data is None:
                print(f"  - missing on server: /{lp}")
                return None
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            with open(dst, "wb") as f:
                f.write(data)
        if lp.endswith(".css"):
            self.process_css(lp)
        return lp

    # ---------- css ----------
    def process_css(self, lp):
        p = os.path.join(self.out, lp)
        txt = open(p, encoding="utf-8", errors="ignore").read()
        base = ORIGIN + "/" + lp

        def repl(m):
            raw = m.group(2)
            if raw.startswith(("data:", "#")):
                return m.group(0)
            u = urllib.parse.urlparse(urllib.parse.urljoin(base, raw))
            if not self.is_site(u):
                return m.group(0)
            alp = self.get_asset(u)
            if not alp:
                return m.group(0)
            return f"url({m.group(1)}{self.rel(lp, alp)}{m.group(1)})"

        new = re.sub(r"url\(\s*(['\"]?)([^'\")]+)\1\s*\)", repl, txt)
        new = re.sub(r"@import\s+(['\"])([^'\"]+)\1",
                     lambda m: self._css_import(lp, base, m), new)
        if new != txt:
            open(p, "w", encoding="utf-8").write(new)

    def _css_import(self, lp, base, m):
        u = urllib.parse.urlparse(urllib.parse.urljoin(base, m.group(2)))
        if self.is_site(u):
            alp = self.get_asset(u)
            if alp:
                return f"@import {m.group(1)}{self.rel(lp, alp)}{m.group(1)}"
        return m.group(0)

    # ---------- html ----------
    def rewrite_url(self, page_lp, page_url, raw):
        val = html.unescape(raw.strip())
        if not val or val.startswith(("#", "javascript:", "mailto:", "tel:", "data:")):
            return raw
        if val in ("www.victex.co.kr",):  # 원본의 잘못된 canonical/og:url 값 보존
            return raw
        u = urllib.parse.urlparse(urllib.parse.urljoin(page_url, val))
        if not self.is_site(u):
            return raw
        frag = ("#" + u.fragment) if u.fragment else ""
        lp = self.want_page(u)
        if lp:
            return html.escape(self.rel(page_lp, lp) + frag, quote=True)
        alp = self.get_asset(u)
        if alp:
            return html.escape(self.rel(page_lp, alp), quote=True)
        # 로컬화 불가능한 동적 링크(다운로드, 검색 등)는 원본 사이트로 연결
        absu = urllib.parse.urlunparse(("http", "www.victex.co.kr", u.path, u.params, u.query, u.fragment))
        return html.escape(absu, quote=True)

    def process_page(self, lp):
        url = self.pages[lp]
        data = fetch(url)
        if data is None:
            print(f"  ! page missing: {url}")
            return
        txt = data.decode("utf-8", errors="replace")

        def attr(m):
            return f'{m.group(1)}{m.group(2)}{self.rewrite_url(lp, url, m.group(3))}{m.group(2)}'

        txt = re.sub(r'(\s(?:href|src|action|data-src|poster)=)(["\'])(.*?)\2', attr, txt, flags=re.S)

        def style_url(m):
            new = self.rewrite_url(lp, url, m.group(2))
            return f"url({m.group(1)}{new}{m.group(1)})"

        txt = re.sub(r"url\(\s*(['\"]?)([^'\")]+)\1\s*\)", style_url, txt)

        # JS 내부에 박힌 이미지 경로("http://www.victex.co.kr/theme/...png") 처리
        def js_asset(m):
            u = urllib.parse.urlparse(m.group(0))
            alp = self.get_asset(u)
            return self.rel(lp, alp) if alp else m.group(0)

        txt = re.sub(r"http://www\.victex\.co\.kr/(?:theme|img|data|css|js)/[^\"'\s)<>]+", js_asset, txt)

        dst = os.path.join(self.out, lp)
        os.makedirs(os.path.dirname(dst) or ".", exist_ok=True)
        with open(dst, "w", encoding="utf-8") as f:
            f.write(txt)
        print(f"  page {lp:28s} <- {url}")

    def run(self):
        for s in SEED_PAGES:
            self.want_page(urllib.parse.urlparse(ORIGIN + s))
        while self.queue:
            self.process_page(self.queue.pop(0))
            time.sleep(0.2)
        # JS 파일 안의 루트 경로 이미지 참조는 원본 서버 경로 구조 그대로 유지되므로 별도 처리 불필요
        print(f"\npages: {len(self.pages)}  assets: {len(self.assets)}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "..", "original"))
    args = ap.parse_args()
    out = os.path.abspath(args.out)
    os.makedirs(out, exist_ok=True)
    print(f"mirroring {ORIGIN} -> {out}")
    Mirror(out).run()


if __name__ == "__main__":
    main()
