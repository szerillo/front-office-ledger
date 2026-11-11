// Nov 11 launch push: OPEN and CLOSED from the facts, the prospect-value note,
// battle card best and worst moves, the player career card, the weekly board
import { open, report } from './_common.mjs';
const {browser, page, errors} = await open();
const r = await page.evaluate(async () => {
  const out = {};
  const flat = t => { const a = []; const f = n => { a.push(n); (n.kids || []).forEach(f); }; f(t); return a; };
  const mo = flat(careerTree('666624'));
  out.morelMiaClosed = mo.some(n => /2025-12-18 · signed with MIA/.test(n.via || '') && n.status === 'closed');
  const mia = AUTO_REGIMES.find(x => x.id === 'mia');
  out.morelCardClosed = [...(mia.chanLedgers.fa.best || []), ...(mia.chanLedgers.fa.worst || [])].filter(x => /Morel/.test(x.h)).every(x => x.open === false);
  const ho = flat(careerTree('605280'));
  const tr = ho.find(n => /2026-08-03 · traded NYM to CHC/.test(n.via || ''));
  out.holmesTradeOpen = !!tr && tr.status === 'open';
  out.holmesProspectNote = !!tr && /prospect value/.test(tr.nm || '');
  out.holmesNymSigningClosed = ho.some(n => /signed with NYM/.test(n.via || '') && n.status === 'closed');
  // no decision before 2021 was reopened, and a played-out one-year deal is closed
  let reopened = 0, oneYrOpen = 0;
  const seen = new Set();
  const walk = (x, d) => { if(!x || typeof x !== 'object' || d > 7 || seen.has(x)) return; seen.add(x);
    if(Array.isArray(x)){ x.forEach(y => walk(y, d + 1)); return; }
    if(x.d && x.h && typeof x.open === 'boolean'){ if(x.open && x.open0 === false) reopened++; if(x.open && /1 yr \/ \$[\d.]+M \(202[0-5]-\d\d winter\)/.test(x.h)) oneYrOpen++; }
    for(const k in x){ if(x[k] && typeof x[k] === 'object') walk(x[k], d + 1); } };
  [...REGIMES, ...AUTO_REGIMES, ...LB_HIST].forEach(x => walk(x, 0));
  out.noneReopened = reopened === 0;
  out.playedOutOneYearClosed = oneYrOpen === 0;
  // battle card
  btState.a = 'lad'; btState.b = 'nym'; switchView('h2h'); renderBattle();
  const bt = document.getElementById('bt-card').innerText;
  out.battleBestWorst = /BEST MOVE/i.test(bt) && /WORST MOVE/i.test(bt) && /Got Josh Fields for Yordan Alvarez/.test(bt);
  // career card
  treeOverlay('605141', 'LAD');
  const cc = document.getElementById('cc-605141');
  out.careerCard = !!cc && /BOS/.test(cc.innerText) && /LAD/.test(cc.innerText) && /extension is graded on its own/.test(cc.innerText);
  closeTreeOverlay();
  // weekly board
  const html = folWeekBoard();
  out.weekBoard = /This week/.test(html) && (html.match(/wk-day/g) || []).length === 7;
  out.noEmDash = !/\u2014/.test(bt + (cc ? cc.innerText : '') + html);
  return out;
});
report('t_nov11', r, errors);
await browser.close();
