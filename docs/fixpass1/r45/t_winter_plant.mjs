// Round 45 challenge C (planted, not one of the 19 suites): the t_winter "named report" exception assumes a
// TRADE_RUMORS row is current and about the player's CURRENT club. Rows carry no date and dkRumor() keys on the
// player id only. Plant: move a reported player to a contending club (a trade after the report) and keep his row.
// A correct rule should no longer accept the old report; this test passes only if it does not.
import { open, report } from './_common.mjs';
const d = await open();
const r = await d.page.evaluate(() => {
  const o = {};
  const availOk = L => L.every(x => !(gmFranchise(x.p) && gmClubPosture(x.ab) !== 'rebuilding') || !!x.rep);
  const rep = TRADE_RUMORS.rows.map(row => DESK.players.find(q => q[1] === row[0])).filter(q => q && q[2]);
  const contender = Object.keys(DESK.teams).find(ab => gmClubPosture(ab) !== 'rebuilding');
  // a reported player who would be franchise core on the contending club
  const cand = rep.find(q => { const c = q.slice(); c[2] = contender; return gmFranchise(c) && q[2] !== contender; });
  o.found = !!cand && !!contender;
  if(cand){
    const moved = cand.slice(); moved[2] = contender;            // traded after the report was filed
    const r0 = dkRumor(moved[1]);                                  // still returns the old club's report
    o.oldReportStillAttached = !!r0;
    o.who = moved[0] + ' (report about ' + cand[2] + ', now on ' + contender + ')';
    o.staleReportRejected = !availOk([{p: moved, ab: contender, rep: r0}]);   // correct behaviour: reject
  }
  return o;
});
console.log(JSON.stringify(r));
report('t_winter_plant', {found: r.found, staleReportRejected: r.staleReportRejected}, d.errors);
await d.browser.close();
