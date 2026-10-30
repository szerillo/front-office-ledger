// GM economics guard rails. Every check encodes a bug that actually shipped
// once: the Witt-for-Soto fantasy trade, the 2-for-30-beats-1-for-29
// negotiation exploit, the counter-echo loop, book money staying on the
// payroll after a trade, arb awards priced off the valuation projection.
import { open, report } from './_common.mjs';
const { browser, page, errors } = await open();
const r = await page.evaluate(() => {
  const out = {};
  switchView('gm');
  const g = n => DESK.players.find(x => x[0] === n);
  // surplus trade logic
  const witt = g('Bobby Witt Jr.'), soto = g('Juan Soto');
  out.wittFranchise = gmFranchise(witt) === true;
  out.wittSurplusBig = gmSurplus(witt) > 10;
  out.sotoSurplusNeg = gmSurplus(soto) < 0;
  // FA anchors (media-range sanity, wide bands)
  const sug = n => { const p = g(n); if(!p) return null; const s = dkSuggest(p, 'fa', null); return [s.sugYrs, s.sugTot]; };
  const ch = sug('Jazz Chisholm Jr.'); out.chisholmBand = !!ch && ch[1] >= 70 && ch[1] <= 170;
  const sk = sug('Tarik Skubal'); out.skubalBand = !!sk && sk[1] >= 300 && sk[1] <= 500;
  // class reality
  out.contrerasControlled = !gmIsFA(g('William Contreras'));
  out.kingInClass = gmIsFA(g('Michael King'));
  out.ryanControlled = !gmIsFA(g('Joe Ryan'));
  // negotiation: extra years are not free money
  document.getElementById('gm-club').value = 'NYM'; gmStart();
  gmState.stage = 2; gmState.open.tab = 'fa'; gmShow();
  const pool = DESK.players.filter(p => gmIsFA(p)).sort((a, b) => gmProj27(b) - gmProj27(a)).slice(0, 60);
  const asks = pool.map(x => ({x, n: gmNegState(x, false)}));
  gmShow();
  const one = asks.filter(o => o.n.ask.yrs === 1).sort((a, b) => b.n.ask.tot - a.n.ask.tot)[0];
  if(one){
    document.getElementById('gm-ny-' + one.x[1]).value = 2;
    document.getElementById('gm-nt-' + one.x[1]).value = one.n.ask.tot + 1;
    gmOffer(one.x[1], 0);
    out.twoYearTrickRejected = gmState.neg[one.x[1]].done === false;
    document.getElementById('gm-ny-' + one.x[1]).value = 1;
    document.getElementById('gm-nt-' + one.x[1]).value = gmState.neg[one.x[1]].ask.tot;
    gmOffer(one.x[1], 0);
    out.honestOfferSigns = gmState.neg[one.x[1]].done === true;
  }
  // payroll: book money leaves with a traded player
  document.getElementById('gm-club').value = 'NYM'; gmStart();
  const before = gmPayroll();
  gmState.outs.add(soto[1]);
  out.payrollDropsOnTrade = before - gmPayroll() > 30;
  // arb is backward-looking: at least some non-tender candidates exist
  const dpw0 = DESK.market.dpw['2027'];
  let nt = 0;
  for(const ab of Object.keys(DESK.teams)){
    for(const q of DESK.players.filter(p => p[2] === ab && gmControlled(p) && (hzBookEnd()[p[1]] || 0) < 2027
        && (p[11] || 0) >= 3 && (p[11] || 0) < 6 && Math.abs(p[5]) + Math.abs(p[6]) + Math.abs(p[7]) >= 0.6)){
      const sal = gmArbSal(q, 2027);
      if(sal > (dkProjSeasons(q, 1, false).per[0] || 0) * dpw0 * 0.85 && sal >= 3) nt++;
    }
  }
  out.nonTendersExist = nt >= 25;
  return out;
});
report('t_gm_core', r, errors);
await browser.close();
