// Nov 12 (round 40): fails if index.html loads any local .js/.json file that is not named by its own content hash,
// except the three files the daily jobs rewrite in place. Also checks the cards part loaded from the cards file.
// Usage: PAGE=<site>/index.html node tests/t_hashnames.mjs
import fs from 'fs'; import path from 'path'; import crypto from 'crypto';
const PAGE = process.env.PAGE || '/work/front-office-ledger-prototype.html', DIR = path.dirname(PAGE);
const LIVE = new Set(['rumors.json', 'share.json', 'wire.json']);
const md5 = f => crypto.createHash('md5').update(fs.readFileSync(f)).digest('hex');
const src = fs.readFileSync(PAGE, 'utf8'), bad = [], ok = [];
const refs = new Set([...src.matchAll(/['"`]([\w.-]+\.(?:js|json))(?=[?'"`]|\$)/g)].map(m => m[1]));
const check = (name, from) => {
  if(LIVE.has(name)) { ok.push(name + ' (live file, exempt)'); return; }
  const m = name.match(/^(.+)\.([0-9a-f]{10})\.(js|json)$/);
  if(!m) { bad.push(`${from} loads ${name}: not content-hash named`); return; }
  const f = path.join(DIR, name);
  if(!fs.existsSync(f)) { bad.push(`${from} loads ${name}: file missing`); return; }
  if(md5(f).slice(0, 10) !== m[2]) { bad.push(`${name}: name says ${m[2]}, bytes are ${md5(f).slice(0, 10)}`); return; }
  ok.push(name);
};
for(const r of refs) check(r, 'index.html');
const cards = [...refs].find(r => /^cards\.[0-9a-f]{10}\.js$/.test(r));
if(!cards) bad.push('index.html loads no hashed cards file');
else if(fs.existsSync(path.join(DIR, cards))) for(const m of fs.readFileSync(path.join(DIR, cards), 'utf8').matchAll(/'(cards2[\w.]*\.js)'/g)) check(m[1], cards);
console.log(JSON.stringify({checked: ok.length + bad.length, ok, bad}, null, 1));
console.log(bad.length ? `t_hashnames FAIL (${bad.length})` : `t_hashnames PASS (${ok.length})`); process.exit(bad.length ? 1 : 0);
