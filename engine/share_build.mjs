// Builds the share pages (c/<id>.html) and their preview images (og/<id>.png),
// plus the site-wide og.png, from the built page itself. Run after regen.
import { chromium } from 'playwright';
import fs from 'fs';
const OUT = process.argv[2] || '/home/claude/share';
fs.mkdirSync(OUT + '/c', {recursive: true}); fs.mkdirSync(OUT + '/og', {recursive: true});
const b = await chromium.launch({executablePath: '/opt/pw-browsers/chromium', proxy: process.env.HTTPS_PROXY ? {server: process.env.HTTPS_PROXY} : undefined});
const p = await b.newPage();
await p.route('**/statsapi.mlb.com/**', r => r.abort());
await p.goto('file:///home/claude/front-office-ledger-prototype.html');
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
      titles: r.titles || 0};
  });
  return {rows, n: AUTO_REGIMES.length + LB_HIST.length};
});
const col = g => g == null ? ['#f4efe2', '#6b6457', '#bdb4a2'] : g >= 65 ? ['#e3ecdf', '#1e6b47', '#1e6b47'] : g >= 55 ? ['#eef0dc', '#55621d', '#55621d'] : g >= 45 ? ['#f7f3e8', '#1d1a14', '#3a352b'] : g >= 38 ? ['#f6e5d3', '#8a5d00', '#8a5d00'] : ['#f5dcd8', '#a32c20', '#a32c20'];
const chip = (txt, g, big) => { const [bg, fg, bd] = col(g); return `<span style="display:inline-block; background:${bg}; color:${fg}; border:${big ? 3 : 2}px solid ${bd}; border-radius:6px; font:600 ${big ? 92 : 26}px/1 'IBM Plex Mono', monospace; padding:${big ? '14px 26px' : '9px 14px'}">${txt}</span>`; };
const fonts = `<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Source+Serif+4:ital,wght@0,400;0,600;1,400&family=IBM+Plex+Mono:wght@500;600&display=swap" rel="stylesheet">`;
const ball = `<svg width="118" height="118" viewBox="0 0 64 64"><defs><clipPath id="b"><circle cx="32" cy="32" r="26"/></clipPath></defs><circle cx="32" cy="32" r="26" fill="#faf6ec"/><g clip-path="url(#b)" stroke="#9db6cc" stroke-width="1.4"><line x1="4" y1="18" x2="60" y2="18"/><line x1="4" y1="25" x2="60" y2="25"/><line x1="4" y1="32" x2="60" y2="32"/><line x1="4" y1="39" x2="60" y2="39"/><line x1="4" y1="46" x2="60" y2="46"/></g><g clip-path="url(#b)" fill="none" stroke="#9d3025" stroke-width="2.6" stroke-linecap="round"><path d="M 13 7 C 24 20, 24 44, 13 57"/><path d="M 51 7 C 40 20, 40 44, 51 57"/></g><circle cx="32" cy="32" r="26" fill="none" stroke="#1d1a14" stroke-width="2.6"/></svg>`;
const frame = inner => `<!doctype html><html><head><meta charset="utf-8">${fonts}<style>
  body{margin:0; width:1200px; height:630px; background:#f2ecdd; position:relative; overflow:hidden; font-family:'Source Serif 4', Georgia, serif; color:#1d1a14}
  .feint{position:absolute; left:0; right:0; height:1px; background:#c9d6e2}
  .margin{position:absolute; top:0; bottom:0; left:92px; width:2px; background:#c98a80}
  .in{position:absolute; left:130px; right:80px; top:58px}
  .rule{border-top:3px double #1d1a14; margin-bottom:26px}
  .foot{position:absolute; left:130px; bottom:40px; font:500 22px 'IBM Plex Mono', monospace; color:#6b6457}
</style></head><body>${[180, 260, 340, 420, 500].map(y => `<div class="feint" style="top:${y}px"></div>`).join('')}<div class="margin"></div><div class="in"><div class="rule"></div>${inner}</div>
<div class="foot">frontofficeledger.com</div><div style="position:absolute; right:84px; bottom:28px">${ball.replace('width="118" height="118"', 'width="76" height="76"')}</div></body></html>`;
const q = await b.newPage({viewport: {width: 1200, height: 630}});
const slug = id => String(id).toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
const esc = t => String(t).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/"/g, '&quot;');
// site-wide image
await q.setContent(frame(`<div style="display:flex; justify-content:space-between; align-items:flex-start"><div>
  <div style="font:900 104px/1.02 'Playfair Display', serif; letter-spacing:1px">FRONT OFFICE</div>
  <div style="font:900 104px/1.02 'Playfair Display', serif; color:#9d3025; letter-spacing:1px">LEDGER</div></div><div style="margin-top:6px">${ball}</div></div>
  <div style="font:italic 400 31px/1.35 'Source Serif 4', serif; color:#3a352b; margin-top:22px; max-width:900px">Every MLB front office since 1998, graded on every trade, draft pick, signing and extension, against what a typical club got from the same move.</div>
  <div style="font:500 24px 'IBM Plex Mono', monospace; color:#6b6457; margin-top:22px">${data.n} front offices graded</div>`), {waitUntil: 'networkidle'});
await q.screenshot({path: OUT + '/og.png'});
for(const r of data.rows){
  const sub = `${r.team} · ${r.span}${r.titles ? ` · ${r.titles} World Series title${r.titles > 1 ? 's' : ''}` : ''}`;
  const rk = r.rank ? `#${r.rank} of 30 active front offices` : r.hist ? 'archive regime' : '';
  const html = frame(`<div style="display:flex; justify-content:space-between; align-items:flex-start; gap:30px">
    <div style="min-width:0"><div style="font:600 22px 'IBM Plex Mono', monospace; color:#9d3025; letter-spacing:2px">FRONT OFFICE LEDGER · REPORT CARD</div>
      <div style="font:900 ${r.exec.length > 18 ? 70 : 84}px/1.05 'Playfair Display', serif; margin-top:14px">${esc(r.exec)}</div>
      <div style="font:400 30px/1.3 'Source Serif 4', serif; color:#3a352b; margin-top:8px">${esc(sub)}</div></div>
    <div style="text-align:center; flex:none">${chip(r.overall, r.og, true)}<div style="font:600 20px 'IBM Plex Mono', monospace; color:#6b6457; margin-top:10px">OVERALL</div></div></div>
    <div style="margin-top:34px; display:flex; flex-wrap:wrap; gap:14px; align-items:center; font:500 24px 'IBM Plex Mono', monospace; color:#3a352b">
      ${r.best.map(([n, l, g]) => `<span>${esc(n)} ${chip(l, g)}</span>`).join('')}<span>Success ${chip(r.success, r.sg)}</span></div>
    <div style="margin-top:26px; font:500 25px 'IBM Plex Mono', monospace; color:#3a352b">${r.isNew ? 'too new to grade' : `${r.net} wins vs expectation`}${rk ? ` · ${rk}` : ''}</div>`);
  await q.setContent(html, {waitUntil: 'networkidle'});
  await q.screenshot({path: `${OUT}/og/${slug(r.id)}.png`});
  const title = `${r.exec}, ${r.team}: ${r.overall} · Front Office Ledger`;
  const desc = r.isNew ? `${r.exec} (${r.team}) is too new to grade.` : `Overall ${r.overall}, ${r.net} wins vs expectation${rk ? ', ' + rk : ''}. Best: ${r.best.map(([n, l]) => `${n} ${l}`).join(', ')}. Every decision graded against what a typical club got from the same move.`;
  const url = `https://frontofficeledger.com/c/${slug(r.id)}`, dest = `/#view=cards&id=${encodeURIComponent(r.id)}`;
  fs.writeFileSync(`${OUT}/c/${slug(r.id)}.html`, `<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>${esc(title)}</title>
<meta name="description" content="${esc(desc)}">
<meta property="og:type" content="website"><meta property="og:site_name" content="Front Office Ledger">
<meta property="og:title" content="${esc(title)}"><meta property="og:description" content="${esc(desc)}">
<meta property="og:url" content="${url}"><meta property="og:image" content="https://frontofficeledger.com/og/${slug(r.id)}.png">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="${esc(title)}">
<meta name="twitter:description" content="${esc(desc)}"><meta name="twitter:image" content="https://frontofficeledger.com/og/${slug(r.id)}.png">
<meta http-equiv="refresh" content="0; url=${dest}">
<style>body{font-family:Georgia,serif; background:#f2ecdd; color:#1d1a14; padding:40px}</style>
</head><body><p><a href="${dest}">Open ${esc(r.exec)}'s report card on Front Office Ledger</a></p>
<script>location.replace(${JSON.stringify(dest)});</script></body></html>
`);
}
console.log('share pages:', data.rows.length);
await b.close();
