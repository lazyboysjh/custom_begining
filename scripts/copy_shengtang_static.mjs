# Copy static HTML UIs into dist for jsDelivr / local CDN path
import { copyFileSync, mkdirSync, existsSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
for (const sub of ['cover', 'status']) {
  const src = path.join(root, 'src/shengtang/ui', sub, 'index.html');
  const dstDir = path.join(root, 'dist/shengtang/ui', sub);
  mkdirSync(dstDir, { recursive: true });
  if (existsSync(src)) {
    copyFileSync(src, path.join(dstDir, 'index.html'));
    console.log('copied', sub);
  }
}
