// usage: node ev.mjs '<js expression returning JSON-able>' [hash]
import fs from 'fs'; import { createRequire } from 'module'; import { execSync } from 'child_process';
const require = createRequire(import.meta.url); const { chromium } = require(execSync('npm root -g').toString().trim() + '/playwright');
const b = await chromium.launch(); const p = await b.newPage({viewport: {width: 1280, height: 900}});
const errs = []; p.on('pageerror', e => errs.push(String(e))); p.on('console', m => { if(m.type() === 'error') errs.push(m.text()); });
await p.route(/gc\.zgo\.at|goatcounter\.com/, r => r.abort()); await p.route(/abacus\.jasoncameron\.dev/, r => r.fulfill({status: 200, contentType: 'application/json', body: '{"value":5}'}));
await p.goto('https://frontofficeledger.com/?cb=' + Date.now() + (process.argv[3] ? '#' + process.argv[3] : ''), {waitUntil: 'load', timeout: 120000}); await p.waitForTimeout(9000);
const src = process.argv[2].startsWith('@') ? fs.readFileSync(process.argv[2].slice(1), 'utf8') : process.argv[2];
const out = await p.evaluate(src);
console.log(typeof out === 'string' ? out : JSON.stringify(out, null, 1)); if(errs.length) console.log('ERRORS', errs.slice(0, 8));
await b.close();
