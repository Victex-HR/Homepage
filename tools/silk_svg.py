#!/usr/bin/env python3
"""
Renewal_4 히어로 배경용 '실크 물결' SVG 생성기.

리본 하나 = 중심선 y_c(x) + 폭 w(x).  w(x) 에 cos 를 써서 폭이 0 이 되는 지점에서
선들이 모였다가 반대로 뒤집혀 퍼지므로, 얇은 천이 꼬이며 흐르는 모양이 된다.
선 n 개를 같은 중심선 위에 (t-.5)*w(x) 만큼 띄워 그린다.

  python3 tools/silk_svg.py   # Renewal_4/assets/images/hero/hero-silk*.svg 생성
"""
import math
import os


def smooth_path(pts):
    """점 목록을 중간점 기준 2차 곡선으로 부드럽게 잇는다."""
    d = 'M{:.0f} {:.0f}'.format(*pts[0])
    for i in range(1, len(pts) - 1):
        mx = (pts[i][0] + pts[i + 1][0]) / 2
        my = (pts[i][1] + pts[i + 1][1]) / 2
        d += 'Q{:.0f} {:.0f} {:.0f} {:.0f}'.format(pts[i][0], pts[i][1], mx, my)
    d += 'L{:.0f} {:.0f}'.format(*pts[-1])
    return d


def ribbon(x0, x1, yc, w, n, grad, op_max, op_min=.06, width=.7, step=24, depth=None):
    """x0..x1 구간에서 중심선 yc(x), 폭 w(x) 인 리본을 n 개 선으로 그린다."""
    out = []
    xs = [x0 + (x1 - x0) * k / int((x1 - x0) / step) for k in range(int((x1 - x0) / step) + 1)]
    for i in range(n):
        t = i / (n - 1) - .5
        pts = []
        for x in xs:
            y = yc(x) + t * w(x)
            if depth:
                y += depth(x) * (t * t - .08)   # 가장자리 선을 살짝 휘게 해 입체감
            pts.append((x, y))
        op = op_min + (op_max - op_min) * math.cos(math.pi * t) ** 1.2
        out.append(f'<path d="{smooth_path(pts)}" stroke="url(#{grad})" stroke-opacity="{op:.3f}" stroke-width="{width}"/>')
    return '\n'.join(out)


def glow(x0, x1, yc, width, op, step=40, color='#fff'):
    pts = [(x, yc(x)) for x in range(int(x0), int(x1) + 1, step)]
    return f'<path d="{smooth_path(pts)}" stroke="{color}" stroke-opacity="{op}" stroke-width="{width}" filter="url(#blur)"/>'


def smoothstep(a, b, x):
    t = max(0.0, min(1.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)


def main_svg():
    # viewBox 1600x900 = 히어로(지표 바 제외) 영역에 늘려 맞춘다.
    # 1) 좌하단 : 왼쪽 아래에서 시작해 재생 버튼 근처에서 꼬이고, 사진 바닥 쪽으로 휘어 올라가는 큰 리본
    yc1 = lambda x: 800 - 210 * smoothstep(-60, 1000, x) + 34 * math.sin(x / 150)
    w1 = lambda x: 210 * math.cos((x + 40) / 520 * math.pi) * (1 - .35 * smoothstep(500, 1000, x))
    d1 = lambda x: 60 * math.sin(x / 260)
    # 2) 좌상단 : 제목 위쪽을 대각선으로 스치는 옅은 리본
    yc2 = lambda x: 360 - .62 * (x + 60) + 26 * math.sin(x / 120)
    w2 = lambda x: 150 * math.cos((x - 120) / 420 * math.pi)
    # 3) 중앙 하단 : 탱크 받침 아래 바닥만 스치며 오른쪽으로 빠지는 리본 (사진 위를 덮지 않도록)
    yc3 = lambda x: 850 - 30 * smoothstep(500, 1350, x) + 12 * math.sin(x / 110)
    w3 = lambda x: 70 * math.cos((x - 560) / 420 * math.pi)
    body = '\n'.join([
        # 빛 번짐은 사진이 없는 왼쪽 아래에만, 흰색 대신 옅은 하늘색으로 (사진을 뿌옇게 덮지 않도록)
        glow(-60, 520, lambda x: 790 + 20 * math.sin(x / 160), 170, .45, color='#c9dcf2'),
        ribbon(-60, 720, yc1, w1, 56, 'g1', .78, depth=d1),
        ribbon(-60, 560, yc2, w2, 40, 'g2', .36),
        ribbon(380, 1350, yc3, w3, 40, 'g3', .5),
    ])
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 900" preserveAspectRatio="none" fill="none">
<defs>
<linearGradient id="g1" gradientUnits="userSpaceOnUse" x1="-60" y1="0" x2="720" y2="0"><stop offset="0" stop-color="#5a86bf"/><stop offset=".55" stop-color="#6d97cd"/><stop offset="1" stop-color="#a7c2e5" stop-opacity="0"/></linearGradient>
<linearGradient id="g2" gradientUnits="userSpaceOnUse" x1="-60" y1="0" x2="560" y2="0"><stop offset="0" stop-color="#8fb0da"/><stop offset="1" stop-color="#8fb0da" stop-opacity="0"/></linearGradient>
<linearGradient id="g3" gradientUnits="userSpaceOnUse" x1="380" y1="0" x2="1350" y2="0"><stop offset="0" stop-color="#86a9d6" stop-opacity="0"/><stop offset=".4" stop-color="#86a9d6"/><stop offset="1" stop-color="#a7c2e5" stop-opacity="0"/></linearGradient>
<filter id="blur" filterUnits="userSpaceOnUse" x="-200" y="-100" width="2000" height="1100"><feGaussianBlur stdDeviation="26"/></filter>
</defs>
<g stroke-linecap="round" stroke-linejoin="round">
{body}
</g>
</svg>
'''


def panel_svg():
    # 우측 상단 CCUS 패널 안쪽 (viewBox 760x430 ≒ 패널) : 왼쪽 아래에서 오른쪽 위로 흐르는 옅은 리본
    yc = lambda x: 500 - .55 * (x - 300) + 15 * math.sin(x / 80)
    w = lambda x: 100 * math.cos((x - 400) / 400 * math.pi)
    body = ribbon(300, 800, yc, w, 40, 'p1', .5, step=16)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 760 430" preserveAspectRatio="none" fill="none">
<defs><linearGradient id="p1" gradientUnits="userSpaceOnUse" x1="300" y1="0" x2="800" y2="0"><stop offset="0" stop-color="#8db0da" stop-opacity="0"/><stop offset=".4" stop-color="#6f98cf"/><stop offset="1" stop-color="#9dbbe2"/></linearGradient></defs>
<g stroke-linecap="round" stroke-linejoin="round">
{body}
</g>
</svg>
'''


def top_svg():
    # Renewal_3 · Renewal_5 상단 소개 영역 (viewBox 1600x420) :
    # 소개 문구 아래에서 시작해 사옥 사진 쪽 위로 휘어 올라가는 실크 리본 (3-1안 시안의 파란 곡선)
    yc = lambda x: 430 - 330 * smoothstep(250, 1050, x) + 18 * math.sin(x / 90)
    w = lambda x: 70 * math.cos((x - 520) / 520 * math.pi) * (1 - .4 * smoothstep(700, 1050, x))
    body = '\n'.join([
        glow(260, 900, yc, 90, .55, color='#d6e6f7'),
        ribbon(250, 1050, yc, w, 44, 't1', .72, step=18),
    ])
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 420" preserveAspectRatio="none" fill="none">
<defs>
<linearGradient id="t1" gradientUnits="userSpaceOnUse" x1="250" y1="0" x2="1050" y2="0"><stop offset="0" stop-color="#4f86c6" stop-opacity="0"/><stop offset=".3" stop-color="#4a82c4"/><stop offset=".75" stop-color="#7aa6d8"/><stop offset="1" stop-color="#a9c6e8" stop-opacity="0"/></linearGradient>
<filter id="blur" filterUnits="userSpaceOnUse" x="-200" y="-100" width="2000" height="620"><feGaussianBlur stdDeviation="22"/></filter>
</defs>
<g stroke-linecap="round" stroke-linejoin="round">
{body}
</g>
</svg>
'''


if __name__ == '__main__':
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'Renewal_4', 'assets', 'images', 'hero')
    for name, svg in [('hero-silk.svg', main_svg()), ('hero-silk-panel.svg', panel_svg())]:
        with open(os.path.join(out, name), 'w', encoding='utf-8') as f:
            f.write(svg)
        print(name, round(len(svg) / 1024), 'KB')
    top = top_svg()
    for site in ('Renewal_3', 'Renewal_5'):
        d = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', site, 'assets', 'images', 'hero')
        if os.path.isdir(d):
            with open(os.path.join(d, 'hero-silk-top.svg'), 'w', encoding='utf-8') as f:
                f.write(top)
            print(site, 'hero-silk-top.svg', round(len(top) / 1024), 'KB')
