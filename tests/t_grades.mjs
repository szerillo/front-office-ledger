// Grade snapshot (Nov 11): every trade side's shown net and every card row's number, compared with
// tests/fixtures/grades.json. The other suites check behaviour and selected cases; none would notice
// one wrong grade on an untested move (a planted +2.0 on a 2018 trade passed all 13). Any change in a
// grade fails here until the fixture is regenerated on purpose:
//   UPDATE=1 REASON="why" node tests/t_grades.mjs   (after an intended change; the diff and the reason are
//   appended to docs/grade-changes.md, and the run refuses without a reason)
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
if(process.env.DUMP) fs.writeFileSync(process.env.DUMP, JSON.stringify(now));   // Nov 11: dump for attribution
if(process.env.UPDATE === '1'){
  // regeneration leaves a record: every grade that moved, by how much, the commit and the reason,
  // appended to docs/grade-changes.md, so no grade changes without a stated cause
  const reason = (process.env.REASON || '').trim();
  if(reason.length < 15){ console.log('t_grades: set REASON="why these grades change" (15+ characters) to regenerate'); process.exit(1); }
  let was = {}; try { was = JSON.parse(fs.readFileSync(FIX, 'utf8')); } catch(e){}
  const moved = Object.keys(now).filter(k => k in was && now[k] !== was[k]).map(k => [k, was[k], now[k], (+now[k] - +was[k])]);
  const gone = Object.keys(was).filter(k => !(k in now)), added = Object.keys(now).filter(k => !(k in was));
  moved.sort((a, b) => Math.abs(b[3] || 0) - Math.abs(a[3] || 0));
  let commit = process.env.COMMIT || '';
  if(!commit){ try { commit = (await import('child_process')).execSync('git rev-parse --short HEAD', {cwd: new URL('..', import.meta.url).pathname}).toString().trim(); } catch(e){ commit = 'unknown'; } }
  const stamp = new Date().toISOString().slice(0, 16).replace('T', ' ') + ' UTC';
  const lines = [`\n## ${stamp} · page built on ${commit}`, '', `Reason: ${reason}`, '',
    `${moved.length} grades moved, ${added.length} new, ${gone.length} removed (of ${Object.keys(now).length}).`];
  if(moved.length){ lines.push('', '| Grade | Was | Now | Change |', '|---|---|---|---|');
    moved.slice(0, 40).forEach(([k, a, b, d]) => lines.push(`| ${k.replace(/\|/g, ' / ')} | ${a} | ${b} | ${isFinite(d) ? (d > 0 ? '+' : '') + d.toFixed(1) : ''} |`));
    if(moved.length > 40) lines.push('', `(${moved.length - 40} smaller moves not listed)`); }
  [['New', added], ['Removed', gone]].forEach(([lab, L]) => { if(L.length) lines.push('', lab + ': ' + L.slice(0, 15).map(k => k.replace(/\|/g, ' / ')).join('; ') + (L.length > 15 ? ` and ${L.length - 15} more` : '')); });
  const LOG = new URL('../docs/grade-changes.md', import.meta.url).pathname;
  if(!fs.existsSync(LOG)) fs.writeFileSync(LOG, '# Grade changes\n\nEvery regeneration of tests/fixtures/grades.json, with what moved and why. Written by `UPDATE=1 REASON=... node tests/t_grades.mjs`.\n');
  fs.appendFileSync(LOG, lines.join('\n') + '\n');
  fs.writeFileSync(FIX, JSON.stringify(now));
  console.log(lines.join('\n')); console.log('t_grades fixture written:', Object.keys(now).length, 'grades; logged in docs/grade-changes.md'); process.exit(0);
}
const was = JSON.parse(fs.readFileSync(FIX, 'utf8'));
const changed = Object.keys(was).filter(k => k in now && now[k] !== was[k]);
const gone = Object.keys(was).filter(k => !(k in now)), added = Object.keys(now).filter(k => !(k in was));
changed.slice(0, 10).forEach(k => console.log('changed', k, was[k], '->', now[k]));
gone.slice(0, 5).forEach(k => console.log('missing', k)); added.slice(0, 5).forEach(k => console.log('new', k));
report('t_grades', {gradesUnchanged: changed.length === 0, noneMissing: gone.length === 0, noneAdded: added.length === 0, _counted: Object.keys(now).length, _changed: changed.length}, errors);
