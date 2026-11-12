// Nov 10 2026: share pages for the live parts of the site, each with its own preview image, so a link
// posted on X shows the deal, the club's winter or the offseason instead of the generic card.
//   w/<id>.html + og/w/<id>.png   every graded move on the Wire
//   s/<ab>.html + og/s/<ab>.png   every club's winter page (30)
//   o/<id>.html + og/o/<id>.png   the 20 best and 20 worst winters
//   share.json                    what exists, read by the page to pick the share link
//   feed.xml                      an RSS feed of the 40 latest graded moves (each item links to its w/ page)
// Rendered from the site itself. Usage: node engine/share_live.mjs <out dir> [site url] [--only-new <repo dir>]
// With --only-new, a move or winter that already has a page in <repo dir> is skipped; club pages are rebuilt
// only when that club's winter changed (the page's description is the fingerprint).
import { createRequire } from 'module'; import { execSync } from 'child_process'; import fs from 'fs';
const require = createRequire(import.meta.url);
let chromium; try { ({ chromium } = require('playwright')); } catch { ({ chromium } = require(execSync('npm root -g').toString().trim() + '/playwright')); }
const OUT = process.argv[2] || './share_out', BASE = (process.argv[3] && !process.argv[3].startsWith('--') ? process.argv[3] : 'https://frontofficeledger.com/');
const oi = process.argv.indexOf('--only-new'), REPO = oi > 0 ? process.argv[oi + 1] : '';
for(const d of ['w', 's', 'o', 'og/w', 'og/s', 'og/o']) fs.mkdirSync(`${OUT}/${d}`, {recursive: true});
const b = await chromium.launch();
const p = await b.newPage({viewport: {width: 1200, height: 630}});
await p.route(/gc\.zgo\.at|goatcounter\.com|abacus\.jasoncameron\.dev/, r => r.abort());
await p.goto(BASE, {waitUntil: 'load', timeout: 120000});
await p.waitForFunction(() => window.CARDS_READY === true, null, {timeout: 90000});
await p.evaluate(async () => { await wireLoad(true); await offsLoad(); document.documentElement.dataset.theme = 'light'; });
const esc = t => String(t).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/"/g, '&quot;');
const shot = async (inner, file) => {
  await p.evaluate(inner => {
    let f = document.getElementById('og-frame'); if(f) f.remove();
    f = document.createElement('div'); f.id = 'og-frame';
    f.style.cssText = 'position:fixed; left:0; top:0; width:1200px; height:630px; z-index:999999; background:var(--page); color:var(--ink); padding:34px 56px; box-sizing:border-box; overflow:hidden; display:flex; flex-direction:column';
    f.innerHTML = `<div style="display:flex; align-items:center; gap:12px; font:700 22px var(--f-body); letter-spacing:3px">${document.querySelector('.brand .logo').outerHTML.replace('class="logo"', 'width="34" height="34"')}FRONT OFFICE <span style="color:var(--margin)">LEDGER</span></div>
      <div style="flex:1; display:flex; flex-direction:column; justify-content:center; min-height:0">${inner}</div>
      <div style="font:600 20px var(--f-mono); color:var(--muted)">frontofficeledger.com</div>`;
    document.body.appendChild(f);
  }, inner);
  await p.waitForTimeout(100);
  await (await p.$('#og-frame')).screenshot({path: file});
};
const page = o => `<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>${esc(o.title)}</title>
<meta name="description" content="${esc(o.desc)}">
<meta property="og:type" content="website"><meta property="og:site_name" content="Front Office Ledger">
<meta property="og:title" content="${esc(o.title)}"><meta property="og:description" content="${esc(o.desc)}">
<meta property="og:url" content="https://frontofficeledger.com/${o.path}"><meta property="og:image" content="https://frontofficeledger.com/${o.img}?v=${o.ver}">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:site" content="@FrontOfficeLdgr"><meta name="twitter:creator" content="@SeanZerillo">
<meta name="twitter:title" content="${esc(o.title)}"><meta name="twitter:description" content="${esc(o.desc)}"><meta name="twitter:image" content="https://frontofficeledger.com/${o.img}?v=${o.ver}">
<meta http-equiv="refresh" content="0; url=/${o.to}">
<style>body{font-family:Georgia,serif; background:#f2ecdd; color:#1d1a14; padding:40px}</style>
</head><body><p><a href="/${o.to}">${esc(o.link)}</a></p>
<script>location.replace(${JSON.stringify('/' + o.to)});</script></body></html>
`;
// Nov 12 (round 36): winter pages already in the repo that are no longer in the top/bottom 20 are rebuilt too, so no
// winter page keeps an old number after a regrade
const KEEP_O = REPO && fs.existsSync(`${REPO}/o`) ? fs.readdirSync(`${REPO}/o`).filter(f => f.endsWith('.html')).map(f => f.slice(0, -5)) : [];
// Nov 12 (round 40): winters whose rank is too close to call (gap under 0.5 wins, model-sensitive) say so instead of a
// rank number. Only the pairs listed here; each entry names the winter it cannot be separated from.
const TOO_CLOSE = {'2014-wsh': "2011 A's", '2011-ath': '2014 Nationals'};
const data = await p.evaluate(([KEEP_O, TOO_CLOSE]) => {
  const nick = ab => teamNick(CLUB_NAME[ab] || ab), slug = id => String(id).replace(/[^A-Za-z0-9_-]/g, '-');
  const chip = (ab, px) => `<span class="wi-tc" style="${folTC(ab)}; font-size:${px}px; padding:${Math.round(px / 5)}px ${Math.round(px / 2.4)}px; border-radius:6px">${ab}</span>`;
  const grade = (g, px) => g ? `<span class="grade ${letterClass(g)}" style="font-size:${px}px; padding:${Math.round(px / 6)}px ${Math.round(px / 2.2)}px">${g}</span>` : '';
  const kick = t => `<div style="font:700 20px var(--f-mono); letter-spacing:3px; text-transform:uppercase; color:var(--margin)">${t}</div>`;
  const head = (t, px) => `<div style="font:700 ${px}px/1.12 var(--f-head, 'Playfair Display', Georgia, serif); margin-top:10px">${t}</div>`;
  // the Wire: every graded move
  const W = (WIRE.items || []).filter(it => it.notable && (it.kind === 'trade' ? (it.sides || []).length : it.g)).map(it => {
    const h = wireHeadline(it), when = folMD(it.d) + ', ' + String(it.d).slice(0, 4);
    const body = it.kind === 'trade'
      ? it.sides.slice(0, 3).map(s => `<div style="display:flex; align-items:center; gap:16px; margin-top:16px; font-size:27px">${chip(s.ab, 26)}${grade(s.g, 30)}<span style="min-width:0; white-space:nowrap; overflow:hidden; text-overflow:ellipsis">gets ${(s.gets || []).map(w => w.nm).slice(0, 3).join(', ') || 'cash'}</span>${s.net != null ? `<strong class="${s.net >= 0 ? 'pos' : 'neg'}" style="margin-left:auto; font:700 28px var(--f-mono); white-space:nowrap">${fmtW(s.net)} wins</strong>` : ''}</div>`).join('')
      : `<div style="display:flex; align-items:center; gap:18px; margin-top:22px; font-size:28px">${chip(it.club, 30)}${grade(it.g, 40)}<span>${it.terms ? `${it.terms.yrs} yr / $${it.terms.tot}M` : it.kind === 'claim' ? 'waiver claim' : ''}${it.fa && it.fa.rel != null ? ` · <strong class="${it.fa.rel >= 0 ? 'pos' : 'neg'}">${fmtW(it.fa.rel)} wins</strong> against a typical signing` : it.val != null ? ` · <strong class="${it.val >= 0 ? 'pos' : 'neg'}">${fmtW(it.val)} wins</strong> of surplus` : ''}</span></div>`;
    return {id: slug(it.id), raw: String(it.id), d: it.d, h, title: `${h} · Front Office Ledger`, desc: wireShareText(it), to: `#view=wire&id=${encodeURIComponent(it.id)}`, link: `${h}: the grade on Front Office Ledger`,
      inner: kick(`The Wire · ${when} · graded the day it happened`) + head(h, h.length > 60 ? 44 : 54) + body};
  });
  // club by club
  const S = Object.keys(DESK.teams || {}).sort().map(ab => {
    const c = wireClubWinter(ab), L = wireWinterLetter(c.net, c.n), nm = x => x.w ? x.w.nm : '';
    const own = (DESK.players || []).filter(q => q[2] === ab && gmIsFA(q) && !gmIsProsRow(q) && gmProj27(q) >= 0.3 && !wireActual(q[1])).sort((a, b) => gmProj27(b) - gmProj27(a));
    const line = (lbl, xs, none) => `<div style="display:flex; gap:14px; margin-top:12px; font-size:26px"><strong style="flex:none; width:210px; font:700 20px var(--f-mono); letter-spacing:2px; text-transform:uppercase; color:var(--muted); padding-top:5px">${lbl}</strong><span style="min-width:0; white-space:nowrap; overflow:hidden; text-overflow:ellipsis">${xs.length ? xs.slice(0, 4).join(', ') + (xs.length > 4 ? ` and ${xs.length - 4} more` : '') : none}</span></div>`;
    const desc = `${nick(ab)} this winter: ${c.n ? `${fmtW(c.net)} wins from ${pz(c.n, 'graded move', 'graded moves')}` : 'no graded move yet'}, ${c.ins.length} in, ${c.outs.length} out, ${own.length ? pz(own.length, 'free agent', 'free agents') + ' still unsigned' : 'no free agent of note unsigned'}.`;
    return {id: ab.toLowerCase(), title: `${CLUB_NAME[ab] || ab}: the winter so far · Front Office Ledger`, desc, to: `#view=stove&id=${ab.toLowerCase()}`, link: `The ${nick(ab)} winter page on Front Office Ledger`,
      inner: kick('The 2026-27 winter, club by club') + `<div style="display:flex; align-items:center; gap:20px; margin-top:8px">${head(CLUB_NAME[ab] || ab, 60)}<span style="margin-left:auto; display:flex; align-items:center; gap:14px">${L !== '–' ? grade(L, 46) : ''}${c.n ? `<strong class="${c.net >= 0 ? 'pos' : 'neg'}" style="font:700 40px var(--f-mono)">${fmtW(c.net)}</strong>` : ''}</span></div>
        <div style="height:5px; background:var(--tc); ${folTC(ab)}; margin:14px 0 6px"></div>`
        + line('Gained', c.ins.map(nm).filter(Boolean), 'nobody yet') + line('Lost', c.outs.map(nm).filter(Boolean), 'nobody yet') + line('Still unsigned', own.map(q => q[0]), 'none') + line('Needs', c.needs.filter(x => !c.filled.includes(x)), 'no clear need')};
  });
  // the 20 best and 20 worst winters
  const st = offsSettled().slice().sort((a, b) => b.tot - a.tot), top = st.slice(0, 20).concat(st.slice(-20)), pick = top.concat(st.filter(r => KEEP_O.includes(r.id) && !top.includes(r)));
  // Nov 12 (round 41): a rank is shown only inside the top or bottom 20; exact ties share a rank (T-18); a page kept
  // outside the 20s (round 36) carries no rank at all (it used to read "#675 worst" for a +18.2 winter)
  const rankTxt = (r, unit) => {
    if(TOO_CLOSE[r.id]) return `One of the two best ${unit}s on record (too close to rank vs ${TOO_CLOSE[r.id]})`;
    const t1 = x => Math.round(x.tot * 10), me = t1(r);      // ranks and ties on the shown value (one decimal)
    const hi = st.filter(x => t1(x) > me).length + 1, lo = st.filter(x => t1(x) < me).length + 1, tie = st.filter(x => t1(x) === me).length > 1;
    if(hi <= 20) return `The ${tie ? 'T-' : '#'}${hi} best ${unit} since 1998`;
    if(lo <= 20) return `The ${tie ? 'T-' : '#'}${lo} worst ${unit} since 1998`;
    return null;
  };
  const O = pick.map(r => { const nm = `${offsYr(r.w)} ${offsName(r)}`, rkD = rankTxt(r, 'offseason'), rkK = rankTxt(r, 'winter');
    const mv = r.moves.slice(0, 3).map(m => `<div style="display:flex; gap:14px; margin-top:10px; font-size:24px"><span style="min-width:0; white-space:nowrap; overflow:hidden; text-overflow:ellipsis">${m[2]}</span><strong class="${m[3] >= 0 ? 'pos' : 'neg'}" style="margin-left:auto; font:700 24px var(--f-mono)">${fmtW(m[3])}</strong></div>`).join('');
    return {id: r.id, title: `${nm}: ${fmtW(r.tot)} wins in one winter · Front Office Ledger`, desc: `${rkD || `A ${fmtW(r.tot)}-win offseason`}, under ${r.exec || 'that front office'}: trades ${fmtW(r.tr)}, free agents ${fmtW(r.fa)}. ${r.moves[0] ? r.moves[0][2] + '.' : ''}`,
      to: `#view=winters&id=${r.id}`, link: `${nm} on Front Office Ledger`,
      inner: kick(`${rkK || 'One winter, every move graded'} · ${r.exec || ''}`) + `<div style="display:flex; align-items:center; gap:20px; margin-top:6px">${chip(r.ab, 30)}${head(nm, nm.length > 30 ? 46 : 54)}<strong class="${r.tot >= 0 ? 'pos' : 'neg'}" style="margin-left:auto; font:700 52px var(--f-mono); white-space:nowrap">${fmtW(r.tot)}</strong></div>
        <div style="font-size:24px; color:var(--ink-2); margin-top:8px">Trades ${fmtW(r.tr)} · free agents ${fmtW(r.fa)}${r.prevW != null && r.nextW != null ? ` · ${r.prevW} wins before, ${r.nextW} after` : ''}</div><div style="border-top:2px solid var(--ink); margin-top:14px"></div>${mv}`}; });
  return {W, S, O};
}, [KEEP_O, TOO_CLOSE]);
const prev = (dir, id) => { if(!REPO) return null; const f = `${REPO}/${dir}/${id}.html`; return fs.existsSync(f) ? fs.readFileSync(f, 'utf8') : null; };
const ver = new Date().toISOString().slice(0, 10).replace(/-/g, '');
let made = {w: 0, s: 0, o: 0};
for(const [dir, rows] of [['w', data.W], ['s', data.S], ['o', data.O]]){
  for(const r of rows){
    const old = prev(dir, r.id);
    // Nov 12 (round 35): winter pages carry a number too, so they are rebuilt when their description changes, like club pages
    if(old && (dir === 'w' || old.includes(`content="${esc(r.desc)}"`))) continue;      // already built; club and winter pages only when they moved
    await shot(r.inner, `${OUT}/og/${dir}/${r.id}.png`);
    fs.writeFileSync(`${OUT}/${dir}/${r.id}.html`, page({title: r.title, desc: r.desc, path: `${dir}/${r.id}`, img: `og/${dir}/${r.id}.png`, to: r.to, link: r.link, ver}));
    made[dir]++;
  }
}
fs.writeFileSync(`${OUT}/share.json`, JSON.stringify({built: new Date().toISOString(), w: data.W.map(r => r.raw), s: 1, o: data.O.map(r => r.id)}));
// RSS: newest first, one item per graded move, so a reader or an RSS-to-X service can follow the Wire
const rfc = d => new Date(String(d).slice(0, 10) + 'T17:00:00Z').toUTCString();
const feedRows = data.W.slice().sort((a, b) => String(b.d).localeCompare(String(a.d))).slice(0, 40);
fs.writeFileSync(`${OUT}/feed.xml`, `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom"><channel>
<title>Front Office Ledger: The Wire</title>
<link>https://frontofficeledger.com/#view=wire</link>
<atom:link href="https://frontofficeledger.com/feed.xml" rel="self" type="application/rss+xml"/>
<description>Every MLB move of the 2026-27 winter, graded the day it happens.</description>
<language>en-us</language>
${feedRows.map(r => `<item><title>${esc(r.h)}</title><link>https://frontofficeledger.com/w/${r.id}</link><guid isPermaLink="true">https://frontofficeledger.com/w/${r.id}</guid><pubDate>${rfc(r.d)}</pubDate><description>${esc(r.desc)}</description></item>`).join('\n')}
</channel></rss>
`);
console.log(`share pages written: ${made.w} moves (of ${data.W.length}), ${made.s} clubs (of ${data.S.length}), ${made.o} winters (of ${data.O.length}) -> ${OUT}`);
await b.close();
