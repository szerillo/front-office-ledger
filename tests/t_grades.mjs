// Grade snapshot (Nov 11): every trade side's shown net and every card row's number, compared with
// tests/fixtures/grades.json. The other suites check behaviour and selected cases; none would notice
// one wrong grade on an untested move (a planted +2.0 on a 2018 trade passed all 13). Any change in a
// grade fails here until the fixture is regenerated on purpose:
//   UPDATE=1 node tests/t_grades.mjs     (after an intended engine or data change; say why in the commit)
import fs from 'fs';
import { open, report } from './_common.mjs';
const FIX = new URL('./fixtures/grades.json', import.meta.url).pathname;
const {browser, page, errors} = await open();
const now = await page.evaluate(() => {
  const out = {}, ix = tbIndex().all, seen = new Set();
  for(const p in ix) for(const e of ix[p]){
    const k = e.d + '|' + e.seats.map(s => s[0]).join('/'); if(seen.has(k)) continue; seen.add(k);
    e.seats.forEach((s, i) => { out['t|' + k + '|' + i + s[0]] = e.incomplete || s.incomplete ? 'held' : seatNet(s, e.d).toFixed(1); });
  }
  const seen2 = new Set();
  const walk = (o, reg, d) => { if(!o || typeof o !== 'object' || d > 7 || seen2.has(o)) return; seen2.add(o);
    if(Array.isArray(o)){ o.forEach(x => walk(x, reg, d + 1)); return; }
    if(o.d && o.h && typeof o.war === 'number') out['c|' + reg + '|' + o.d + '|' + String(o.h).slice(0, 60)] = o.war.toFixed(1);
    for(const k in o){ const v = o[k]; if(v && typeof v === 'object') walk(v, reg, d + 1); } };
  [...(typeof REGIMES !== 'undefined' ? REGIMES : []), ...AUTO_REGIMES, ...LB_HIST].forEach(r => walk(r, abOf(r), 0));
  return out;
});
await browser.close();
if(process.env.UPDATE === '1'){
  fs.writeFileSync(FIX, JSON.stringify(now));
  console.log('t_grades fixture written:', Object.keys(now).length, 'grades'); process.exit(0);
}
const was = JSON.parse(fs.readFileSync(FIX, 'utf8'));
const changed = Object.keys(was).filter(k => k in now && now[k] !== was[k]);
const gone = Object.keys(was).filter(k => !(k in now)), added = Object.keys(now).filter(k => !(k in was));
changed.slice(0, 10).forEach(k => console.log('changed', k, was[k], '->', now[k]));
gone.slice(0, 5).forEach(k => console.log('missing', k)); added.slice(0, 5).forEach(k => console.log('new', k));
report('t_grades', {gradesUnchanged: changed.length === 0, noneMissing: gone.length === 0, noneAdded: added.length === 0, _counted: Object.keys(now).length, _changed: changed.length}, errors);
