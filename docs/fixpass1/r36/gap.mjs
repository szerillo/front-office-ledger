import { open } from '/tmp/deploy/good7/tests/_common.mjs';
const {browser, page} = await open(); await page.waitForFunction(() => window.BOOK_READY === true, null, {timeout: 60000}).catch(() => {});
console.log(JSON.stringify(await page.evaluate(() => { const all = [...AUTO_REGIMES, ...LB_HIST]; const ab = x => (typeof abOf === 'function' ? abOf(x) : x.abbr) || x.abbr;
  const W = {}; all.forEach(x => (W[ab(x)] = W[ab(x)] || []).push([x.startDate, x.endDate || '9999', x.id]));
  let none = [], two = []; for(const [d, seats] of TRADE_BOOK.trades) for(const st of seats){ if(d < '1998-01-01') continue; const h = (W[st[0]] || []).filter(([s, e]) => d >= s && d <= e); if(!h.length) none.push([d, st[0], st[1]]); if(h.length > 1) two.push([d, st[0], h.map(x => x[2])]); }
  return {noSeat: none.length, noSeatAbs: Math.round(none.reduce((a, x) => a + Math.abs(x[2]), 0) * 10) / 10, big: none.filter(x => Math.abs(x[2]) >= 1).slice(0, 12), twoSeats: two.length, twoEx: two.slice(0, 3)}; }))); await browser.close();
