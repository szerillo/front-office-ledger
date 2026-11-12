// Build check (Nov 11): the built page must load with zero JS errors and carry the same page code as the last
// approved build. Data lines (the long JSON payloads) are left out of the code hash, so a data refresh passes and a
// build step that deletes or changes page code fails. After an intended code change: UPDATE=1 REASON="..." node tests/t_build.mjs
import fs from 'fs';
import crypto from 'crypto';
import { open, report } from './_common.mjs';
const PAGE = process.env.PAGE || '/work/front-office-ledger-prototype.html';
const FIX = new URL('./fixtures/page_code.json', import.meta.url);
// Nov 12 (round 35): data = the declarations the engine and the build write, by name, whole statement (single
// line or a multi-line block). Everything else is page code. Round 34's "literal declaration" rule hid hand-written
// tables (MIN_N, CHANNELS, DNA_MET) and broke on the engine's pretty-printed EXT_MAP; length and shape are not data.
const DATA_NAMES = 'AUTO_REGIMES CALIB CHAMPS_AUTO CHAMP_LINES CURATED_EXTRA DESK DEV_MAP EXT_MAP FA_SKILL GMC LB_HIST METHOD_VIZ MOVE_BANDS PLAYER_MOVES PLAYER_MOVE_TYPES PLAYER_ORIGIN SCEN TRADE_BOOK PLAYER_NAMES PLAYER_RANKS TEAM_WL TRADE_STAR QUIZ_CTX PLAYER_FATE'.split(' ');
const DECL = new RegExp('^(?:const|let|var)\\s+(' + DATA_NAMES.join('|') + ')\\s*=');
function dataMask(L){
  const m = new Array(L.length).fill(false);
  for(let i = 0; i < L.length; i++){
    if(!DECL.test(L[i])) continue;
    let depth = 0, j = i;
    for(; j < L.length; j++){
      let q = null, esc = false;
      for(const ch of L[j]){
        if(q){ if(esc) esc = false; else if(ch === '\\') esc = true; else if(ch === q) q = null; }
        else if(ch === '"' || ch === "'") q = ch;
        else if('[{('.includes(ch)) depth++;
        else if(']})'.includes(ch)) depth--;
      }
      if(depth <= 0) break;
    }
    for(let k = i; k <= Math.min(j, L.length - 1); k++) m[k] = true;
    i = j;
  }
  return m;
}
const lines = fs.readFileSync(PAGE, 'utf8').split('\n');
const mask = dataMask(lines);
const code = lines.filter((l, i) => !mask[i]).map(l => l.replace(/\s+$/, ''));
// the cache-busting hashes in script URLs change with the data; mask them
// Nov 12 (round 41, staged): content-hash file names (hash_names.py) change with the data like ?v= did; mask them too.
// Whether each name matches its file's bytes is t_hashnames.mjs's job, not this test's.
const norm = code.map(l => l.replace(/\?v=[0-9a-f]{6,}/g, '?v=*').replace(/\.[0-9a-f]{10}\.(js|json)\b/g, '.*.$1'));
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
