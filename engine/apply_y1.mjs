// Surgical update: change only the year-one base (index 16) of the listed players inside the page's DESK
// and in desk_data.json, leaving every other field exactly as it is.
import fs from 'fs';
const ch = JSON.parse(fs.readFileSync('/work/y1_changes.json', 'utf8'));
const P = '/work/front-office-ledger-prototype.html'; let s = fs.readFileSync(P, 'utf8');
const k = s.indexOf('\nconst DESK = ') + 1, e = s.indexOf('\n', k); const line = s.slice(k, e);
const DESK = (0, eval)('(' + line.slice('const DESK = '.length).replace(/;\s*$/, '') + ')');
let n = 0, bad = 0;
for(const p of DESK.players){ const c = ch[String(p[1])]; if(!c) continue; if(Math.abs(p[16] - c[0]) > 1e-9){ bad++; continue; } p[16] = c[1]; n++; }
const js = JSON.stringify(DESK);
const lit = "'" + js.replace(/\\/g, '\\\\').replace(/'/g, "\\'").replace(/\u2028/g, '\\u2028').replace(/\u2029/g, '\\u2029').replace(/<\//g, '<\\/') + "'";
const back = (0, eval)('(JSON.parse(' + lit + '))'); if(JSON.stringify(back) !== js) throw new Error('round trip failed');
s = s.slice(0, k) + 'const DESK = JSON.parse(' + lit + ');' + s.slice(e); fs.writeFileSync(P, s);
const D = JSON.parse(fs.readFileSync('/work/desk_data.json', 'utf8')); let m = 0;
for(const p of D.players){ const c = ch[String(p[1])]; if(c && Math.abs(p[16] - c[0]) < 1e-9){ p[16] = c[1]; m++; } }
fs.writeFileSync('/work/desk_data.json', JSON.stringify(D));
console.log('page players updated', n, 'skipped (base differed)', bad, '| desk_data.json updated', m, '| line length', line.length, '->', ('const DESK = JSON.parse(' + lit + ');').length);
