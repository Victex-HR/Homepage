#!/usr/bin/env node
/**
 * original/ 과 renewal/ 메인 페이지를 같은 해상도로 캡처해 screenshots/ 에 저장한다.
 * 히어로 리뉴얼 전·후 비교, 그리고 히어로 외 섹션이 바뀌지 않았는지 확인하는 용도.
 *
 *   npm run shots                 # 기본 4개 해상도, 히어로 화면
 *   npm run shots -- --sections   # fullPage 전체 섹션까지 캡처
 *
 * 의존성: playwright (npm i -D playwright && npx playwright install chromium)
 */
const http = require('http');
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const ROOT = path.resolve(__dirname, '..');
const OUT = path.join(ROOT, 'screenshots');
const VIEWPORTS = [[1920, 1080], [1366, 768], [800, 1000], [390, 844]];
const SECTIONS = ['MAIN', 'MCNT1', 'MCNT2', 'MCNT3', 'MCNT4', 'MCNT5', 'FOOTER'];
const withSections = process.argv.includes('--sections');

const MIME = {
  '.html': 'text/html; charset=utf-8', '.css': 'text/css', '.js': 'application/javascript',
  '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.gif': 'image/gif',
  '.svg': 'image/svg+xml', '.webp': 'image/webp', '.woff': 'font/woff', '.woff2': 'font/woff2',
  '.ttf': 'font/ttf', '.eot': 'application/vnd.ms-fontobject', '.mp4': 'video/mp4',
};

function serve() {
  return new Promise((resolve) => {
    const server = http.createServer((req, res) => {
      const p = path.join(ROOT, decodeURIComponent(req.url.split('?')[0]));
      if (!p.startsWith(ROOT) || !fs.existsSync(p) || fs.statSync(p).isDirectory()) {
        res.writeHead(404); return res.end();
      }
      res.writeHead(200, { 'Content-Type': MIME[path.extname(p).toLowerCase()] || 'application/octet-stream' });
      fs.createReadStream(p).pipe(res);
    });
    server.listen(0, () => resolve(server));
  });
}

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const server = await serve();
  const base = `http://localhost:${server.address().port}`;
  const browser = await chromium.launch();

  for (const [w, h] of VIEWPORTS) {
    for (const site of ['original', 'renewal']) {
      const page = await browser.newPage({ viewport: { width: w, height: h } });
      await page.goto(`${base}/${site}/index.html`, { waitUntil: 'networkidle', timeout: 60000 }).catch(() => {});
      // 전환 애니메이션을 끄고 최종 상태로 캡처
      await page.addStyleTag({ content: '*,*::before,*::after{transition:none!important;animation:none!important}' });
      await page.waitForTimeout(800);
      const targets = withSections ? SECTIONS : ['MAIN'];
      for (const [i, anchor] of targets.entries()) {
        if (i > 0) {
          await page.evaluate((n) => window.$ && $.fn.fullpage && $.fn.fullpage.moveTo(n), i + 1);
          await page.waitForTimeout(1200);
        }
        const file = path.join(OUT, `${w}x${h}_${anchor}_${site}.png`);
        await page.screenshot({ path: file });
        console.log('saved', path.relative(ROOT, file));
      }
      await page.close();
    }
  }
  await browser.close();
  server.close();
})();
