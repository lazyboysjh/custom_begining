import { chromium } from 'playwright';
import path from 'node:path';
import fs from 'node:fs';
import { fileURLToPath, pathToFileURL } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const ui = path.join(root, 'src/shengtang/ui');
const out = path.join(root, 'tmp/ui-audit');
fs.mkdirSync(out, { recursive: true });

const preview = pathToFileURL(path.join(ui, 'preview.html')).href;
const cover = pathToFileURL(path.join(ui, 'cover/index.html')).href;

const viewports = [
  ['desktop', 1280, 800],
  ['tablet', 768, 1024],
  ['mobile', 390, 844],
];

async function main() {
  const browser = await chromium.launch();
  const page = await browser.newPage();

  for (const [name, w, h] of viewports) {
    await page.setViewportSize({ width: w, height: h });

    // status
    await page.goto(preview, { waitUntil: 'networkidle' });
    await page.click('button[data-pane="status"]');
    await page.waitForTimeout(1000);
    const frame = page.frameLocator('#statusFrame');
    await frame.locator('.stat').first.click();
    await page.waitForTimeout(700);
    await page.screenshot({ path: path.join(out, `status-${name}.png`), fullPage: true });

    // cover page 1
    await page.goto(cover, { waitUntil: 'networkidle' });
    await page.waitForTimeout(600);
    await page.screenshot({ path: path.join(out, `cover-p1-${name}.png`), fullPage: true });

    // cover page 3
    await page.click('#btnEnter');
    await page.waitForTimeout(400);
    await page.click('#btnToMeet');
    await page.waitForTimeout(500);
    const cards = page.locator('.char-card');
    if ((await cards.count()) > 0) {
      await cards.first.click();
      await page.waitForTimeout(400);
    }
    await page.screenshot({ path: path.join(out, `cover-p3-${name}.png`), fullPage: true });
  }

  await browser.close();
  console.log('wrote', out);
  for (const f of fs.readdirSync(out).filter(x => x.endsWith('.png'))) {
    console.log('-', f, fs.statSync(path.join(out, f)).size);
  }
}

main().catch(err => {
  console.error(err);
  process.exit(1);
});
