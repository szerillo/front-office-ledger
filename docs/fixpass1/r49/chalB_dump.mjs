// Round 49 challenge B: every graded letter and number the page shows, as one canonical JSON.
import { open } from './_common.mjs';
const d = await open();
const r = await d.page.evaluate(async () => {
  if (typeof normalizeCurated === 'function') normalizeCurated();
  const all = [...(typeof REGIMES !== 'undefined' ? REGIMES : []), ...(typeof AUTO_REGIMES !== 'undefined' ? AUTO_REGIMES : []), ...(typeof LB_HIST !== 'undefined' ? LB_HIST : [])];
  const out = {};
  const keep = o => { const x = {}; for (const k of Object.keys(o || {}).sort()) { const v = o[k]; if (v == null || typeof v === 'number' || (typeof v === 'string' && v.length <= 4)) x[k] = v; } return x; };
  all.forEach(x => {
    const ch = {}; Object.keys(x.chan || {}).sort().forEach(k => { ch[k] = keep(x.chan[k]); });
    out[x.id] = { top: keep(x), chan: ch };
  });
  return out;
});
console.log(JSON.stringify(r)); await d.browser.close();
