// Round 56 (Nov 14 audit item 3): the next-five-years ranks are the same on every load. Pass: (a) two loads with the
// live transaction feed on, one of them computing the ranks before the feed arrives, give identical ranks for all 30
// clubs and 5 seasons once the feed is applied; (b) applying the feed starts the ranking over (no rank kept from
// before the feed); (c) reversing the club order gives the same ranks (tie-break). Exit 1 otherwise.
import { open, report } from './_common.mjs';
process.env.LIVE_FEED = '1';
const get = async (early) => {
  const d = await open();
  if (early) await d.page.evaluate(() => { try { window.__early = JSON.stringify(hzLeague().rows.map(r => r.rk)); } catch(e){} });
  await d.page.waitForFunction(() => typeof LIVE !== 'undefined' && LIVE.ok, null, {timeout: 60000}).catch(() => {});
  const r = await d.page.evaluate(() => {
    const ranks = L => Object.fromEntries(L.rows.map(r => [r.ab, r.rk.join(',')]));
    const a = ranks(hzLeague()), m1 = hzLeague();
    liveApply([]); const reset = hzLeague() !== m1;
    const keys = Object.keys(DESK.teams), saved = {}; keys.forEach(k => { saved[k] = DESK.teams[k]; delete DESK.teams[k]; }); keys.reverse().forEach(k => DESK.teams[k] = saved[k]);
    hzLeague._m = null; const rev = ranks(hzLeague());
    keys.reverse().forEach(k => { delete DESK.teams[k]; }); Object.keys(saved).forEach(k => DESK.teams[k] = saved[k]); hzLeague._m = null;
    return {a, reset, revSame: JSON.stringify(Object.entries(rev).sort()) === JSON.stringify(Object.entries(a).sort()), live: LIVE.ok, early: !!window.__early};
  });
  await d.browser.close(); return r;
};
const x = await get(false), y = await get(true);
const diff = Object.keys(x.a).filter(k => x.a[k] !== y.a[k]);
console.log('feed applied', x.live, y.live, 'early computed', y.early, 'differing clubs', diff.slice(0, 5));
report('hz_check', {feed_on: x.live && y.live, two_loads_same: diff.length === 0 && Object.keys(x.a).length === 30, feed_restarts_ranking: x.reset && y.reset, tie_break_same: x.revSame && y.revSame}, []);
