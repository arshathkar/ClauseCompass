#!/usr/bin/env node
/**
 * Check frontend bundle size budgets.
 * - Initial JS bundle: ≤ 200 KB gzip
 * - Lazy chunks (pdf.js + mammoth): ≤ 600 KB gzip combined
 *
 * Run after `npm run build` in the frontend directory.
 */

import { readdir, stat } from 'fs/promises';
import { join } from 'path';
import { createReadStream } from 'fs';
import { createGzip } from 'zlib';

const DIST_DIR = join(process.cwd(), 'frontend', 'dist', 'assets');
const INITIAL_BUDGET_KB = 200;
const LAZY_BUDGET_KB = 600;

async function getGzipSize(filePath) {
  return new Promise((resolve, reject) => {
    let size = 0;
    const gzip = createGzip();
    const stream = createReadStream(filePath).pipe(gzip);
    stream.on('data', (chunk) => { size += chunk.length; });
    stream.on('end', () => resolve(size));
    stream.on('error', reject);
  });
}

async function main() {
  let files;
  try {
    files = await readdir(DIST_DIR);
  } catch {
    console.error(`ERROR: ${DIST_DIR} not found. Run 'npm run build' first.`);
    process.exit(1);
  }

  const jsFiles = files.filter(f => f.endsWith('.js'));
  let initialTotal = 0;
  let lazyTotal = 0;
  const results = [];

  for (const file of jsFiles) {
    const filePath = join(DIST_DIR, file);
    const rawSize = (await stat(filePath)).size;
    const gzipSize = await getGzipSize(filePath);
    const gzipKB = gzipSize / 1024;

    const isLazy = file.includes('pdf') || file.includes('mammoth') || file.includes('chunk-');
    if (isLazy) {
      lazyTotal += gzipKB;
    } else {
      initialTotal += gzipKB;
    }

    results.push({
      file,
      raw: `${(rawSize / 1024).toFixed(1)} KB`,
      gzip: `${gzipKB.toFixed(1)} KB`,
      type: isLazy ? 'lazy' : 'initial',
    });
  }

  console.log('\nBundle Size Report');
  console.log('==================\n');
  console.table(results);

  console.log(`\nInitial JS (gzip): ${initialTotal.toFixed(1)} KB / ${INITIAL_BUDGET_KB} KB`);
  console.log(`Lazy chunks (gzip): ${lazyTotal.toFixed(1)} KB / ${LAZY_BUDGET_KB} KB\n`);

  let failed = false;
  if (initialTotal > INITIAL_BUDGET_KB) {
    console.error(`FAIL: Initial bundle (${initialTotal.toFixed(1)} KB) exceeds ${INITIAL_BUDGET_KB} KB budget`);
    failed = true;
  }
  if (lazyTotal > LAZY_BUDGET_KB) {
    console.error(`FAIL: Lazy chunks (${lazyTotal.toFixed(1)} KB) exceed ${LAZY_BUDGET_KB} KB budget`);
    failed = true;
  }

  if (failed) {
    process.exit(1);
  } else {
    console.log('OK: All bundle size budgets met.');
  }
}

main();
