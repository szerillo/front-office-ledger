// Trades the release / free-agency rule closed (Nov 11): OPEN with PLAYER_MOVES hidden from the rule,
// CLOSED with it. Seeded 15 for a hand check (seed 20261121, LCG as audit_sample.mjs).
import { open } from '../_common.mjs';
const { browser, page } = await open();
await page.waitForFunction(() => typeof PLAYER_MOVES !== "undefined", null, {timeout: 120000});
const res = await page.evaluate(() => {
  const T = TRADE_BOOK.trades, out = [];
  const pm = PLAYER_MOVES;
  for(const [d, seats] of T){
    const a = folTradeOpen(seats, d);
    PLAYER_MOVES = {}; const b = folTradeOpen(seats, d); PLAYER_MOVES = pm;
    if(b && !a){
      // which live pieces the rule ended
      const ended = []; const nm = p => (typeof PLAYER_NAMES !== 'undefined' && PLAYER_NAMES[p]) || p;
      for(const s of seats) for(const [p] of (s[2] || [])){
        const ev = (pm[String(p)] || []).filter(m => m[0] > d).map(m => [m[0], typeof m[1] === 'number' ? PLAYER_MOVE_TYPES[m[1]] : m[1]])
          .filter(m => /^(Released|Declared Free Agency|Signed as Free Agent|Minor-league deal)$/.test(m[1]));
        if(ev.length && folGone(p) !== true) ended.push([String(p), nm(String(p)), ev[0][0], ev[0][1]]);
      }
      out.push({d, clubs: seats.map(s => s[0]).join('/'), ended});
    }
  }
  return out;
});
await browser.close();
console.log('closed by the rule', res.length); (await import('fs')).writeFileSync('/tmp/closed147.json', JSON.stringify(res));
let seed = 20261121; const idx = res.map((_, i) => i), pick = [];
while(pick.length < 15){ seed = (seed * 1103515245 + 12345) % 2147483648; pick.push(res[idx.splice(seed % idx.length, 1)[0]]); }
for(const p of pick.sort((a, b) => a.d < b.d ? -1 : 1)) console.log(JSON.stringify(p));
