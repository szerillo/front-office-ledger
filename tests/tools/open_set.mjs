// every trade folTradeOpen reads OPEN on a page (PAGE= or TARGET=live), to diff two pages
import { open } from '../_common.mjs';
const { browser, page } = await open();
await page.waitForFunction(() => typeof PLAYER_MOVES !== "undefined", null, {timeout: 120000});
const r = await page.evaluate(() => TRADE_BOOK.trades.filter(([d, s]) => folTradeOpen(s, d)).map(([d, s]) => d + ' ' + s.map(x => x[0]).join('/')));
await browser.close();
(await import('fs')).writeFileSync(process.env.OUT, JSON.stringify(r));
console.log('OPEN trades', r.length);
