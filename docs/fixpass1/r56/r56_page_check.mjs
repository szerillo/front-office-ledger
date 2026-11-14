// Round 56 (Nov 14 re-audit items 2, 5, 6, 7). Pass, all of:
// copy: no "1.35x", "1.15x" or "leverage-weighted" on the Heists page or any card's trade table;
// method: a methodology section id="method-review" explains the label and links /corrections/; every review label
//   links to it; the card note links it;
// w2020: every winter touching the 60-game 2020 season (2019-20 and 2020-21) shows its 2020 total with the 162-game
//   pace and a change on that pace; no other winter mentions it;
// trades: the Heists list labels exactly the trades on docs/fixpass1/r56/trade_review_expected.json (expected list read
//   from that file, not from the page). Exit 1 otherwise. Usage: [TARGET=live LIVE_URL=<site>] [EXPECT=<file>] node r56_page_check.mjs
import { open, report } from './_common.mjs';
import fs from 'fs';
const EXP = JSON.parse(fs.readFileSync(process.env.EXPECT || '/tmp/r56/tree/docs/fixpass1/r56/trade_review_expected.json', 'utf8'));
const d = await open();
await d.page.waitForFunction(() => window.BOOK_READY === true, null, {timeout: 90000}).catch(() => {});
const r = await d.page.evaluate(async (keys) => {
  if (typeof cardsReady === 'function') { try { await cardsReady(); } catch (e) {} }
  normalizeCurated();
  const o = {};
  // copy
  switchView('heists'); await new Promise(r => setTimeout(r, 400));
  const hv = document.getElementById('view-heists').textContent;
  let tables = 0, levT = 0;
  const pages = [...AUTO_REGIMES, ...LB_HIST.filter(x => x.realCard)];
  for (const reg of pages.slice(0, 200)) { const h = allTradesTable(reg); if (!h) continue; tables++; if (/leverage-weighted|1\.35x|1\.15x/.test(h)) levT++; }
  o.copy = {heists: /1\.35x|1\.15x|leverage-weighted/.test(hv), tables, levT};
  // method
  const sec = document.getElementById('method-review');
  renderReport(pages.find(x => x.ctrlReview).id);
  const chips = [...document.querySelectorAll('#view-report a[data-review]')], note = document.querySelector('#view-report [data-review="card"]');
  o.method = {sec: !!sec && /under review/i.test(sec.textContent) && !!(sec.nextElementSibling && sec.nextElementSibling.querySelector('a[href="/corrections/"]')),
    chips: chips.length, chipsOk: chips.filter(a => a.getAttribute('href') === '/#view=method&id=review').length, note: !!note && /method-review/.test(note.innerHTML)};
  // 2020
  if (!OFFS.rows) await offsLoad();
  const touch = OFFS.rows.filter(x => x.prevW != null && x.nextW != null && (x.w === 2019 || x.w === 2020));
  let ok20 = 0, bad20 = [], other = 0;
  for (const x of touch) { const t = (() => { const e = document.createElement('div'); e.innerHTML = offsCard(x, 0); return e.textContent; })();
    const a = x.w === 2020 ? Math.round(x.prevW * 162 / 60) : x.prevW, b = x.w === 2019 ? Math.round(x.nextW * 162 / 60) : x.nextW, dd = b - a;
    if (/per 162/.test(t) && t.includes(`(${dd >= 0 ? '+' : ''}${dd}, on a 162-game pace)`)) ok20++; else if (bad20.length < 3) bad20.push(x.id); }
  for (const x of OFFS.rows.filter(x => x.w !== 2019 && x.w !== 2020).slice(0, 300)) { const e = document.createElement('div'); e.innerHTML = offsCard(x, 0); if (/per 162|162-game/.test(e.textContent)) other++; }
  o.w2020 = {n: touch.length, ok: ok20, bad: bad20, other};
  // trades
  const want = new Set(keys); const ts = folTrades(); let miss = 0, extra = 0, lab = 0;
  for (const t of ts) { const e = document.createElement('div'); e.innerHTML = folHeistCard(t, {}); const has = !!e.querySelector('[data-review="trade"]'); if (has) lab++;
    const w = want.has(t.d + '|' + t.S.map(s => s.ab).sort().join('/')); if (w && !has) miss++; if (!w && has) extra++; }
  o.trades = {n: ts.length, labelled: lab, miss, extra, listKeys: want.size};
  return o;
}, Object.keys(EXP.trades));
console.log(JSON.stringify(r));
report('r56_page_check', {copy_heists_clean: !r.copy.heists, copy_tables_clean: r.copy.tables > 100 && r.copy.levT === 0, method_section: r.method.sec, labels_link_method: r.method.chips > 0 && r.method.chips === r.method.chipsOk, note_links_method: r.method.note,
  w2020_all_paced: r.w2020.n >= 50 && r.w2020.ok === r.w2020.n, w2020_others_clean: r.w2020.other === 0, trades_labelled_as_listed: r.trades.miss === 0 && r.trades.extra === 0 && r.trades.labelled >= 600}, d.errors);
await d.browser.close();
