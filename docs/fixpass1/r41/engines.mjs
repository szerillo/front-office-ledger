// Round 41 C: every suite runs Chromium; iPhone visitors get WebKit. Same live page, both engines, same probes.
import { createRequire } from 'module'; import { execSync } from 'child_process';
const require = createRequire(import.meta.url); const pw = require(execSync('npm root -g').toString().trim() + '/playwright');
const URL = process.argv[2] || 'https://frontofficeledger.com/';
for (const name of ['chromium', 'webkit']) {
  let b; try { b = await pw[name].launch(); } catch (e) { console.log(name, 'LAUNCH FAILED', e.message.split('\n')[0]); continue; }
  const dev = { ...pw.devices['iPhone 13'] }; if(name !== 'webkit') delete dev.defaultBrowserType; const ctx = await b.newContext(dev);
  const p = await ctx.newPage(); const errs = []; p.on('pageerror', e => errs.push(e.message.slice(0, 120)));
  await p.route(/statsapi|goatcounter|abacus|gc\.zgo/, r => r.abort());
  const t0 = Date.now();
  await p.goto(URL + '?v=' + Date.now(), { waitUntil: 'load', timeout: 120000 });
  await p.waitForFunction(() => window.CARDS_READY === true && window.MOVES_READY === true, null, { timeout: 90000 }).catch(() => {});
  const r = await p.evaluate(async () => {
    const out = {};
    out.ready = window.CARDS_READY === true; out.moves = window.MOVES_READY === true; out.banner = !!document.getElementById('cards-fail');
    const g = {}; [...AUTO_REGIMES, ...LB_HIST].forEach(x => { g[x.id] = [x.forGrade, ...['draft','trade','fa','waiver','intl','ext'].map(k => x.chan[k] && x.chan[k].g)]; });
    out.gradeSig = JSON.stringify(g).length + ':' + [...JSON.stringify(g)].reduce((a, c) => (a * 31 + c.charCodeAt(0)) >>> 0, 7);
    out.chc = AUTO_REGIMES.find(x => x.id === 'chc').forGrade; out.minaya = LB_HIST.find(x => x.id === 'nym-omar-minaya').chan.trade.g;
    try { await offsLoad(); out.offsRows = (OFFS.rows || (OFFS.data && OFFS.data.rows) || []).length; } catch (e) { out.offs = 'ERR ' + e.message; }
    out.trades = TRADE_BOOK.trades.length; out.clubs = Object.keys(window.CARD_DETAIL || {}).length;
    // a few views the visitor reaches by tapping
    const views = {}; for (const v of ['wire', 'leaderboard', 'winters', 'method', 'trees']) { try { location.hash = '#view=' + v; await new Promise(r => setTimeout(r, 3000)); const el = document.getElementById('view-' + v); views[v] = el ? (!el.hidden && el.innerText.length) : 'no section'; } catch (e) { views[v] = 'ERR ' + e.message; } }
    out.views = views; return out;
  });
  console.log(name, JSON.stringify(r), '| page errors', errs.length, errs.slice(0, 3), '| secs', ((Date.now() - t0) / 1000).toFixed(1));
  await b.close();
}
