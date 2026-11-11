import fs from 'fs';
const w={}; new Function('window',fs.readFileSync('cards.js','utf8'))(w);
const decs=[]; const seen=new Set();
const walk=(o,reg)=>{ if(Array.isArray(o)) o.forEach(x=>walk(x,reg)); else if(o&&typeof o==='object'){ if(o.d&&o.h&&'open' in o){ const k=o.d+'|'+o.h; if(!seen.has(k)){seen.add(k); decs.push({reg,...o});} } for(const k in o) walk(o[k], reg);} };
for(const k in w.CARD_DETAIL) walk(w.CARD_DETAIL[k], k);
const S=JSON.parse(fs.readFileSync('/tmp/sample40.json','utf8')); const used=new Set(S.map(o=>o.d+'|'+o.h));
const ch=o=>o.ch||(/^Trade/.test(o.t)?'trade':/^Free agency/.test(o.t)?'fa':/^Extension/.test(o.t)?'ext':o.t);
const rec=decs.filter(o=>o.d>='2024-01-01'&&['trade','fa','ext'].includes(ch(o))&&typeof o.war==='number'&&!used.has(o.d+'|'+o.h));
const money=o=>{const m=/\$([\d.]+)M/.exec(o.h);return m?+m[1]:0};
const fe=rec.filter(o=>ch(o)!=='trade').sort((a,b)=>money(b)-money(a)).slice(0,12);
const tr=rec.filter(o=>ch(o)==='trade').sort((a,b)=>Math.abs(b.war)-Math.abs(a.war));
const trU=[]; const seenH=new Set(); for(const o of tr){ const k=o.d+(o.pids||[]).slice().sort().join(); if(seenH.has(k)) continue; seenH.add(k); trU.push(o); if(trU.length>=8) break; }
const H=[...fe,...trU]; fs.writeFileSync('/tmp/hi20.json', JSON.stringify(H,null,1));
H.forEach((o,i)=>console.log(i,o.reg,ch(o),o.d,o.war,o.open,'|',o.h.slice(0,120),'|',(o.pids||[]).join(','), '|', String(JSON.stringify(o.sides||"")).slice(0,200)));
