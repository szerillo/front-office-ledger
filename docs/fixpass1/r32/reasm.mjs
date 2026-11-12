// load cards.js + cards2.js in either order into a fake window; md5 of the merged CARD_DETAIL in the original key order
import fs from 'fs'; import vm from 'vm'; import crypto from 'crypto';
const [dir, orig] = process.argv.slice(2);
const o = fs.readFileSync(orig, 'utf8'); const body = o.slice('window.CARD_DETAIL = '.length, o.lastIndexOf(";\nif(typeof"));
const keys = Object.keys(JSON.parse(body)); const md5 = s => crypto.createHash('md5').update(s).digest('hex');
for (const order of [['cards.js', 'cards2.js'], ['cards2.js', 'cards.js']]) {
  let merged = 0; const added = [];
  const win = {}; win.window = win; win.cardsMerge = () => merged++;
  win.document = {createElement: () => ({}), body: {appendChild: c => added.push(c.src)}};
  const ctx = vm.createContext(win);
  for (const f of order) vm.runInContext(fs.readFileSync(dir + '/' + f, 'utf8'), ctx);
  const D = win.CARD_DETAIL; const re = JSON.stringify(Object.fromEntries(keys.map(k => [k, D[k]])));
  console.log(order.join('+'), 'clubs', Object.keys(D).length, 'merge calls', merged, 'md5', md5(re), md5(re) === md5(JSON.stringify(JSON.parse(body))) ? 'EQUAL to original as the page sees it' : 'DIFFERENT', 'starts', added.join(','));
}
const canon = JSON.stringify(JSON.parse(body)); console.log('original md5 raw', md5(body), 'original parsed+restringified by JS', md5(canon));
