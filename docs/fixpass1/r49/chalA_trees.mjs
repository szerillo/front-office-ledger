import { open } from './_common.mjs';
const d = await open();
const r = await d.page.evaluate(() => {
  const fold = x => String(x||'').normalize('NFD').replace(/[̀-ͯ]/g,'').toLowerCase().trim();
  const names = new Set();
  const walk = n => { if(!n) return; (n.proj||[]).forEach(x => names.add(x)); (n.kids||[]).forEach(walk); };
  (typeof TREES!=='undefined'?TREES:[]).forEach(t => walk(t.root));
  (typeof CHAMPS!=='undefined'?CHAMPS:[]).forEach(c => (c.trees||[]).forEach(t => walk(t.root)));
  const P = DESK.players, exact = new Set(P.map(p=>p[0])), byF = {};
  P.forEach(p => (byF[fold(p[0])] = byF[fold(p[0])] || []).push(p[0]));
  const all=[...names], diac = all.filter(n => fold(n) !== n.toLowerCase().trim());
  const miss = all.filter(n => !exact.has(n)), foldHit = miss.filter(n => byF[fold(n)]);
  return {names: all.length, withDiacritics: diac.length, exactMiss: miss.length, missButFoldMatches: foldHit.map(n=>[n, byF[fold(n)]]), missNoMatch: miss.filter(n=>!byF[fold(n)]).slice(0,30)};
});
console.log(JSON.stringify(r)); await d.browser.close();
