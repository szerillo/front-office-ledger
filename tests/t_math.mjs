// v5.1 full-site math audit, encoded: every check here was a real defect
// found by the November 2026 audit (or a number a user questioned).
import { open, report } from './_common.mjs';
const d = await open();
const r = await d.page.evaluate(async () => {
  const o = {};
  // arbitration: service time from the transaction feed, calibrated awards
  const pl = nm => DESK.players.find(x => x[0] === nm);
  const baty = pl('Brett Baty'), alv = pl('Francisco Alvarez');
  o.batyFirstArb = gmArbNo(baty, 2027) === 1 && gmArbSal(baty, 2027) < 5;          // was $12.0M at the 3rd-award ratio
  o.alvarezSecondArb = gmArbNo(alv, 2027) === 2 && gmArbSal(alv, 2027) < 8;        // was $14.4M
  o.serviceIsReal = Math.abs(gmSvc(pl('Bobby Witt Jr.')) - 5.0) < 0.01 && gmSvc(pl('Paul Skenes')) < 2.3;
  o.stephensonIsFA = gmIsFA(pl('Tyler Stephenson'));                               // old proxy fix wrongly held him back
  o.qoIsReal = GM_QO === 23.15;
  // one net figure per regime, one grade rule for every card
  $('#erasel').value = 'active';
  const rows = lbRows();
  o.forGradeFollowsRule = rows.every(x => x.forGrade === gradeComp(x.net / x.seasons));
  o.reportTileMatchesLeaderboard = rows.every(x => { renderReport(x.id); const m = document.querySelector('#rc-tiles').innerText.match(/Net value vs\. expectation\s*([+\-]?\d+\.\d)/); return m && Math.abs(+m[1] - x.net) <= 0.15; });
  o.retentionNotRunaway = AUTO_REGIMES.every(x => Math.abs((x.chan.ret && x.chan.ret.net2) || 0) < 60);   // NYY had +133 from re-signings
  // champions: biggest channel is the biggest; computed card is canonical
  o.champBiggest = ALL_CHAMPS().every(c => { renderChamp(c.id); const t = document.querySelector('#view-champs').innerText; const m = t.match(/Biggest channel\s*\n?\s*([^\n]+?)\s*\d+% of core WAR/);
    const mix = {}; (c.roster||[]).forEach(x => { const k = x[4]==='inh' ? 'inherited' : x[1]; mix[k] = (mix[k]||0) + x[5]; });
    const big = Object.keys(mix).filter(k=>CHAMP_CH[k]).sort((a,b)=>mix[b]-mix[a])[0]; return !m || !big || m[1].trim() === CHAMP_CH[big].name; });
  const tex = ALL_CHAMPS().find(c => c.id === 'tex23');
  o.rangersOneLedger = tex && tex.computed === true && !!tex.story;
  // head to head: two seats of one trade mirror each other
  const all = [...REGIMES, ...AUTO_REGIMES].filter(x => x.h2h); const map = {};
  all.forEach(x => (x.h2h||[]).forEach(q => { map[abOf(x) + '|' + q.opp] = q; }));
  o.h2hSymmetric = Object.entries(map).every(([k, q]) => { const [a, b] = k.split('|'); const w = map[b + '|' + a]; return !w || (Math.abs(q.net + w.net) <= 0.25 && q.n === w.n); });
  o.h2hAllSeats = all.length === 30;
  // payroll: the salary book closes to every payroll widget
  o.salaryBookCloses = Object.keys(DESK.teams||{}).every(ab => { const dv = document.createElement('div'); dv.innerHTML = moneyTable(ab);
    const tr = [...dv.querySelectorAll('tr')].find(t => /Committed \+ estimated/.test(t.innerText)); const t27 = tr ? +tr.cells[3].innerText.replace(/[^\d.\-]/g,'') : NaN;
    return Math.abs(t27 - ((((DESK.payroll||{})[ab]||{})['2027']||[0])[0] + dkArbEstimate(ab, 2027).est)) <= 1.0; });
  o.horizonNoOwnFAs = Object.keys(DESK.teams||{}).every(ab => hzRows(ab).live.every(x => !gmIsFA(x.p)));
  o.noControlledVeterans = DESK.players.every(q => !(gmSvc(q) >= 6 && gmControlled(q) && (hzBookEnd()[q[1]]||0) < 2027));
  // trees: every player chain builds; every trade line closes; no phantom seats
  const names = Object.assign({}, TRADE_BOOK.names, PLAYER_NAMES);
  const pidOf = nm => Object.keys(names).find(k => names[k] === nm);
  o.treesBuild = ['William Contreras','Ozzie Albies','Garrett Whitlock','Mookie Betts','Juan Soto','Francisco Lindor'].every(nm => { try { const t = tnode(careerTree(pidOf(nm))).replace(/<[^>]+>/g,''); return !/undefined|NaN|null/.test(t); } catch(e) { return false; } });
  const betts = tnode(careerTree(pidOf('Mookie Betts'))).replace(/<[^>]+>/g,' ');
  o.bettsOrigin = /drafted by BOS/.test(betts); o.bettsBothSeats = /BOS\s+\(Chaim Bloom\) got/.test(betts) && /LAD\s+\(Andrew Friedman\) got/.test(betts); o.bettsPieces = /Verdugo/.test(betts) && /Weissert/.test(betts); o.bettsExtension = /12 yr/.test(betts);
  o.tradeLinesClose = TRADE_BOOK.trades.every(([dt, seats]) => seats.every(s => Math.abs(s[2].reduce((a,x)=>a+x[1],0) - s[3].reduce((a,x)=>a+x[1],0) - s[1]) <= 0.25));
  const lindor = TRADE_BOOK.trades.find(([dt, seats]) => dt === '2021-01-07' && seats.some(s => s[0] === 'NYM'));
  o.lindorBothSeats = !!lindor && lindor[1].length === 2;
  o.curatedCardsHaveTrees = REGIMES.every(x => bookTreesFor(x).length >= 3);
  const hal = TRADE_BOOK.trades.find(([dt, seats]) => dt === '2009-12-16' && seats.some(st => st[0] === 'TOR'));
  o.halladayReturnRecovered = !!hal && hal[1].find(st => st[0] === 'TOR')[2].length >= 3;          // was "Toronto got nothing"
  o.noPassThroughSeats = TRADE_BOOK.trades.every(([dt, seats]) => seats.every(st => !st[2].some(x => st[3].some(y => y[0] === x[0]))));
  o.curatedOnEngine = REGIMES.every(x => !!x.chanLedgers && Math.abs(lbRows().find(y => y.id === x.id).net - (CHANNELS.reduce((a,c)=>a+((x.chan[c.key]||{}).net||0),0) + ((x.chan.ret&&x.chan.ret.net2)||0))) < 0.15);
  // simulator: extend then trade leaves no ghost money; the salary tab agrees with the rail
  switchView('gm'); document.getElementById('gm-club').value = 'SEA'; gmStart();
  const woo = DESK.players.find(q => q[0] === 'Bryan Woo' && q[2] === 'SEA');
  if(woo){
    const before = gmPayroll();
    gmExtend(woo[1], 5, 100, 'arb'); gmExtend(woo[1], 5, 100, 'arb');
    o.extendOnce = gmState.moves.filter(m => m.kind === 'ext').length === 1;
    gmState.outs.add(woo[1]); gmState.moves.filter(m => m.kind === 'ext' && m.pid === woo[1]).forEach(m => { m.kind = 'info'; m.aav = 0; m.surplus = 0; });
    const prior = (hzBookEnd()[woo[1]]||0) >= 2027 ? gmBookAAVFor(woo, 2027) : (gmArbSal(woo, 2027) || 0);
    o.extendThenTradeNoGhost = Math.abs(gmPayroll() - (before - prior)) < 0.6;
  }
  gmStart();
  const dv = document.createElement('div'); dv.innerHTML = moneyTable('SEA', true);
  const tr = [...dv.querySelectorAll('tr')].find(t => /Committed \+ estimated/.test(t.innerText));
  o.salaryTabMatchesRail = !!tr && Math.abs(+tr.cells[3].innerText.replace(/[^\d.\-]/g,'') - gmPayroll()) <= 1.0;
  // no negative zero or broken text on any tab
  let bad = [];
  for(const v of ['leaderboard','report','trees','champs','method','dna','h2h','desk','horizon','scen','gm']){
    switchView(v); await new Promise(z => setTimeout(z, 200));
    const t = document.querySelector('#view-' + v).innerText;
    if(/-0\.0(?!\d)|NaN|undefined|\[object|\$-\d/.test(t)) bad.push(v);
  }
  o.cleanText = bad.length === 0;
  return o;
});
await d.browser.close();
report('t_math', r, d.errors);
