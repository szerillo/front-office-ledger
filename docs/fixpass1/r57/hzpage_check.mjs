// Round 57 (Nov 14 audit item 1): the next-five-years ranks a reader sees do not change between loads.
// Loads each club's report card N times (default 6) with the live transaction feed on (every other load with the feed
// held back 4 s, as on a slow connection), waits until the feed has been
// applied, and reads the five ranks drawn in the card's "The next five years" box. Pass: for each club every load
// shows the same five ranks, and they equal the page's own league table (hzLeague) after the feed. Clubs: BOS, SF,
// ATL, TB (the Auditor's cases) plus NYY. Exit 1 otherwise. Usage: BASE=<site url> [N=6] node hzpage_check.mjs
import { createRequire } from 'module';
import { execSync } from 'child_process';
import { report } from './_common.mjs';
const require = createRequire(import.meta.url);
let chromium; try { ({ chromium } = require('playwright')); } catch { ({ chromium } = require(execSync('npm root -g').toString().trim() + '/playwright')); }
const BASE = process.env.BASE || 'http://127.0.0.1:8767/r57/tree/', N = +(process.env.N || 6);
const clubs = ['bos', 'sf', 'atl', 'tb', 'nyy'];
const browser = await chromium.launch(); const seen = {}, mism = [], errors = [];
for (const c of clubs) for (let i = 0; i < N; i++) {
  const page = await browser.newPage({viewport: {width: 1500, height: 1000}});
  page.on('pageerror', e => errors.push(e.message.slice(0, 120)));
  await page.route(/gc\.zgo\.at|goatcounter\.com/, r => r.abort());
  // every other load gets the transaction feed 4 s late (a slow network), so the card is drawn before the feed arrives
  if (i % 2) await page.route('**/statsapi.mlb.com/**', async r => { await new Promise(z => setTimeout(z, 4000)); r.continue(); });
  await page.route(/abacus\.jasoncameron\.dev/, r => r.fulfill({status: 200, contentType: 'application/json', body: '{"value":5}'}));
  await page.goto(BASE + '?v=' + Date.now() + i + '#view=cards&id=' + c, {waitUntil: 'load', timeout: 120000});
  await page.waitForFunction(() => window.HZ_FEED_DONE === true || (typeof LIVE !== 'undefined' && LIVE.ok), null, {timeout: 60000}).catch(() => {});
  await page.waitForTimeout(800 + (i % 3) * 700 + (i % 2 ? 1500 : 0));
  const r = await page.evaluate((c) => { const box = [...document.querySelectorAll('#view-report .home-card')].find(e => /The next five years/.test(e.textContent));
    const shown = box ? [...box.querySelectorAll('.mini-bars .mb span')].map(s => s.textContent.trim()).filter(t => /^#\d+$/.test(t)).join(',') : null;
    const row = hzLeague().rows.find(r => r.ab === c.toUpperCase()); return {shown, table: row ? row.rk.map(k => '#' + k).join(',') : null, feed: typeof LIVE !== 'undefined' && !!LIVE.ok}; }, c);
  (seen[c] = seen[c] || new Set()).add(r.shown);
  if (r.shown !== r.table) mism.push(`${c} load ${i + 1}: shown ${r.shown} table ${r.table} feed ${r.feed}`);
  await page.close();
}
await browser.close();
const flips = Object.entries(seen).filter(([, s]) => s.size > 1).map(([c, s]) => c + ': ' + [...s].join(' | '));
console.log('loads', clubs.length * N, 'flips', flips, 'mismatches', mism.slice(0, 6));
report('hzpage_check', {all_loads_drawn: Object.values(seen).every(s => ![...s].includes(null)), same_ranks_every_load: flips.length === 0, drawn_equals_league_table: mism.length === 0}, errors);
