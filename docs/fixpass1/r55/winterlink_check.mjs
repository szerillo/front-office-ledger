// Round 55 (Nov 14 audit, item 9): #view=winters&id= opens any winter, not just those with a share page.
// Pass: 5 winter ids without a share page (2007-chc, 2000-nyy, 2018-nyy, 2018-19-nyy season form, 2011-oak) each open
// with that winter first under "Shared with you"; a bad id shows the "No winter matches" note. Exit 1 on any miss.
// Usage: B=<site index url> node winterlink_check.mjs
import { open, report } from './_common.mjs';
const d = await open();
const base = process.env.B || 'http://127.0.0.1:8767/r55/tree/index.html';
const cases = [['2007-chc', '2007-chc'], ['2000-nyy', '2000-nyy'], ['2018-nyy', '2018-nyy'], ['2018-19-nyy', '2018-nyy'], ['2011-oak', '2011-ath'], ['1997-zzz', null]];
const res = {};
for (const [id, want] of cases) {
  const ctx = await d.browser.newContext(); const pg = await ctx.newPage(); await pg.route('**/statsapi.mlb.com/**', r => r.abort());
  await pg.goto(base + '?q=' + Date.now() + '#view=winters&id=' + id, {waitUntil: 'load'});
  await pg.waitForFunction(() => typeof OFFS !== 'undefined' && OFFS.rows, null, {timeout: 60000}).catch(() => {}); await pg.waitForTimeout(1500);
  const r = await pg.evaluate(() => { const v = document.getElementById('view-offs'); const kick = [...v.querySelectorAll('.home-kick')].find(k => /shared with you/i.test(k.textContent));
    const card = kick ? kick.nextElementSibling : null; return {focus: offState.focus, shared: !!kick, miss: !!v.querySelector('[data-winter-miss]'), wid: card ? (card.querySelector('[data-wid]') || card).getAttribute('data-wid') || card.textContent.slice(0, 40) : null}; });
  res[id] = want ? (r.shared && r.focus === want && !r.miss) : (r.miss && !r.shared);
  if (!res[id]) console.log(id, JSON.stringify(r));
  await ctx.close();
}
report('winterlink_check', res, d.errors);
await d.browser.close();
