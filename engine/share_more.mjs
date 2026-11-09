// Nov 2026: share pages with their own preview images for team pages (t/<ab>), heists (h/<date>-<ab>)
// and the daily game (play/who-won). Rendered from the built page itself. Run after regen.
import { createRequire } from 'module'; import { execSync } from 'child_process'; import fs from 'fs';
const require = createRequire(import.meta.url);
let chromium; try { ({ chromium } = require('playwright')); } catch { ({ chromium } = require(execSync('npm root -g').toString().trim() + '/playwright')); }
const OUT = process.argv[2] || '/work/share';
for(const d of ['t', 'h', 'play', 'og/t', 'og/h']) fs.mkdirSync(`${OUT}/${d}`, {recursive: true});
const b = await chromium.launch();
const p = await b.newPage({viewport: {width: 1200, height: 630}});
await p.route('**/statsapi.mlb.com/**', r => r.abort());
await p.goto('file:///work/front-office-ledger-prototype.html');
await p.waitForFunction(() => window.CARDS_READY === true, null, {timeout: 60000});
await p.evaluate(() => { document.querySelectorAll('.fol-rise, .fol-anim').forEach(e => e.classList.remove('fol-rise', 'fol-anim')); document.documentElement.dataset.theme = 'light'; });
const esc = t => String(t).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/"/g, '&quot;');
// one 1200x630 frame: the brand, the content, the address
const shot = async (inner, file) => {
  await p.evaluate(inner => {
    let f = document.getElementById('og-frame'); if(f) f.remove();
    f = document.createElement('div'); f.id = 'og-frame';
    f.style.cssText = 'position:fixed; left:0; top:0; width:1200px; height:630px; z-index:999999; background:var(--page); color:var(--ink); padding:34px 56px; box-sizing:border-box; overflow:hidden; display:flex; flex-direction:column';
    f.innerHTML = `<div style="display:flex; align-items:center; gap:12px; font:700 22px var(--f-body); letter-spacing:3px">${document.querySelector('.brand .logo').outerHTML.replace('class="logo"', 'width="34" height="34"')}FRONT OFFICE <span style="color:var(--margin)">LEDGER</span></div>
      <div style="flex:1; display:flex; flex-direction:column; justify-content:center; min-height:0">${inner}</div>
      <div style="font:600 20px var(--f-mono); color:var(--muted)">frontofficeledger.com</div>`;
    f.innerHTML = f.innerHTML.replace(/\bfol-rise\b/g, '').replace(/\bfol-anim\b/g, '');
    document.body.appendChild(f);
    f.querySelectorAll('button, .savebtn').forEach(x => x.remove());
  }, inner);
  await p.waitForTimeout(120);
  await (await p.$('#og-frame')).screenshot({path: file});
};
const page = (o) => `<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>${esc(o.title)}</title>
<meta name="description" content="${esc(o.desc)}">
<meta property="og:type" content="website"><meta property="og:site_name" content="Front Office Ledger">
<meta property="og:title" content="${esc(o.title)}"><meta property="og:description" content="${esc(o.desc)}">
<meta property="og:url" content="https://frontofficeledger.com/${o.path}"><meta property="og:image" content="https://frontofficeledger.com/${o.img}">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:site" content="@FrontOfficeLdgr"><meta name="twitter:creator" content="@SeanZerillo">
<meta name="twitter:title" content="${esc(o.title)}"><meta name="twitter:description" content="${esc(o.desc)}"><meta name="twitter:image" content="https://frontofficeledger.com/${o.img}">
<meta http-equiv="refresh" content="0; url=${o.dest}">
<style>body{font-family:Georgia,serif; background:#f2ecdd; color:#1d1a14; padding:40px}</style>
</head><body><p><a href="${o.dest}">${esc(o.link)}</a></p>
<script>location.replace(${JSON.stringify(o.dest)});</script></body></html>
`;
// team pages
const teams = await p.evaluate(() => Object.keys(DESK.teams || {}).sort().map(ab => { const f = folCardFacts(ab); return f ? {ab, club: f.club, exec: f.exec, grade: f.grade, rank: f.rank, n: f.n, net: fmtW(f.net), best: f.best ? String(f.best.h).replace(/<[^>]*>/g, '') : '', bw: f.best ? fmtW(f.best.war) : '', html: folTradingCard(ab)} : null; }).filter(Boolean));
for(const t of teams){
  const slug = t.ab.toLowerCase();
  await shot(`<div style="transform:scale(1.0); transform-origin:left top; margin-top:6px">${t.html.replace('width:1040px', 'width:1088px')}</div>`, `${OUT}/og/t/${slug}.png`);
  const title = `${t.club} front office: ${t.grade} · Front Office Ledger`;
  const desc = `${t.exec}${t.rank ? `, #${t.rank} of ${t.n} front offices` : ''}, ${t.net} wins vs. a typical front office.${t.best ? ` Best move: ${t.best} (${t.bw}).` : ''}`;
  fs.writeFileSync(`${OUT}/t/${slug}.html`, page({title, desc, path: `t/${slug}`, img: `og/t/${slug}.png`, dest: `/#view=team&id=${slug}`, link: `Open the ${t.club} front office on Front Office Ledger`}));
}
// heists: every trade the heist of the day draws from
const heists = await p.evaluate(() => folTrades().filter(t => t.gap >= 8 && t.S.length === 2).sort((a, b) => b.gap - a.gap).slice(0, 150).map(t => ({id: folHeistId(t), d: t.d, html: folHeistCard(t), head: `${folNickAt(t.win.ab, t.d)} got ${(t.win.got[0] || {}).nm || 'the better end'} from the ${folNickAt(t.lose.ab, t.d)}`, gap: fmtW(t.gap), stamp: folStamp(t.gap), mon: folMon(t.d)})));
for(const h of heists){
  await shot(`<div style="font:600 20px var(--f-mono); color:var(--margin); letter-spacing:2px; margin-bottom:8px">HEISTS AND DISASTERS</div><div style="font-size:21px; zoom:1.45">${h.html}</div>`, `${OUT}/og/h/${h.id}.png`);
  const title = `${h.head} (${h.stamp}, ${h.gap} wins) · Front Office Ledger`;
  const desc = `${h.mon}: what every player produced for the club that got him, over his control window. Every trade since 1998, ranked.`;
  fs.writeFileSync(`${OUT}/h/${h.id}.html`, page({title, desc, path: `h/${h.id}`, img: `og/h/${h.id}.png`, dest: `/#view=heists&id=${h.id}`, link: `See this trade on Front Office Ledger`}));
}
// the daily game: Trade Grade (play/who-won kept for links already shared)
await shot(`<div style="font:600 20px var(--f-mono); color:var(--margin); letter-spacing:2px">DAILY GAME</div>
  <div style="font:900 104px/1.02 var(--f-display); margin-top:10px">Trade Grade</div>
  <div style="font-size:30px; color:var(--ink-2); margin-top:14px; max-width:960px">Five real calls a day: three trades and two free-agent contracts. Pick the winner, then see what every player produced.</div>
  <div style="font-size:44px; letter-spacing:8px; margin-top:22px">🟩🟥🟩🟩🟩</div>`, `${OUT}/og/trade-grade.png`);
for(const slug of ['trade-grade', 'who-won'])
  fs.writeFileSync(`${OUT}/play/${slug}.html`, page({title: 'Trade Grade · Front Office Ledger', desc: 'Five real calls a day: three trades and two free-agent contracts. Pick the winner; the Ledger shows the receipts.', path: `play/${slug}`, img: 'og/trade-grade.png', dest: '/#view=quiz', link: "Play today's Trade Grade on Front Office Ledger"}));
console.log('team pages', teams.length, '| heist pages', heists.length);
await b.close();
