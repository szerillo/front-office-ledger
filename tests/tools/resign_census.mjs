// Round 12 C (prereg d4be855): every trade the release / free-agency rule closes, recomputed with each
// "released or filed, then re-signed by the club that held him within 60 days" pair removed from the feed.
// A trade that reopens was closed only by a same-club re-sign.
import { open } from '../_common.mjs';
const { browser, page } = await open();
await page.waitForFunction(() => typeof PLAYER_MOVES !== "undefined", null, {timeout: 120000});
const r = await page.evaluate(() => {
  const PM = PLAYER_MOVES, ty = m => typeof m[1] === 'number' ? PLAYER_MOVE_TYPES[m[1]] : m[1];
  const clean = {};
  for (const [p, rows] of Object.entries(PM)) {
    const drop = new Set();
    rows.forEach((m, k) => {
      if (!/^(Released|Declared Free Agency)$/.test(ty(m))) return;
      const held = rows.slice(0, k).filter(x => x[3]).map(x => x[3]).pop();
      const j = rows.findIndex((x, i) => i > k && /^(Signed as Free Agent|Minor-league deal)$/.test(ty(x)));
      if (j > 0 && rows[j][3] === held && (new Date(rows[j][0]) - new Date(m[0])) / 864e5 <= 60) { drop.add(k); drop.add(j); }
    });
    clean[p] = drop.size ? rows.filter((_, i) => !drop.has(i)) : rows;
  }
  const out = [];
  for (const [d, seats] of TRADE_BOOK.trades) {
    const now = folTradeOpen(seats, d);
    PLAYER_MOVES = {}; const noRule = folTradeOpen(seats, d); PLAYER_MOVES = PM;
    if (now || !noRule) continue;                      // only trades the release rule closes
    PLAYER_MOVES = clean; const fixed = folTradeOpen(seats, d); PLAYER_MOVES = PM;
    if (fixed) out.push([d, seats.map(s => s[0]).join('/')]);
  }
  return out;
});
await browser.close();
console.log('closed by the release rule only because of a same-club re-sign:', r.length);
for (const x of r) console.log(' ', x.join(' '));
