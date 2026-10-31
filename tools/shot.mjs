// Screenshots a local HTML file (or an image shown alone) at a width, in light or dark.
//   node tools/shot.mjs <file.html|.svg> <out.png> [--width 1280] [--dark] [--full]
import { pathToFileURL } from 'node:url';
import { resolve } from 'node:path';
const { chromium } = await import(pathToFileURL(resolve('../Portfolio/node_modules/playwright/index.mjs')).href);
const [src, out, ...rest] = process.argv.slice(2);
const opt = (k, d) => (rest.includes(k) ? rest[rest.indexOf(k) + 1] : d);
const browser = await chromium.launch({ channel: 'chrome' });
const page = await browser.newPage({ viewport: { width: Number(opt('--width', 1280)), height: 900 }, colorScheme: rest.includes('--dark') ? 'dark' : 'light', deviceScaleFactor: 1 });
const url = pathToFileURL(resolve(src)).href;
if (src.endsWith('.svg')) {
  // shown as a picture, the way GitHub shows it (its own fonts only, nothing loaded from outside)
  const { writeFileSync } = await import('node:fs');
  const wrap = resolve(src + '.view.html');
  writeFileSync(wrap, `<body style="margin:0;background:#888"><img src="${url}" style="width:100%;display:block"></body>`);
  await page.goto(pathToFileURL(wrap).href);
} else await page.goto(url);
await page.waitForLoadState('networkidle').catch(() => {});
await page.waitForFunction(() => [...document.images].every((i) => i.complete), null, { timeout: 20000 }).catch(() => {});
await page.waitForTimeout(Number(opt('--wait', 1500)));
await page.screenshot({ path: out, fullPage: rest.includes('--full') });
await browser.close();
console.log(out);
