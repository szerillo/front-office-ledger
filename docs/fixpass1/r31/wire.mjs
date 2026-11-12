// Wire census: grade every current-winter move under a fixed, saved copy of the league feed, so two builds can be compared
import fs from 'fs';
import { createRequire } from 'module'; import { execSync } from 'child_process';
const require = createRequire(import.meta.url); const { chromium } = require(execSync('npm root -g').toString().trim() + '/playwright');
const feed = fs.readFileSync('/tmp/wire/feed.json', 'utf8');
const b = await chromium.launch(); const p = await b.newPage(); const errs = [];
p.on('pageerror', e => errs.push(e.message.slice(0, 120)));
await p.route('**/statsapi.mlb.com/**', r => r.fulfill({status: 200, contentType: 'application/json', body: feed}));
await p.route(/goatcounter|abacus/, r => r.abort());
await p.goto('file://' + process.env.PAGE, {waitUntil: 'load', timeout: 120000}); await p.waitForTimeout(4000);
const out = await p.evaluate(async () => { await wireLoad(true); const o = {};
  for (const it of WIRE.items) o[it.id] = JSON.stringify([it.kind, it.g || null, it.ga || null, it.gb || null, (it.sides || []).map(s => [s.ab, s.g, s.net]), it.grade || null]);
  return o; });
fs.writeFileSync(process.env.OUT, JSON.stringify(out)); console.log(Object.keys(out).length, 'wire items; errors', errs.length);
await b.close();
