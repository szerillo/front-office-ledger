// grade the fixed deal set on one build. PAGE=<index.html> DEALS=<json> OUT=<json> [FAIR=1 writes typed totals]
// [SWAP=<live dump json>: put live MOVE_BANDS and DESK.deals into the page first (control C')] [SEED=1: dpw 2027 +10%]
import { open } from '/tmp/deploy/good4/tests/_common.mjs'; import fs from 'fs';
const D = JSON.parse(fs.readFileSync(process.env.DEALS, 'utf8'));
const swap = process.env.SWAP ? JSON.parse(fs.readFileSync(process.env.SWAP, 'utf8')) : null;
const {browser, page, errors} = await open();
await page.evaluate(async () => { try { await dkDealsLoad(); } catch(e){} });
await page.waitForFunction(() => DESK && DESK.deals, null, {timeout: 30000});
const out = await page.evaluate(({D, swap, fair, seed}) => {
  if(swap){ for(const k of Object.keys(MOVE_BANDS)) delete MOVE_BANDS[k]; Object.assign(MOVE_BANDS, swap.MOVE_BANDS); DESK.deals = swap.DESK.deals; }
  if(seed) DESK.market.dpw['2027'] = DESK.market.dpw['2027'] * 1.1;
  const P = id => DESK.players.find(x => x[1] === id);
  const piece = id => { const p = P(id); return {kind: 'player', p, ctrl: gmIsProsRow(p) ? 6 : gmCtrlOf(p)}; };
  const read = html => { const d = document.createElement('div'); d.innerHTML = html;
    return {letters: [...d.querySelectorAll('.grade')].map(e => e.textContent.trim()).filter(t => /^[A-F][+-]?$/.test(t)),
            tiles: [...d.querySelectorAll('.tile .val')].map(e => e.textContent.trim()), text: d.textContent.replace(/\s+/g, ' ').trim(), html}; };
  const res = {};
  for(const x of D.deals){
    try {
      if(x.mode === 'trade'){
        Object.assign(dkState, {mode: 'trade', you: x.you, them: x.them, send: x.send.map(piece), recv: x.recv.map(piece)});
        res[x.id] = read(dkTradeVerdict());
      } else if(x.mode === 'fa'){
        const p = P(x.pid);
        if(fair){ x.tot = Math.max(1, Math.round(dkFaFair(p, x.yrs).fair * x.factor)); res[x.id] = {tot: x.tot}; continue; }
        res[x.id] = read(dkFaVerdict({p, yrs: x.yrs, tot: x.tot, club: x.club}));
      } else {
        dkState.dr = {recv: x.recv, send: x.send}; dkState.mode = 'draft'; res[x.id] = read(dkDraftVerdict());
      }
    } catch(e){ res[x.id] = {error: String(e).slice(0, 200)}; }
  }
  return res;
}, {D, swap, fair: !!process.env.FAIR, seed: !!process.env.SEED});
if(process.env.FAIR){ for(const x of D.deals) if(x.mode === 'fa') x.tot = out[x.id].tot; fs.writeFileSync(process.env.OUT, JSON.stringify(D, null, 1)); }
else fs.writeFileSync(process.env.OUT, JSON.stringify(out));
console.log(Object.keys(out).length, 'deals; page errors', errors.length, errors.slice(0, 3));
await browser.close();
