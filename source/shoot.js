const puppeteer = require('puppeteer-core');
const path = require('path');

const BASE = path.resolve(__dirname, '..');   // project root (parent of source/)
const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';

const SHOTS = [
  ['00-hero',   0],
  ['01-before', 1],
  ['02-garden', 2],
  ['03-fire',   3],
  ['04-cook',   4],
  ['05-camp',   5],
  ['06-sky',    6],
  ['07-now',    7],
];

(async () => {
  const browser = await puppeteer.launch({
    executablePath: CHROME,
    headless: 'new',
    args: ['--allow-file-access-from-files', '--force-device-scale-factor=1', '--hide-scrollbars'],
  });
  const page = await browser.newPage();

  const problems = [];
  page.on('console', m => { if (m.type() === 'error' || m.type() === 'warning') problems.push(m.type().toUpperCase() + ': ' + m.text()); });
  page.on('pageerror', e => problems.push('PAGEERROR: ' + e.message));
  page.on('requestfailed', r => problems.push('REQFAIL: ' + r.url().slice(0, 90) + ' :: ' + (r.failure() && r.failure().errorText)));

  const width = Number(process.argv[2] || 1440);
  const height = Number(process.argv[3] || 900);
  const tag = process.argv[4] || 'desk';
  await page.setViewport({ width, height, deviceScaleFactor: 2 });

  await page.goto('file://' + path.join(BASE, 'finding-shreya.html'), { waitUntil: 'networkidle0', timeout: 90000 });
  await page.evaluate(() => document.fonts.ready);
  await new Promise(r => setTimeout(r, 1200));

  // report which fonts actually resolved
  const fontCheck = await page.evaluate(() => {
    const names = ['Eczar', 'Newsreader', 'Karla'];
    return names.map(n => n + '=' + document.fonts.check('16px "' + n + '"'));
  });

  for (const [name, idx] of SHOTS) {
    await page.evaluate((i) => {
      const secs = document.querySelectorAll('main > section');
      const s = secs[i];
      window.scrollTo({ top: s.offsetTop, behavior: 'instant' });
      // settle the reveal state so screenshots show the finished frame
      document.querySelectorAll('.rv').forEach(el => el.classList.add('in'));
    }, idx);
    await new Promise(r => setTimeout(r, idx === 2 ? 2900 : 900));
    await page.screenshot({ path: `${BASE}/preview/${tag}-${name}.png` });
  }

  // page-level sanity
  const info = await page.evaluate(() => ({
    scrollW: document.documentElement.scrollWidth,
    clientW: document.documentElement.clientWidth,
    docH: document.documentElement.scrollHeight,
    wipeX: getComputedStyle(document.getElementById('wipe')).getPropertyValue('--x').trim(),
    bodyBg: getComputedStyle(document.body).backgroundColor,
  }));

  console.log('fonts   :', fontCheck.join('  '));
  console.log('layout  :', JSON.stringify(info));
  console.log('h-scroll:', info.scrollW > info.clientW ? '*** OVERFLOW ' + info.scrollW + ' > ' + info.clientW : 'none');
  console.log('problems:', problems.length ? '\n  ' + [...new Set(problems)].join('\n  ') : 'none');

  await browser.close();
})();
