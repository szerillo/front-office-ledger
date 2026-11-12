// Build check (Nov 11): the built page must load with zero JS errors and carry the same page code as the last
// approved build. Data lines (the long JSON payloads) are left out of the code hash, so a data refresh passes and a
// build step that deletes or changes page code fails. After an intended code change: UPDATE=1 REASON="..." node tests/t_build.mjs
import fs from 'fs';
import crypto from 'crypto';
import { open, report } from './_common.mjs';
const PAGE = process.env.PAGE || '/work/front-office-ledger-prototype.html';
const FIX = new URL('./fixtures/page_code.json', import.meta.url);
// Nov 12 (round 34): long lines are not data by length alone; 176 code lines over 400 chars (105 KB, e.g. the Deal
// Desk GM line) were outside the hash. Data = a declaration of a literal or JSON.parse payload, or a bare literal line.
const isData = l => { const t = l.trim(); return /^(const|let|var)\s+[\w$]+\s*=\s*(JSON\.parse\('|[\[{"0-9-])/.test(t) || /^[\[\]{}"0-9-]/.test(t); };
const lines = fs.readFileSync(PAGE, 'utf8').split('\n');
const code = lines.filter(l => !isData(l)).map(l => l.replace(/\s+$/, ''));
// the cache-busting hashes in script URLs change with the data; mask them
const norm = code.map(l => l.replace(/\?v=[0-9a-f]{6,}/g, '?v=*'));
const sha = crypto.createHash('sha256').update(norm.join('\n')).digest('hex').slice(0, 16);
if (process.env.UPDATE === '1') {
  if (!process.env.REASON) { console.log('UPDATE=1 needs REASON'); process.exit(1); }
  fs.writeFileSync(FIX, JSON.stringify({ sha, codeLines: norm.length, reason: process.env.REASON, at: new Date().toISOString() }, null, 1));
  console.log('page_code fixture written', sha, norm.length);
}
const fx = JSON.parse(fs.readFileSync(FIX, 'utf8'));
const {browser, page, errors} = await open();
const live = await page.evaluate(() => ({ dollar: typeof $ === 'function', cards: window.CARDS_READY === true, moves: window.MOVES_READY === true,
  regimes: typeof AUTO_REGIMES !== 'undefined' && AUTO_REGIMES.length === 30, teamsel: document.querySelectorAll('#teamsel option').length > 30 }));
const r = {
  codeHashMatches: sha === fx.sha,
  codeLineCount: norm.length === fx.codeLines,
  helpersPresent: live.dollar,
  cardsLoaded: live.cards, movesLoaded: live.moves,
  reportCardsBuilt: live.regimes && live.teamsel,
  zeroPageErrors: errors.length === 0,
};
if (!r.codeHashMatches) console.log('code hash', sha, 'expected', fx.sha, '| code lines', norm.length, 'expected', fx.codeLines);
await browser.close();
report('t_build', r, errors);
