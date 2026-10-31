// The profile picture: idanach.com's "I" mark (its favicon, public/favicon.svg in the Portfolio repository), drawn at
// 1024 x 1024 in the site's colours, in four looks. GitHub shows a profile picture as a circle, so the mark sits well
// inside it. Rendered by Chrome from vector paths, so it stays sharp at any size GitHub shows it.
//   node tools/avatar.mjs [out folder, default assets]      writes avatar-<look>.png
import { writeFileSync, mkdirSync } from 'node:fs';
import { resolve, join } from 'node:path';
import { pathToFileURL } from 'node:url';

const { chromium } = await import(pathToFileURL(resolve('../Portfolio/node_modules/playwright/index.mjs')).href);
const out = resolve(process.argv[2] || 'assets');
const S = 1024;
// the site's colours (Portfolio src/styles/tokens.css): night, paper, the night look on the blueprint grid, and accent
const LOOKS = {
  night: { bg: '#0A0E22', fg: '#EEF0FA', dot: '#8F7BFF' },
  paper: { bg: '#EFEDE6', fg: '#121212', dot: '#5B3DF5' },
  blueprint: { bg: '#0A0E22', fg: '#EEF0FA', dot: '#8F7BFF', grid: '#232B52' },
  accent: { bg: '#5B3DF5', fg: '#FFFFFF', dot: '#0A0E22' },
};
const MARK = 0.62;                       // the mark's box, as a share of the picture's width

function svg(c) {
  const k = (S * MARK) / 64, o = (S - S * MARK) / 2;
  const grid = c.grid
    ? `<defs><pattern id="g" width="${S / 16}" height="${S / 16}" patternUnits="userSpaceOnUse"><path d="M${S / 16} 0H0V${S / 16}" fill="none" stroke="${c.grid}" stroke-width="2"/></pattern></defs><rect width="${S}" height="${S}" fill="url(#g)"/>`
    : '';
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${S} ${S}" width="${S}" height="${S}">
<rect width="${S}" height="${S}" fill="${c.bg}"/>${grid}
<g transform="translate(${o},${o}) scale(${k})">
<g transform="rotate(-24 32 32)"><path fill="none" stroke="${c.fg}" stroke-width="3.6" d="M3 32 A29 11 0 0 1 61 32"/></g>
<path fill="${c.fg}" transform="translate(18.25,52) scale(0.02778,-0.02778)" d="M84 0V345H290V1095H84V1440H906V1095H700V345H906V0Z"/>
<g transform="rotate(-24 32 32)"><path fill="none" stroke="${c.fg}" stroke-width="3.6" d="M61 32 A29 11 0 0 1 3 32"/><circle fill="${c.dot}" cx="46" cy="41.3" r="5.6"/></g>
</g></svg>`;
}

mkdirSync(out, { recursive: true });
const browser = await chromium.launch({ channel: 'chrome' });
const page = await browser.newPage({ viewport: { width: S, height: S }, deviceScaleFactor: 1 });
for (const [look, c] of Object.entries(LOOKS)) {
  await page.setContent(`<body style="margin:0">${svg(c)}</body>`);
  const file = join(out, `avatar-${look}.png`);
  writeFileSync(file, await page.screenshot({ clip: { x: 0, y: 0, width: S, height: S } }));
  console.log(file);
}
await browser.close();
