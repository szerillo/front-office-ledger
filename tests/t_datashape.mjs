// Nov 12 (round 35): t_build leaves the 24 named data blocks out of the page-code hash. This check covers them:
// a block under 200 characters (the empty defaults the page uses until book.js loads, e.g. TRADE_BOOK) must match
// its pinned text exactly; a larger block (engine data) must keep its shape: top-level type, key set of fixed-key
// objects, element shape of arrays, value shape of id-keyed maps, two levels down. Data refreshes keep shapes.
// After an intended change: UPDATE=1 REASON="..." node tests/t_datashape.mjs
import fs from 'fs'; import vm from 'vm'; import crypto from 'crypto';
const PAGE = process.env.PAGE || '/work/front-office-ledger-prototype.html';
const FIX = new URL('./fixtures/data_shape.json', import.meta.url);
const NAMES = 'AUTO_REGIMES CALIB CHAMPS_AUTO CHAMP_LINES CURATED_EXTRA DESK DEV_MAP EXT_MAP FA_SKILL GMC LB_HIST METHOD_VIZ MOVE_BANDS PLAYER_MOVES PLAYER_MOVE_TYPES PLAYER_ORIGIN SCEN TRADE_BOOK PLAYER_NAMES PLAYER_RANKS TEAM_WL TRADE_STAR QUIZ_CTX PLAYER_FATE'.split(' ');
const L = fs.readFileSync(PAGE, 'utf8').split('\n');
const DECL = new RegExp('^(?:const|let|var)\\s+(' + NAMES.join('|') + ')\\s*=');
const blocks = {};
for(let i = 0; i < L.length; i++){
  const m = L[i].match(DECL); if(!m) continue;
  let depth = 0, j = i;
  for(; j < L.length; j++){ let q = null, esc = false;
    for(const ch of L[j]){ if(q){ if(esc) esc = false; else if(ch === '\\') esc = true; else if(ch === q) q = null; }
      else if(ch === '"' || ch === "'") q = ch; else if('[{('.includes(ch)) depth++; else if(']})'.includes(ch)) depth--; }
    if(depth <= 0) break; }
  blocks[m[1]] = L.slice(i, j + 1).join('\n'); i = j;
}
const idLike = ks => ks.length > 40 || (ks.length > 0 && ks.every(k => /^[0-9|:-]+$/.test(k)));
const shape = (v, d) => {
  if(v === null) return 'null';
  if(Array.isArray(v)){ if(d <= 0 || !v.length) return 'arr'; const s = [...new Set(v.slice(0, 3).map(x => JSON.stringify(shape(x, d - 1))))].sort(); return ['arr', s]; }
  if(typeof v === 'object'){ const ks = Object.keys(v); if(d <= 0) return 'obj';
    if(idLike(ks)) return ['map', ks.length ? shape(v[ks[0]], d - 1) : 'empty'];
    return ['obj', Object.fromEntries(ks.sort().map(k => [k, shape(v[k], d - 1)]))]; }
  return typeof v === 'number' ? 'num' : typeof v;
};
const now = {}; const problems = [];
for(const n of NAMES){
  const t = blocks[n];
  if(t == null){ now[n] = 'missing'; continue; }
  if(t.length < 200){ now[n] = 'text:' + crypto.createHash('sha256').update(t).digest('hex').slice(0, 16); continue; }
  try {
    const ctx = vm.createContext({JSON});
    // the declaration line may hold more than one name (PLAYER_ORIGIN); evaluate the statement and read the name back
    vm.runInContext(t.replace(/^(const|let)\s/, 'var ').replace(/\/\/ [A-Z_]+-END\s*$/, ''), ctx);
    now[n] = JSON.stringify(shape(ctx[n], 3));
  } catch(e){ now[n] = 'eval-error'; problems.push(n + ': ' + String(e).slice(0, 60)); }
}
if(process.env.UPDATE === '1'){
  if(!process.env.REASON){ console.log('UPDATE=1 needs REASON'); process.exit(1); }
  fs.writeFileSync(FIX, JSON.stringify({reason: process.env.REASON, at: new Date().toISOString(), blocks: now}, null, 1));
  console.log('fixture written'); process.exit(0);
}
const want = JSON.parse(fs.readFileSync(FIX, 'utf8')).blocks;
const changed = NAMES.filter(n => now[n] !== want[n]);
console.log('t_datashape', JSON.stringify({blocks: NAMES.length, pinnedText: Object.values(now).filter(v => String(v).startsWith('text:')).length, changed, problems}, null, 1));
if(changed.length || problems.length){ console.log('FAIL:', changed.concat(problems).join(', ')); process.exitCode = 1; } else console.log('PASS');
