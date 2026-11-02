// v5.9: no view may depend on what was drawn before it. Every routable view
// is rendered for every entity twice, once right after its richest sibling
// and once right after its emptiest, and the two must read identically. Also:
// no decision row sits on two regimes of the same club, and no row is dated
// outside its regime's window. Slow (several minutes) by design.
import { open, report } from './_common.mjs';
const d = await open({width: 1360, height: 900}); const p = d.page;
p.setDefaultTimeout(0);
const r = await p.evaluate(() => {
  ['h2h', 'horizon', 'trees', 'gm', 'dna'].forEach(v => { try { switchView(v); } catch(e){} });
  const opts = id => { const el = document.getElementById(id); return el ? [...el.options].map(o => o.value).filter(Boolean) : []; };
  const views = { cards: opts('teamsel'), champions: ALL_CHAMPS().map(c => c.id), scenarios: scAll().map(s => s.id),
    h2h: opts('h2hsel'), horizon: opts('hz-club').map(x => x.toLowerCase()), trees: opts('treesel'),
    boards: ['fa', 'pros', 'farm'], desk: ['trade', 'fa', 'ext', 'draft'], simulator: opts('gm-club').map(x => x.toLowerCase()) };
  const txt = () => { const el = document.querySelector('[id^="view-"]:not([hidden])'); return el ? el.innerText.replace(/\s+/g, ' ') : ''; };
  const go = (v, id) => { routeApply('#view=' + v + '&id=' + encodeURIComponent(id)); return txt(); };
  const o = {};
  for(const [v, ids] of Object.entries(views)){
    const lens = ids.map(id => [id, go(v, id).length]).sort((a, b) => b[1] - a[1]);
    const rich = lens[0][0], poor = lens[lens.length - 1][0];
    o['orderIndependent_' + v] = ids.length > 0 && ids.every(id => { go(v, rich); const a = go(v, id); go(v, poor); return a === go(v, id); });
  }
  normalizeCurated();
  const cards = [...AUTO_REGIMES, ...LB_HIST.filter(x => x.realCard)];
  const sig = {}; let outside = 0;
  cards.forEach(c => { const st = (c.startDate || (c.start + '-01-01')).slice(0, 10), en = (c.endDate || '9999-12-31').slice(0, 10);
    Object.entries(c.allx || {}).forEach(([k, rows]) => (rows || []).forEach(x => { const dd = String(x[0]).slice(0, 10);
      (sig[k + '|' + dd + '|' + x[1]] = sig[k + '|' + dd + '|' + x[1]] || []).push(c);
      if(dd < st && !(k === 'draft' && dd.slice(0, 4) === st.slice(0, 4) && dd >= st.slice(0, 4) + '-06-01') || dd > en) outside++; }));
    (c.h2h || []).forEach(pp => (pp.deals || []).forEach(dl => { if(dl.d < st || dl.d > en) outside++; })); });
  o.noRowOnTwoRegimesOfOneClub = Object.values(sig).every(cs => new Set(cs.map(c => c.team)).size === cs.length);
  o.noRowOutsideItsWindow = outside === 0;
  return o; });
await d.browser.close();
report('t_leak', r, d.errors);
