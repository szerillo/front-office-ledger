// Round 55 (Nov 14 audit, blocker 2 and item 10): the corrections log is reachable and indexed.
// Pass: the footer's "Corrections" link goes to /corrections/ (not the feedback email); every under-review label on a
// report card links to /corrections/; /corrections/ loads and links both dated pages; each dated page links back;
// sitemap.xml lists /corrections/, at least 150 c/, 30 t/, 30 s/, 40 o/ and 100 h/ pages, and no page marked noindex
// (checked by fetching every listed share page). Exit 1 otherwise.
import { open, report } from './_common.mjs';
const BASE = process.env.TARGET === 'live' ? (process.env.LIVE_URL || 'https://frontofficeledger.com/') : 'http://127.0.0.1:8767/r55/tree/';
const d = await open();
const r = await d.page.evaluate(async (BASE) => {
  const get = async u => { const x = await fetch(BASE + u, {cache: 'no-store'}); return x.ok ? x.text() : null; };
  if (typeof cardsReady === 'function') { try { await cardsReady(); } catch (e) {} }
  normalizeCurated();
  const foot = [...document.querySelectorAll('footer a')].find(a => a.textContent.trim() === 'Corrections');
  const ids = Object.keys(CTRL_REVIEW).slice(0, 12); let chips = 0, chipsOk = 0;
  for (const id of ids) { renderReport(id); document.querySelectorAll('#view-report [data-review]').forEach(e => { chips++; const a = e.matches('a') ? e : e.querySelector('a'); if (a && a.getAttribute('href') === '/corrections/') chipsOk++; }); }
  const idx = await get('corrections/'), d12 = await get('corrections/2026-11-12.html'), d14 = await get('corrections/2026-11-14.html');
  const sm = await get('sitemap.xml') || ''; const locs = [...sm.matchAll(/<loc>([^<]+)<\/loc>/g)].map(m => m[1]);
  const cnt = k => locs.filter(u => u.includes('.com/' + k + '/')).length;
  let noidx = 0, missing = 0;
  for (const u of locs) { const path = u.replace('https://frontofficeledger.com/', ''); if (!path || path.startsWith('corrections')) continue; const t = await get(path + '.html'); if (!t) missing++; else if (/noindex/.test(t)) noidx++; }
  return {foot: foot ? foot.getAttribute('href') : null, chips, chipsOk, idx: !!idx, idxLinks: !!idx && /2026-11-12\.html/.test(idx) && /2026-11-14\.html/.test(idx), back: !!d12 && !!d14 && d12.includes('href="/corrections/"') && d14.includes('href="/corrections/"'),
    smCorr: locs.some(u => /\/corrections\/$/.test(u)), c: cnt('c'), t: cnt('t'), s: cnt('s'), o: cnt('o'), h: cnt('h'), noidx, missing};
}, BASE);
console.log(JSON.stringify(r));
report('corrlinks_check', {footer_to_log: r.foot === '/corrections/', labels_link_log: r.chips > 0 && r.chips === r.chipsOk, log_loads: r.idx, log_links_dated: r.idxLinks, dated_link_back: r.back,
  sitemap_log: r.smCorr, sitemap_counts: r.c >= 150 && r.t >= 30 && r.s >= 30 && r.o >= 40 && r.h >= 100, sitemap_noindex_0: r.noidx === 0, sitemap_missing_0: r.missing === 0}, d.errors);
await d.browser.close();
