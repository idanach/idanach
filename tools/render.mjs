// Renders an SVG to a PNG at the SVG's own size (its width and height), for pictures uploaded by hand: the LinkedIn
// cover, for example.
//   node tools/render.mjs <file.svg> [out.png]
import { readFileSync, writeFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

const { chromium } = await import(pathToFileURL(resolve('../Portfolio/node_modules/playwright/index.mjs')).href);
const src = resolve(process.argv[2]);
const out = resolve(process.argv[3] || src.replace(/\.svg$/, '.png'));
const svg = readFileSync(src, 'utf8');
const w = Number(/width="(\d+)"/.exec(svg)[1]), h = Number(/height="(\d+)"/.exec(svg)[1]);
const browser = await chromium.launch({ channel: 'chrome' });
const page = await browser.newPage({ viewport: { width: w, height: h }, deviceScaleFactor: 1 });
await page.setContent(`<body style="margin:0">${svg}</body>`);
await page.waitForTimeout(300);
writeFileSync(out, await page.screenshot({ clip: { x: 0, y: 0, width: w, height: h } }));
await browser.close();
console.log(out);
