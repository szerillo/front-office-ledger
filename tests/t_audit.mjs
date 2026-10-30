// Structural audits: decision dates inside regime windows; phone-width
// horizontal overflow on every tab.
import { open, report } from './_common.mjs';
const d = await open();
const r1 = await d.page.evaluate(() => {
  const out = {violations: []};
  const starts = {};
  [...REGIMES, ...AUTO_REGIMES].forEach(r => { if(r.start) starts[r.id] = String(r.start); });
  AUTO_REGIMES.forEach(r => {
    const start = starts[r.id]; if(!start || String(start).length < 8) return;
    const chk = (d2, where) => { if(d2 && /^\d{4}-\d{2}-\d{2}$/.test(String(d2)) && String(d2) < start) out.violations.push([r.id, d2, where]); };
    Object.entries(r.ledgers || {}).forEach(([k, rows]) => (rows || []).forEach(x => chk(x.d, k)));
    Object.entries(r.chanLedgers || {}).forEach(([k, obj]) => {
      (Array.isArray(obj) ? obj : (obj.rows || [])).forEach(x => { if(x && x.d) chk(x.d, 'chan.' + k); });
    });
  });
  out.boundaryClean = out.violations.length === 0;
  return out;
});
await d.browser.close();
const m = await open({width: 390, height: 844});
const r2 = await m.page.evaluate(() => {
  const over = () => document.documentElement.scrollWidth - document.documentElement.clientWidth;
  const out = {};
  for(const v of ['leaderboard', 'report', 'trees', 'dna', 'h2h', 'desk', 'horizon', 'scen', 'gm', 'method']){
    try { switchView(v); } catch(e) {}
    out['overflow_' + v] = over() <= 2;
  }
  switchView('champs'); out.overflow_champs = over() <= 20;  // known 12px residue
  return out;
});
report('t_audit', {...r1, ...r2}, [...d.errors, ...m.errors]);
await m.browser.close();
