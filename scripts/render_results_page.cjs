// Capture the actual static report and check desktop/mobile layout and local links.
const fs = require('node:fs');
const path = require('node:path');
const {pathToFileURL, fileURLToPath} = require('node:url');
const {chromium} = require('playwright');
const root = path.resolve(__dirname, '..');
(async () => {
  const browser = await chromium.launch({headless: true, channel: 'msedge'});
  try {
    const page = await browser.newPage();
    await page.goto(pathToFileURL(path.join(root, 'docs/index.html')).href);
    const links = await page.locator('a[href],img[src]').evaluateAll(nodes =>
      nodes.map(n => n.href || n.src).filter(Boolean));
    for (const link of links) {
      if (link.startsWith('file:') && !fs.existsSync(fileURLToPath(link.split('#')[0]))) {
        throw new Error(`Missing local target: ${link}`);
      }
    }
    for (const [name, width, height] of [['desktop', 1440, 1000], ['mobile', 390, 844]]) {
      await page.setViewportSize({width, height});
      await page.evaluate(async () => {
        document.querySelectorAll('img').forEach(img => img.loading = 'eager');
        await Promise.all([...document.images].map(img => img.decode()));
      });
      const overflow = await page.evaluate(() =>
        document.documentElement.scrollWidth > window.innerWidth);
      if (overflow) throw new Error(`Horizontal overflow at ${width}px`);
      await page.screenshot({path: path.join(root, `docs/images/results-${name}.png`), fullPage: true});
    }
    console.log('Desktop/mobile screenshots saved; local links and layout checks passed.');
  } finally { await browser.close(); }
})().catch(error => {console.error(error); process.exitCode = 1;});
