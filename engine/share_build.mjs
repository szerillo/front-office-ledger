// Builds the share pages (c/<id>.html) and their preview images (og/<id>.png),
// plus the site-wide og.png, from the built page itself. Run after regen.
import { createRequire } from 'module'; import { execSync } from 'child_process';
const require = createRequire(import.meta.url);
let chromium; try { ({ chromium } = require('playwright')); } catch { ({ chromium } = require(execSync('npm root -g').toString().trim() + '/playwright')); }
import fs from 'fs';
const OUT = process.argv[2] || '/work/share';
fs.mkdirSync(OUT + '/c', {recursive: true}); fs.mkdirSync(OUT + '/og', {recursive: true});
const b = await chromium.launch({proxy: process.env.HTTPS_PROXY ? {server: process.env.HTTPS_PROXY, bypass: '127.0.0.1,localhost'} : undefined});
const p = await b.newPage();
await p.route('**/statsapi.mlb.com/**', r => r.abort());
// Nov 14: build from any copy of the page (a staged tree served locally, or the live site): node engine/share_build.mjs <out> [page url] [version tag]
const SRC = process.argv[3] || 'file:///work/front-office-ledger-prototype.html', VER = process.argv[4] || '';
await p.goto(SRC);
await p.waitForFunction(() => window.CARDS_READY === true, null, {timeout: 60000});
const data = await p.evaluate(() => {
  normalizeCurated();
  const act = lbRows().filter(r => !r._hist && !r.isNew).sort((a, b) => (b.forGrade||0) - (a.forGrade||0) || b.net - a.net);
  const rank = Object.fromEntries(act.map((r, i) => [r.id, i + 1]));
  const L = g => g == null ? '·' : g2letter(g);
  const chanName = {draft: 'Draft', trade: 'Trades', fa: 'Free agency', waiver: 'Waivers', intl: "Int'l", ext: 'Extensions'};
  const rows = [...AUTO_REGIMES, ...LB_HIST.filter(r => r.realCard)].map(r => {
    const ch = Object.entries(chanName).map(([k, n]) => [n, (r.chan[k]||{}).g]).filter(([, g]) => g != null).sort((a, b) => b[1] - a[1]);
    const net = CHANNELS.reduce((s, c) => s + ((r.chan[c.key]||{}).net||0), 0) + ((r.chan.ret && r.chan.ret.net2)||0);
    return {id: r.id, exec: regName(r), team: r.teamEra || r.team, span: yrSpan(r.start, r.end), hist: !!LB_HIST.includes(r), isNew: !!r.isNew,
      overall: L(r.forGrade), og: r.forGrade, net: fmtW(net), success: L((r.success||{}).g), sg: (r.success||{}).g, best: ch.slice(0, 3).map(([n, g]) => [n, L(g), g]), rank: rank[r.id] || null,
      titles: r.titles || 0, review: typeof CTRL_REVIEW !== 'undefined' && !!CTRL_REVIEW[r.id]};
  });
  return {rows, n: AUTO_REGIMES.length + LB_HIST.length, nAct: act.length};
});
const col = g => g == null ? ['#f4efe2', '#78705f', '#bdb4a2'] : g >= 65 ? ['#e3ecdf', '#1e6b47', '#1e6b47'] : g >= 55 ? ['#eef0dc', '#55621d', '#55621d'] : g >= 45 ? ['#f7f3e8', '#1d1d1b', '#45423b'] : g >= 38 ? ['#f6e5d3', '#8a5d00', '#8a5d00'] : ['#f5dcd8', '#a32c20', '#a32c20'];
const chip = (txt, g, big) => { const [bg, fg, bd] = col(g); return `<span style="display:inline-block; background:${bg}; color:${fg}; border:${big ? 3 : 2}px solid ${bd}; border-radius:6px; font:600 ${big ? 92 : 26}px/1 'IBM Plex Mono', monospace; padding:${big ? '14px 26px' : '9px 14px'}">${txt}</span>`; };
const fonts = `<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+Display:wdth,wght@62.5..100,400..900&family=Source+Serif+4:ital,wght@0,400;0,600;1,400;1,600&family=IBM+Plex+Mono:wght@500;600&display=swap" rel="stylesheet">`;
const ball = `<svg width="118" height="118" viewBox="0 0 64 64"><defs><clipPath id="b"><circle cx="32" cy="32" r="26"/></clipPath></defs><circle cx="32" cy="32" r="26" fill="#efe0bd"/><g clip-path="url(#b)" stroke="#a88a5c" stroke-width="1.5"><line x1="4" y1="18" x2="60" y2="18"/><line x1="4" y1="25" x2="60" y2="25"/><line x1="4" y1="32" x2="60" y2="32"/><line x1="4" y1="39" x2="60" y2="39"/><line x1="4" y1="46" x2="60" y2="46"/></g><g clip-path="url(#b)" fill="none" stroke="#b23a1e" stroke-width="2.6" stroke-linecap="round"><path d="M 13 7 C 24 20, 24 44, 13 57"/><path d="M 51 7 C 40 20, 40 44, 51 57"/></g><g clip-path="url(#b)" stroke="#b23a1e" stroke-width="1.6" stroke-linecap="round"><line x1="17.1" y1="15.5" x2="22.1" y2="13.1"/><line x1="19.6" y1="23.5" x2="25.0" y2="22.1"/><line x1="20.4" y1="32.0" x2="25.9" y2="32.0"/><line x1="19.6" y1="40.5" x2="25.0" y2="41.9"/><line x1="17.1" y1="48.5" x2="22.1" y2="50.9"/><line x1="46.9" y1="15.5" x2="41.9" y2="13.1"/><line x1="44.4" y1="23.5" x2="39.0" y2="22.1"/><line x1="43.6" y1="32.0" x2="38.1" y2="32.0"/><line x1="44.4" y1="40.5" x2="39.0" y2="41.9"/><line x1="46.9" y1="48.5" x2="41.9" y2="50.9"/></g><circle cx="32" cy="32" r="26" fill="none" stroke="#1d1d1b" stroke-width="2.6"/></svg>`;
const frame = inner => `<!doctype html><html><head><meta charset="utf-8">${fonts}<style>
  body{margin:0; width:1200px; height:630px; background:#f4efe2; position:relative; overflow:hidden; font-family:'Source Serif 4', Georgia, serif; color:#1d1d1b}
  .feint{position:absolute; left:0; right:0; height:1px; background:#c9d6e2}
  .margin{position:absolute; top:0; bottom:0; left:92px; width:2px; background:#d9a093}
  .in{position:absolute; left:130px; right:80px; top:34px}
  .rule{border-top:3px double #1d1d1b; margin-bottom:26px}
  .foot{position:absolute; left:130px; bottom:40px; font:500 22px 'IBM Plex Mono', monospace; color:#78705f}
</style></head><body>${[180, 260, 340, 420, 500].map(y => `<div class="feint" style="top:${y}px"></div>`).join('')}<div class="margin"></div><div class="in"><div style="display:flex; align-items:center; gap:12px; margin-bottom:12px">${ball.replace('width="118" height="118"', 'width="40" height="40"')}<span style="font:700 38px/1 'Noto Serif Display', serif; font-stretch:75%; color:#1d1d1b">Front Office Ledger</span></div><div class="rule"></div>${inner}</div>
<div class="foot">frontofficeledger.com · Every move, graded.</div></body></html>`;
const q = await b.newPage({viewport: {width: 1200, height: 630}});
const slug = id => String(id).toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
const esc = t => String(t).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/"/g, '&quot;');
// site-wide image
await q.setContent(frame(`<div style="display:flex; justify-content:space-between; align-items:flex-start"><div>
  <div style="font:700 96px/1.02 'Noto Serif Display', serif; font-stretch:75%">Every move, graded.</div></div></div>
  <div style="font:italic 400 31px/1.35 'Source Serif 4', serif; color:#45423b; margin-top:22px; max-width:900px">Every MLB front office since 1998, graded on every trade, draft pick, signing and extension, against what a typical club got from the same move.</div>
  <div style="font:500 24px 'IBM Plex Mono', monospace; color:#78705f; margin-top:22px">${data.n} front offices graded</div>`), {waitUntil: 'networkidle'});
await q.screenshot({path: OUT + '/og.png'});
for(const r of data.rows){
  const sub = `${r.team} · ${r.span}${r.titles ? ` · ${r.titles} World Series title${r.titles > 1 ? 's' : ''}` : ''}`;
  // Nov 14 (round 56): no rank numbers in share text or previews: the site publishes none (exact ranks do not hold)
  const html = frame(`<div style="display:flex; justify-content:space-between; align-items:flex-start; gap:30px">
    <div style="min-width:0"><div style="font:600 22px 'IBM Plex Mono', monospace; color:#b23a1e; letter-spacing:2px">REPORT CARD</div>
      <div style="font:700 ${r.exec.length > 18 ? 76 : 92}px/1.02 'Noto Serif Display', serif; font-stretch:75%; margin-top:8px">${esc(r.exec)}</div>
      <div style="font:400 30px/1.3 'Source Serif 4', serif; color:#45423b; margin-top:8px">${esc(sub)}</div></div>
    <div style="text-align:center; flex:none">${chip(r.overall, r.og, true)}<div style="font:600 20px 'IBM Plex Mono', monospace; color:#78705f; margin-top:10px">OVERALL</div></div></div>
    <div style="margin-top:34px; display:flex; flex-wrap:wrap; gap:14px; align-items:center; font:500 24px 'IBM Plex Mono', monospace; color:#45423b">
      ${r.best.map(([n, l, g]) => `<span>${esc(n)} ${chip(l, g)}</span>`).join('')}<span>Success ${chip(r.success, r.sg)}</span></div>
    <div style="margin-top:26px; font:500 25px 'IBM Plex Mono', monospace; color:#45423b">${r.isNew ? 'too new to grade' : `${r.net} wins vs expectation`}</div>${r.review ? `<div style="display:inline-block; margin-top:16px; background:#f3e3b5; color:#5a4410; border:2px solid #c9a64a; border-radius:6px; font:600 22px 'IBM Plex Mono', monospace; padding:6px 12px">UNDER REVIEW: control-end data being corrected</div>` : ''}`);
  await q.setContent(html, {waitUntil: 'networkidle'});
  await q.screenshot({path: `${OUT}/og/${slug(r.id)}.png`});
  const title = `${r.exec}, ${r.team}: ${r.isNew ? 'new, not yet graded' : r.overall}${r.review ? ' (under review)' : ''} · Front Office Ledger`;
  const desc = r.isNew ? `${r.exec} (${r.team}) is too new to grade.` : `Overall ${r.overall}, ${r.net} wins vs expectation. Best: ${r.best.map(([n, l]) => `${n} ${l}`).join(', ')}. Every decision graded against what a typical club got from the same move.${r.review ? ' Under review: control-end data being corrected.' : ''}`;
  const url = `https://frontofficeledger.com/c/${slug(r.id)}`, dest = `/#view=cards&id=${encodeURIComponent(r.id)}`;
  fs.writeFileSync(`${OUT}/c/${slug(r.id)}.html`, `<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>${esc(title)}</title>
<meta name="description" content="${esc(desc)}">
<meta property="og:type" content="website"><meta property="og:site_name" content="Front Office Ledger">
<meta property="og:title" content="${esc(title)}"><meta property="og:description" content="${esc(desc)}">
<meta property="og:url" content="${url}"><meta property="og:image" content="https://frontofficeledger.com/og/${slug(r.id)}.png${VER ? `?v=${VER}` : ''}">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:site" content="@FrontOfficeLdgr"><meta name="twitter:creator" content="@SeanZerillo"><meta name="twitter:title" content="${esc(title)}">
<meta name="twitter:description" content="${esc(desc)}"><meta name="twitter:image" content="https://frontofficeledger.com/og/${slug(r.id)}.png${VER ? `?v=${VER}` : ''}">
<meta http-equiv="refresh" content="0; url=${dest}">
<style>body{font-family:Georgia,serif; background:#f4efe2; color:#1d1d1b; padding:40px}</style>
</head><body><p><a href="${dest}">Open ${esc(r.exec)}'s report card on Front Office Ledger</a></p>
<script>location.replace(${JSON.stringify(dest)});</script></body></html>
`);
}
// Nov 14: what each preview was rendered with, and the image's md5, so a check can hold previews to the live cards
const crypto = await import('crypto');
fs.writeFileSync(`${OUT}/og/cards-manifest.json`, JSON.stringify({built: new Date().toISOString(), src: SRC, ver: VER, cards: Object.fromEntries(data.rows.map(r => [slug(r.id), {id: r.id, overall: r.isNew ? null : r.overall, net: r.isNew ? null : r.net, review: r.review, png: crypto.createHash('md5').update(fs.readFileSync(`${OUT}/og/${slug(r.id)}.png`)).digest('hex')}]))}, null, 0));
console.log('share pages:', data.rows.length);
await b.close();
