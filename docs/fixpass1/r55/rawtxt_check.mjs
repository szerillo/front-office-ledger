// Round 55 (Nov 14 audit, item 4): no "traded player, " placeholder and no cut "St. Louis Cardina" on any report card
// or in the player moves data after load. Pass: 0 hits across every rendered card page and PLAYER_MOVES. Exit 1 otherwise.
import { open, report } from './_common.mjs';
const d = await open();
await d.page.waitForFunction(() => window.MOVES_READY === true, null, {timeout: 90000}).catch(() => {});
const r = await d.page.evaluate(async () => {
  if (typeof cardsReady === 'function') { try { await cardsReady(); } catch (e) {} }
  normalizeCurated();
  const pages = [...(typeof REGIMES !== 'undefined' ? REGIMES : []), ...AUTO_REGIMES, ...LB_HIST.filter(x => x.realCard)];
  const seen = new Set(); let hits = 0, cards = 0, cut = 0; const ex = [];
  for (const reg of pages) { if (seen.has(reg.id)) continue; seen.add(reg.id); renderReport(reg.id);
    const t = document.getElementById('view-report').innerHTML; const h = (t.match(/traded player, /g) || []).length, c = (t.match(/St\. Louis Cardina(?!l)/g) || []).length;
    if (h || c) { cards++; hits += h; cut += c; if (ex.length < 5) ex.push(reg.id); } }
  const mv = JSON.stringify(typeof PLAYER_MOVES !== 'undefined' ? PLAYER_MOVES : {});
  return {pages: seen.size, hits, cut, cards, ex, moves: (mv.match(/traded player, /g) || []).length, movesReady: typeof PLAYER_MOVES !== 'undefined'};
});
console.log(JSON.stringify(r));
report('rawtxt_check', {cards_rendered: r.pages >= 150, placeholder_0: r.hits === 0, cut_name_0: r.cut === 0, moves_loaded: r.movesReady, moves_placeholder_0: r.moves === 0}, d.errors);
await d.browser.close();
