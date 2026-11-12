import { open } from '/tmp/deploy/good7/tests/_common.mjs'; import fs from 'fs';
const {browser, page} = await open();
await page.waitForFunction(() => window.BOOK_READY === true, null, {timeout: 60000}).catch(() => {});
const r = await page.evaluate(() => { const all = [...AUTO_REGIMES, ...LB_HIST]; const ab = x => (typeof abOf === 'function' ? abOf(x) : x.abbr) || x.abbr;
  return all.map(x => { const club = ab(x), s = x.startDate, e = x.endDate || '9999'; let n = 0, net = 0;
    for(const [d, seats] of TRADE_BOOK.trades) for(const st of seats) if(st[0] === club && d >= s && d <= e){ n++; net += st[1]; }
    return [x.id, x.chan.trade.n, n, x.chan.trade.net, Math.round(net * 10) / 10]; }); });
fs.writeFileSync(process.env.OUT, JSON.stringify(r)); await browser.close();
