// Round 54: every value on the known-wrong list carries the under-review label, and nothing else does.
// Pass: the report cards in the expected file (107) labelled exactly as listed (page note, net value, overall where it
// moves, each listed channel, letter label where the letter moves), 0 other cards labelled; the explorer winters in the
// file (320) labelled and 0 others; the winter share pages in the file (19) labelled and 0 others. Exit 1 on any miss. Usage: TARGET=live LIVE_URL=<site> node review_check.mjs
import { open } from './_common.mjs';
const BASE = process.env.LIVE_URL || 'https://frontofficeledger.com/';
const fsx = await import('fs');
const EXP = JSON.parse(fsx.readFileSync(process.env.EXPECT || 'review_expected.json', 'utf8'));
const E = Object.fromEntries(Object.entries(EXP.cards).map(([k, v]) => [k, {c: v.chans, l: v.letters, o: v.overall ? 1 : 0}]));
const d = await open();
const r = await d.page.evaluate(async ([E, WL]) => {
  const LBL = {trade: 'Trades', draft: 'Draft', fa: 'Free agency', ext: 'Extensions', intl: 'International amateurs', waiver: 'Waivers and minor-league finds'};
  if (typeof cardsReady === 'function') { try { await cardsReady(); } catch (e) {} }
  for (let i = 0; i < 100 && (typeof AUTO_REGIMES === 'undefined' || !AUTO_REGIMES.length); i++) await new Promise(r => setTimeout(r, 100));
  normalizeCurated();
  const pages = [...(typeof REGIMES !== 'undefined' ? REGIMES : []), ...AUTO_REGIMES, ...LB_HIST.filter(x => x.realCard)];
  const seen = new Set(), problems = [], labelled = [];
  const listIds = Object.keys(E);   // expected list from the file, not from the page under test
  for (const reg of pages) {
    if (seen.has(reg.id)) continue; seen.add(reg.id);
    if (reg.isNew) { if (listIds.includes(reg.id)) problems.push(reg.id + ': listed but new (no card)'); continue; }
    renderReport(reg.id);
    const root = document.getElementById('view-report');
    const has = q => root.querySelectorAll(q).length;
    const v = E[reg.id] || null;
    const note = has('[data-review="card"]'), net = has('[data-review="net"]'), ov = has('[data-review="overall"]');
    const heads = [...root.querySelectorAll('.chanhead')].map(h => ({label: h.querySelector('strong') ? h.querySelector('strong').textContent : '', chip: h.querySelector('[data-review="chan"],[data-review="letter"]'), letter: !!h.querySelector('[data-review="letter"]')}));
    if (note || net || ov || heads.some(h => h.chip)) labelled.push(reg.id);
    if (!v) { if (note || net || ov || heads.some(h => h.chip)) problems.push(reg.id + ': labelled but not on the list'); continue; }
    if (note !== 1) problems.push(reg.id + ': page note ' + note);
    if (net !== 1) problems.push(reg.id + ': net label ' + net);
    if (ov !== (v.o ? 1 : 0)) problems.push(reg.id + ': overall label ' + ov + ' expected ' + v.o);
    for (const h of heads) {
      const k = Object.keys(LBL).find(x => LBL[x] === h.label); if (!k) continue;
      const want = v.c.includes(k), wantL = v.l.includes(k);
      if (want !== !!h.chip) problems.push(`${reg.id}: channel ${k} label ${!!h.chip} expected ${want}`);
      if (wantL !== h.letter) problems.push(`${reg.id}: letter ${k} label ${h.letter} expected ${wantL}`);
    }
  }
  const missingIds = listIds.filter(i => !seen.has(i));
  missingIds.forEach(i => problems.push(i + ': on the list but no card page'));
  // winters in the explorer
  if (typeof offsLoad === 'function' && !OFFS.rows) await offsLoad();
  const W = new Set(WL);
  let wl = 0;
  for (const row of OFFS.rows || []) {
    const div = document.createElement('div'); div.innerHTML = offsCard(row, 0, {});
    const c = div.querySelectorAll('[data-review="winter"]').length;
    if (c) wl++;
    if (W.has(row.id) !== (c === 1)) problems.push(`winter ${row.id}: label ${c} expected ${W.has(row.id) ? 1 : 0}`);
  }
  return {cards_labelled: labelled.length, cards_on_list: listIds.length, card_pages: seen.size, winter_cards_labelled: wl, winter_list: W.size, problems};
}, [E, EXP.winter_explorer]);
const pages = (await (await fetch(BASE + 'share.json?t=' + Date.now())).json().catch(() => null));
const fs = await import('fs');
const O = (process.env.OPAGES || '').split(',').filter(Boolean);
let oLab = 0; const oProb = [];
for (const f of O) {
  const t = await (await fetch(BASE + 'o/' + f + '?t=' + Date.now())).text();
  const lab = /\(under review\)/.test(t) && /Under review: control-end data being corrected/.test(t);
  if (lab) oLab++;
  const want = EXP.winter_pages.includes(f);
  if (want !== lab) oProb.push(`o/${f}: label ${lab} expected ${want}`);
}
r.share_pages_labelled = oLab; r.problems.push(...oProb);
console.log(JSON.stringify(r, null, 1));
const C = EXP.counts;
const ok = r.problems.length === 0 && r.cards_labelled === C.cards && r.cards_on_list === C.cards && r.winter_cards_labelled === C.winter_explorer && oLab === C.winter_pages;
r.expected_counts = C;
console.log(ok ? 'review_check PASS' : 'review_check FAIL'); await d.browser.close(); process.exit(ok ? 0 : 1);
