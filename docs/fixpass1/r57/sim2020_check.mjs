// Round 57 (Nov 14 audit item 4): the simulator leaves winters across the 60-game 2020 season out of its comparable
// winters. Pass: no comparable winter has 2020 as its "before" or "after" season, 450 remain (480 less 30), and the
// "History's base rate" from the simulator's own comp rule (gmReport's distance formula, an empty winter) for each of
// the 30 clubs equals the reference file REF (base rates from the round 55 page, before the round 56 pacing), when given.
// Writes the 30 base rates to OUT when given. Exit 1 otherwise.
import { open, report } from './_common.mjs';
import fs from 'fs';
const d = await open();
const r = await d.page.evaluate(() => {
  const W = GMC.winters || [];
  const pick = prevW => W.map(x => ({x, d: Math.abs(x.prevW - prevW) / 10 + Math.abs(x.faM - 0) / 120 + Math.abs(x.faN - 0) / 2.5 + Math.abs(x.trN - 0) / 2.5})).sort((a, b) => a.d - b.d).slice(0, 5);
  const per = Object.fromEntries(Object.keys(DESK.teams || {}).sort().map(ab => { const c = pick((GMC.wins2026 || {})[ab] || 81); return [ab, +(c.reduce((a, y) => a + (y.x.nextW - y.x.prevW), 0) / c.length).toFixed(3)]; }));
  return {n: W.length, touch2020: W.filter(x => x.w === 2020 || x.w + 1 === 2020).length, per};
});
if (process.env.OUT) fs.writeFileSync(process.env.OUT, JSON.stringify(r.per));
const ref = process.env.REF ? JSON.parse(fs.readFileSync(process.env.REF, 'utf8')) : null;
const diff = ref ? Object.keys(ref).filter(k => ref[k] !== r.per[k]) : [];
console.log(JSON.stringify({n: r.n, touch2020: r.touch2020, clubs: Object.keys(r.per).length, refGiven: !!ref, differ: diff}));
report('sim2020_check', {no_2020_comps: r.touch2020 === 0, count_450: r.n === 450, thirty_clubs: Object.keys(r.per).length === 30, base_rates_match_reference: !ref || diff.length === 0}, d.errors);
await d.browser.close();
