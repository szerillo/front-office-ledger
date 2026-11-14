// Round 55 (Nov 14 audit, item 7): the methodology's stated split-half numbers equal its chart's data (METHOD_VIZ.rel,
// 2 decimals), and its stated channel weights equal the weights the grades use (relWeights(), 2 decimals), which follow
// from the chart by 0.5 + 0.5 x Spearman-Brown. Also: no channel above 0.2 is described as showing no persistence.
// Pass: every data-relr and data-relw number matches; 5 relr and 5 relw present. Exit 1 otherwise.
import { open, report } from './_common.mjs';
const d = await open();
const r = await d.page.evaluate(() => {
  const rel = Object.fromEntries(METHOD_VIZ.rel.map(([n, v]) => [n, v])), W = relWeights(), bad = [];
  const relr = [...document.querySelectorAll('[data-relr]')], relw = [...document.querySelectorAll('[data-relw]')];
  relr.forEach(e => { const k = e.dataset.relr; if (rel[k] == null || (+e.textContent).toFixed(2) !== rel[k].toFixed(2)) bad.push('r ' + k + ' ' + e.textContent + ' vs ' + rel[k]); });
  relw.forEach(e => { const k = e.dataset.relw; const want = +W[k].toFixed(2); if (+e.textContent !== want) bad.push('w ' + k + ' ' + e.textContent + ' vs ' + W[k]); const rr = {draft: 'Draft', fa: 'Free agency', ext: 'Extensions', waiver: 'Waivers', trade: 'Trades'}[k];
    const f = rel[rr] > 0 ? 0.5 + 0.5 * Math.min(1, 2 * rel[rr] / (1 + rel[rr])) : 0.5; if (Math.abs(f - W[k]) > 0.001) bad.push('formula ' + k); });
  const txt = document.getElementById('view-method') ? document.getElementById('view-method').textContent : document.body.textContent;
  const m = txt.match(/([^.;]*)show no measurable persistence/); const named = m ? m[1] : '';
  Object.entries(rel).forEach(([n, v]) => { if (v > 0.2 && new RegExp(n, 'i').test(named)) bad.push(n + ' above 0.2 called not persistent'); });
  return {nr: relr.length, nw: relw.length, bad};
});
console.log(JSON.stringify(r));
report('method_check', {relr_5: r.nr === 5, relw_5: r.nw === 5, mismatches_0: r.bad.length === 0}, d.errors);
await d.browser.close();
