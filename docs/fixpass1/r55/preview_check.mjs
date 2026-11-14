// Round 55 (Nov 14 audit, blocker 1): every report card's share page (c/<id>.html) and preview image (og/<id>.png)
// match the card as the site renders it. Pass: for every card, the share title's letter = the Overall tile, the share
// description's wins = the Net tile, "(under review)" in the title exactly when the card carries the review note, the
// og:image URL carries a version tag, and the image is the one in og/cards-manifest.json (md5 of the served file) whose
// recorded letter, wins and review flag also equal the card.
// Exit 1 on any miss. Usage: [TARGET=live LIVE_URL=<site>] node preview_check.mjs
import { open, report } from './_common.mjs';
import crypto from 'crypto';
const BASE = process.env.TARGET === 'live' ? (process.env.LIVE_URL || 'https://frontofficeledger.com/') : null;
const d = await open();
let r = await d.page.evaluate(async (BASE) => {
  if (typeof cardsReady === 'function') { try { await cardsReady(); } catch (e) {} }
  normalizeCurated();
  const slug = id => String(id).toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
  const get = async (u, bin) => { const x = await fetch(BASE + u + (u.includes('?') ? '&' : '?') + 't=' + Date.now(), {cache: 'no-store'}); if (!x.ok) return null; if (!bin) return x.text(); const b = new Uint8Array(await x.arrayBuffer()); let s = ''; for (let i = 0; i < b.length; i += 8192) s += String.fromCharCode.apply(null, b.subarray(i, i + 8192)); return btoa(s); };
  const man = JSON.parse(await get('og/cards-manifest.json') || '{"cards":{}}').cards;
  const pages = [...(typeof REGIMES !== 'undefined' ? REGIMES : []), ...AUTO_REGIMES, ...LB_HIST.filter(x => x.realCard)];
  const seen = new Set(), out = [];
  for (const reg of pages) {
    if (seen.has(reg.id)) continue; seen.add(reg.id);
    renderReport(reg.id);
    const root = document.getElementById('view-report');
    const tile = lbl => [...root.querySelectorAll('.tile')].find(t => (t.querySelector('.lbl') || {}).textContent === lbl);
    const ov = tile('Overall grade'), nt = tile('Net value vs. expectation');
    const card = {letter: ov ? ov.querySelector('.grade').textContent.trim() : null, net: nt ? (nt.querySelector('.val').firstChild.textContent || '').trim() : null, review: !!root.querySelector('[data-review="card"]'), isNew: !!reg.isNew};
    const html = await get('c/' + slug(reg.id) + '.html');
    out.push({id: reg.id, s: slug(reg.id), card, html, man: man[slug(reg.id)] || null, png: await get('og/' + slug(reg.id) + '.png', true)});
  }
  // team share pages (t/<ab>): title grade and wins against the team view's own facts
  const teams = [];
  for (const ab of Object.keys(DESK.teams || {}).sort()) { const f = folCardFacts(ab); if (!f) continue;
    teams.push({ab, grade: f.grade, net: fmtW(f.net), rv: typeof CTRL_REVIEW !== 'undefined' && !!CTRL_REVIEW[ab.toLowerCase()], html: await get('t/' + ab.toLowerCase() + '.html')}); }
  return {out, teams};
}, BASE || 'http://127.0.0.1:8767/r55/tree/');
const problems = []; let ok = 0; const teams = r.teams; r = r.out;
const A = s => (s || '').replace(/&amp;/g, '&').replace(/&quot;/g, '"').replace(/&#x27;/g, "'");
for (const x of r) {
  const p = m => problems.push(x.id + ': ' + m);
  if (!x.html) { p('no share page'); continue; }
  const title = A((x.html.match(/<title>([^<]*)/) || [])[1]), desc = A((x.html.match(/name="description" content="([^"]*)/) || [])[1]);
  const img = (x.html.match(/og:image" content="([^"]*)/) || [])[1] || '';
  const tl = (title.match(/: ([A-F][+\-−]?|new, not yet graded)( \(under review\))? ·/) || []);
  if (x.card.isNew) { if (!/new, not yet graded/.test(title)) p('new card, title ' + title); }
  else {
    if (tl[1] !== x.card.letter) p(`title letter ${tl[1]} vs card ${x.card.letter}`);
    const dn = (desc.match(/Overall [^,]+, ([+\-−]?[\d.]+) wins vs expectation/) || [])[1];
    if (dn !== x.card.net) p(`desc wins ${dn} vs card ${x.card.net}`);
  }
  if (!!tl[2] !== x.card.review && !x.card.isNew) p(`title review ${!!tl[2]} vs card ${x.card.review}`);
  if (!/\?v=\w+/.test(img)) p('og:image has no version tag');
  if (!x.man) { p('not in manifest'); continue; }
  if (!x.card.isNew && (x.man.overall !== x.card.letter || x.man.net !== x.card.net)) p(`image rendered with ${x.man.overall} ${x.man.net} vs card ${x.card.letter} ${x.card.net}`);
  if (x.man.review !== x.card.review) p(`image review ${x.man.review} vs card ${x.card.review}`);
  const md5 = x.png ? crypto.createHash('md5').update(Buffer.from(x.png, 'base64')).digest('hex') : null;
  if (md5 !== x.man.png) p(`served image md5 ${md5} vs manifest ${x.man.png}`);
  if (!problems.some(q => q.startsWith(x.id + ': '))) ok++;
}
let tok = 0;
for (const t of teams) {
  const n0 = problems.length, p = m => problems.push('t/' + t.ab + ': ' + m);
  if (!t.html) { p('no team share page'); continue; }
  const title = A((t.html.match(/<title>([^<]*)/) || [])[1]), desc = A((t.html.match(/name="description" content="([^"]*)/) || [])[1]);
  const m = title.match(/front office: (\S+?)( \(under review\))? \u00b7/) || [];
  if (m[1] !== t.grade) p(`title grade ${m[1]} vs team view ${t.grade}`);
  if (!!m[2] !== t.rv) p(`title review ${!!m[2]} vs ${t.rv}`);
  if (!desc.includes(`${t.net} wins vs. a typical front office`)) p(`desc lacks ${t.net} wins`);
  if (!/og:image" content="[^"]*\?v=\w+/.test(t.html)) p('og:image has no version tag');
  if (problems.length === n0) tok++;
}
console.log('problems:', problems.length, problems.slice(0, 15));
report('preview_check', {cards: r.length, cards_ok: ok, teams: teams.length, teams_ok: tok, all_ok: ok === r.length && r.length >= 150 && tok === teams.length && teams.length === 30, problems_0: problems.length === 0}, d.errors);
await d.browser.close();
