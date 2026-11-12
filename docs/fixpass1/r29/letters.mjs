// Letter/number grade census: every report-card grade and every graded decision's letter, using the page's own functions.
import fs from 'fs';
import { open } from '/tmp/deploy/good2/tests/_common.mjs';
const {browser, page, errors} = await open();
const out = await page.evaluate(() => {
  const o = {};
  const regs = [...(typeof REGIMES !== 'undefined' ? REGIMES : []), ...AUTO_REGIMES, ...LB_HIST];
  for (const r of regs) {
    const id = r.id;
    if (r.forGrade != null) o[`rc|${id}|forGrade`] = r.forGrade;
    for (const [ch, v] of Object.entries(r.chan || {})) if (v && v.g != null) o[`rc|${id}|${ch}.g`] = v.g;
    if (r.success && r.success.g != null) o[`rc|${id}|success.g`] = r.success.g;
  }
  const seen = new Set();
  const walk = (x, id, d) => { if (!x || typeof x !== 'object' || d > 7 || seen.has(x)) return; seen.add(x);
    if (Array.isArray(x)) { x.forEach(y => walk(y, id, d + 1)); return; }
    if (x.d && x.h && (typeof x.war === 'number' || typeof x.net === 'number') && x.ch) {
      const m = {kind: x.ch, surplus: typeof x.war === 'number' ? x.war : x.net, rel: x.rel, st: x.st};
      try { o[`mv|${id}|${x.ch}|${x.d}|${(x.pids || []).join(',')}`] = gmMoveLetter(m); } catch (e) {}
    }
    for (const k in x) { const v = x[k]; if (v && typeof v === 'object') walk(v, id, d + 1); } };
  regs.forEach(r => walk(r, r.id, 0));
  const ix = tbIndex().all, s2 = new Set();
  for (const p in ix) for (const e of ix[p]) { const k = e.d + '|' + e.seats.map(s => s[0]).sort().join('/'); if (s2.has(k)) continue; s2.add(k);
    const by = {}; e.seats.forEach(s => { by[s[0]] = (by[s[0]] || 0) + (e.incomplete || s.incomplete ? 0 : seatNet(s, e.d)); });
    for (const c in by) o[`tr|${k}|${c}`] = gmMoveLetter({kind: 'trade', surplus: by[c]}); }
  return o;
});
fs.writeFileSync(process.env.OUT, JSON.stringify(out)); console.log(Object.keys(out).length, 'errors', errors.length);
await browser.close();
