// Nov 11 launch push: OPEN and CLOSED from the facts, the prospect-value note,
// battle card best and worst moves, the player career card, the weekly board
import { open, report } from './_common.mjs';
const {browser, page, errors} = await open();
const r = await page.evaluate(async () => {
  const out = {};
  const flat = t => { const a = []; const f = n => { a.push(n); (n.kids || []).forEach(f); }; f(t); return a; };
  const mo = flat(careerTree('666624'));
  out.morelMiaClosed = mo.some(n => /2025-12-18 · signed with MIA/.test(n.via || '') && n.status === 'closed');
  const mia = AUTO_REGIMES.find(x => x.id === 'mia');
  out.morelCardClosed = [...(mia.chanLedgers.fa.best || []), ...(mia.chanLedgers.fa.worst || [])].filter(x => /Morel/.test(x.h)).every(x => x.open === false);
  const ho = flat(careerTree('605280'));
  const tr = ho.find(n => /2026-08-03 · traded NYM to CHC/.test(n.via || ''));
  out.holmesTradeOpen = !!tr && tr.status === 'open';
  out.holmesProspectNote = !!tr && /prospect value/.test(tr.nm || '');
  out.holmesNymSigningClosed = ho.some(n => /signed with NYM/.test(n.via || '') && n.status === 'closed');
  // no decision before 2021 was reopened without a reason, and a played-out one-year deal is closed
  let reopened = 0, oneYrOpen = 0, tradeReopened = 0, bettsOpen = true, hendersonOpen = true, judgeClosed = true;
  const seen = new Set();
  const walk = (x, d) => { if(!x || typeof x !== 'object' || d > 7 || seen.has(x)) return; seen.add(x);
    if(Array.isArray(x)){ x.forEach(y => walk(y, d + 1)); return; }
    if(x.d && x.h && typeof x.open === 'boolean'){ if(x.open && x.open0 === false && !/^trade$/i.test(x.ch || x.t || '')){ const pr = (x.pids || []).map(p => { folGone(p); return folGone._m && folGone._m.get(String(p)); }).find(Boolean);
      const ok = (/^Extended/.test(x.h) && (x.sides || []).some(y => y[0] === 'Still to come')) || (/^(Drafted|Int'l amateur)/.test(x.h) && pr && gmSvc(pr) < 6); if(!ok) reopened++; }
      if(/^Extended Mookie Betts/.test(x.h)) bettsOpen = bettsOpen && x.open; if(/^Drafted Gunnar Henderson/.test(x.h)) hendersonOpen = hendersonOpen && x.open; if(/^Drafted Aaron Judge/.test(x.h)) judgeClosed = judgeClosed && !x.open; if(x.open && x.open0 === false && /^trade$/i.test(x.ch || x.t || '')) tradeReopened++; if(x.open && /1 yr \/ \$[\d.]+M \(202[0-5]-\d\d winter\)/.test(x.h)) oneYrOpen++; }
    for(const k in x){ if(x[k] && typeof x[k] === 'object') walk(x[k], d + 1); } };
  [...REGIMES, ...AUTO_REGIMES, ...LB_HIST].forEach(x => walk(x, 0));
  // only for a stated reason: an extension still running with the club (Betts, 2020),
  // or a pre-2021 draft or international signing still in his control years
  out.noneReopened = reopened === 0;
  out.preCutoffStillRunningOpen = bettsOpen && hendersonOpen;
  out.preCutoffControlOverClosed = judgeClosed;
  out.tradesReopenedFew = tradeReopened < 40;
  out._tradeReopened = tradeReopened;
  out.playedOutOneYearClosed = oneYrOpen === 0;
  // battle card
  btState.a = 'lad'; btState.b = 'nym'; switchView('h2h'); renderBattle();
  const bt = document.getElementById('bt-card').innerText;
  out.battleBestWorst = /BEST MOVE/i.test(bt) && /WORST MOVE/i.test(bt) && /Got Josh Fields for Yordan Alvarez/.test(bt);
  // career card
  treeOverlay('605141', 'LAD');
  const cc = document.getElementById('cc-605141');
  out.careerCard = !!cc && /BOS/.test(cc.innerText) && /LAD/.test(cc.innerText) && /extension is graded on its own/.test(cc.innerText);
  closeTreeOverlay();
  // audit fixes: a Rule 5 grade no longer stands in for a trade's net; one deal, one tree node;
  // a flipped piece keeps a trade open; the giving side names where the value went
  const ix = tbIndex().all;
  const rom = (ix['605447'] || []).find(e => e.d === '2018-12-13');
  out.rule5ConduitSign = !!rom && rom.seats.every(st => !(st[2].length === 0 && st[3].length && seatNet(st, rom.d) > 0));
  const jd = flat(careerTree('518626')).filter(n => /2022-03-1\d · traded MIN to NYY/.test(n.via || ''));
  out.oneNodePerDeal = jd.length === 1;
  const cws = AUTO_REGIMES.find(x => x.id === 'cws');
  const hou = [...cws.chanLedgers.trade.best, ...cws.chanLedgers.trade.worst].find(x => /Adrian Houser/.test(x.h));
  out.flippedPiecesKeepOpen = !hou || hou.open === true;
  const tor = AUTO_REGIMES.find(x => x.id === 'tor');
  const ol = [...tor.chanLedgers.trade.best, ...tor.chanLedgers.trade.worst].find(x => /Otto Lopez/.test(x.h));
  out.valueWhereverLabel = !ol || ol.sides.some(sd => /wherever he played/.test(sd[0]));
  // block 3: an extension whose seasons have not started is OPEN; linked same-day legs keep
  // their own numbers; a deal missing players on a side is held back on the tree
  const chc = AUTO_REGIMES.find(x => x.id === 'chc');
  const hoE = [...(chc.chanLedgers.ext.best || []), ...(chc.chanLedgers.ext.worst || [])].find(x => /Nico Hoerner · 6 yr/.test(x.h));
  out.unstartedExtensionOpen = !!hoE && hoE.open === true;
  const sx = String(Object.keys(ix).find(p => pName(p) === 'Richie Sexson'));
  const sxe = (ix[sx] || []).find(e => e.d === '2003-11-28');
  out.linkedLegsAddToZero = !!sxe && Math.abs(sxe.seats.reduce((a, st) => a + seatNet(st, sxe.d), 0)) < 0.15;
  const bd = String(Object.keys(ix).find(p => pName(p) === 'Erik Bedard'));
  out.incompleteDealHeldBack = flat(careerTree(bd)).some(n => /2011-07-31/.test(n.via || '') && n.wv == null && /held back/.test(n.nm || ''));
  // weekly board
  const html = folWeekBoard();
  out.weekBoard = /This week/.test(html) && (html.match(/wk-day/g) || []).length === 7;
  out.noEmDash = !/\u2014/.test(bt + (cc ? cc.innerText : '') + html);
  return out;
});
// deal comps: inline on the working page, fetched after load on the deployed page;
// either way the Deal Desk finds real comparable trades
r.dealsLazy = await page.evaluate(async () => {
  for(let i = 0; i < 40 && !dkDealsReady(); i++){ dkDealsLoad(); await new Promise(z => setTimeout(z, 250)); }
  const inline = !window.DESK_DEALS_SRC;
  return dkDealsReady() && DESK.deals.length > 1000 && dkComps(3, 3, '3+', 'c', '', '').length > 0 && (inline || [...document.scripts].some(x => /deals\.js/.test(x.src)));
});
// comps arriving after an Assistant GM note is on screen keep the note (live race, Nov 11)
r.agmNoteSurvivesComps = await page.evaluate(async () => {
  if(!window.DESK_DEALS_SRC) return true;
  DESK.deals = null; dkDealsLoad._p = 0; switchView('desk');
  const rb = Object.keys(DESK.teams).filter(ab => folPosture(ab).key === 'rebuilding'), ct = Object.keys(DESK.teams).filter(ab => folPosture(ab).key === 'contender');
  dkState.you = rb[0]; dkState.them = ct[0]; dkState.recv = []; dkState.send = []; renderDesk(); dkAgm();
  for(let i = 0; i < 40 && !dkDealsReady(); i++) await new Promise(z => setTimeout(z, 250));
  await new Promise(z => setTimeout(z, 300));
  return /Assistant GM/.test((document.getElementById('dk-agm-note') || {}).textContent || '');
});
report('t_nov11', r, errors);
await browser.close();
