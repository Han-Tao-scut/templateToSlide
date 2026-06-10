#!/usr/bin/env node
/**
 * Defensive dom-to-pptx export adapter.
 *
 * The public shape of dom-to-pptx may vary across installations. This adapter
 * performs preflight checks on the HTML contract, then tries common module API
 * shapes. If none match, it fails with a clear error so the installed package's
 * examples can be inspected and this adapter updated without changing the Skill
 * workflow.
 */

import fs from 'node:fs';
import path from 'node:path';
import process from 'node:process';
import { fileURLToPath, pathToFileURL } from 'node:url';

function parseArgs(argv) {
  const args = { input: null, out: null, selector: '#pptx-export-root .slide', json: false };
  for (let i = 0; i < argv.length; i += 1) {
    const item = argv[i];
    if (item === '--out') {
      args.out = argv[++i];
    } else if (item === '--selector') {
      args.selector = argv[++i];
    } else if (item === '--json') {
      args.json = true;
    } else if (!args.input) {
      args.input = item;
    } else {
      throw new Error(`Unexpected argument: ${item}`);
    }
  }
  if (!args.input) throw new Error('Missing input HTML path');
  if (!args.out) throw new Error('Missing --out output PPTX path');
  return args;
}

function validateHtmlContract(html) {
  const errors = [];
  const warnings = [];
  if (!html.includes('id="pptx-export-root"') && !html.includes("id='pptx-export-root'")) {
    errors.push('HTML must contain #pptx-export-root');
  }
  const slideMatches = html.match(/<section\b[^>]*class=["'][^"']*\bslide\b[^"']*["'][^>]*>/g) || [];
  if (slideMatches.length === 0) {
    errors.push('HTML must contain one or more <section class="slide"> elements');
  }
  if (/transform\s*:\s*scale\(/i.test(html)) {
    warnings.push('HTML contains transform: scale(...). Export DOM should use natural unscaled slide dimensions.');
  }
  if (/Option\s+[A-C]|Preview|Generated/i.test(html)) {
    warnings.push('HTML appears to contain preview/debug labels; ensure they are not inside the export canvas.');
  }
  return { errors, warnings, slideCount: slideMatches.length };
}

async function loadDomToPptx() {
  try {
    return await import('dom-to-pptx');
  } catch (error) {
    const require = (await import('node:module')).createRequire(import.meta.url);
    try {
      return require('dom-to-pptx');
    } catch {
      throw new Error(`Unable to import dom-to-pptx. Install runtime dependencies first. Original error: ${error.message}`);
    }
  }
}

async function tryFunction(fn, attempts) {
  let lastError = null;
  for (const attempt of attempts) {
    try {
      const result = await attempt(fn);
      return { ok: true, result };
    } catch (error) {
      lastError = error;
    }
  }
  return { ok: false, error: lastError };
}

function resultToFile(result, outPath) {
  if (!result) return fs.existsSync(outPath);
  if (Buffer.isBuffer(result)) {
    fs.writeFileSync(outPath, result);
    return true;
  }
  if (result instanceof Uint8Array) {
    fs.writeFileSync(outPath, Buffer.from(result));
    return true;
  }
  if (typeof result === 'string' && fs.existsSync(result) && result !== outPath) {
    fs.copyFileSync(result, outPath);
    return true;
  }
  return fs.existsSync(outPath);
}

async function exportWithModule(mod, html, inputPath, outPath, selector) {
  const candidates = [
    mod.default,
    mod.domToPptx,
    mod.convert,
    mod.convertHtmlToPptx,
    mod.htmlToPptx,
    mod.exportToPptx,
    mod.createPptx,
  ].filter((item, index, arr) => typeof item === 'function' && arr.indexOf(item) === index);

  if (candidates.length === 0) {
    throw new Error('dom-to-pptx module loaded, but no known export function was found. Inspect the installed package examples and update scripts/export_dom_to_pptx.mjs.');
  }

  const fileUrl = pathToFileURL(path.resolve(inputPath)).href;
  const commonOptions = {
    output: outPath,
    outputPath: outPath,
    out: outPath,
    selector,
    rootSelector: '#pptx-export-root',
    slideSelector: selector,
    width: 1920,
    height: 1080,
  };

  const attempts = [
    (fn) => fn(html, commonOptions),
    (fn) => fn({ html, ...commonOptions }),
    (fn) => fn(inputPath, commonOptions),
    (fn) => fn({ input: inputPath, inputPath, ...commonOptions }),
    (fn) => fn(fileUrl, commonOptions),
    (fn) => fn({ url: fileUrl, ...commonOptions }),
  ];

  const errors = [];
  for (const fn of candidates) {
    const outcome = await tryFunction(fn, attempts);
    if (outcome.ok && resultToFile(outcome.result, outPath)) {
      return { functionName: fn.name || 'anonymous', output: outPath };
    }
    if (outcome.error) errors.push(`${fn.name || 'anonymous'}: ${outcome.error.message}`);
  }

  throw new Error(`No known dom-to-pptx call signature succeeded. Attempts: ${errors.join(' | ')}`);
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const inputPath = path.resolve(args.input);
  const outPath = path.resolve(args.out);
  const html = fs.readFileSync(inputPath, 'utf8');
  const contract = validateHtmlContract(html);
  const report = {
    ok: false,
    input: inputPath,
    output: outPath,
    selector: args.selector,
    contract,
    export: null,
    error: null,
  };

  if (contract.errors.length > 0) {
    report.error = contract.errors.join('; ');
    if (args.json) console.log(JSON.stringify(report, null, 2));
    else console.error(report.error);
    process.exit(1);
  }

  fs.mkdirSync(path.dirname(outPath), { recursive: true });
  const mod = await loadDomToPptx();
  report.export = await exportWithModule(mod, html, inputPath, outPath, args.selector);
  report.ok = fs.existsSync(outPath) && fs.statSync(outPath).size > 0;
  if (!report.ok) {
    report.error = 'Export completed without producing a non-empty PPTX file';
  }

  if (args.json) console.log(JSON.stringify(report, null, 2));
  else {
    if (contract.warnings.length > 0) {
      console.warn('Warnings:');
      for (const warning of contract.warnings) console.warn(`  - ${warning}`);
    }
    console.log(`Exported: ${outPath}`);
    console.log(`Slides detected: ${contract.slideCount}`);
  }

  process.exit(report.ok ? 0 : 1);
}

main().catch((error) => {
  const report = { ok: false, error: error.message };
  if (process.argv.includes('--json')) console.log(JSON.stringify(report, null, 2));
  else console.error(error.message);
  process.exit(1);
});
