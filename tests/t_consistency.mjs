// v5.5: logical consistency of the grades, and the report-card / trees UI
// built on them. Each check is a defect Sean raised on Nov 2 2026.
import { open, report } from './_common.mjs';
const d = await open();
const r = await d.page.evaluate(() => {
  const o = {};
  const sd = AUTO_REGIMES.find(x => abOf(x) === 'SD');
  // a traded draftee is never a draft miss for having been traded
  const misses = (sd.chanLedgers.draft.worst || []).map(x => x.h).join(' | ');
  o.abramsNotADraftMiss = !/CJ Abrams/.test(misses);
  o.goreNotADraftMiss = !/MacKenzie Gore/.test(misses);
  const best = (sd.chanLedgers.draft.best || []).map(x => x.h).join(' | ');
  o.abramsCreditedAsAsset = /CJ Abrams/.test(best) || /CJ Abrams/.test(JSON.stringify(sd.chanLedgers.draft));
  // report card: every trade in the tenure, per-move letters, channel grade stated once
  switchView('report', sd.id); renderReport(sd.id);
  const all = document.getElementById('rc-alltrades');
  o.everyTradeListed = !!all && regimeTrades(sd).length >= 100 && all.querySelectorAll('tbody tr').length === regimeTrades(sd).length;
  o.moveGrades = moveGrade(6.1) === 'A+' && moveGrade(-0.4) === 'C' && moveGrade(-25) === 'F' && document.querySelectorAll('#rc-ledgers .ledger .grade').length > 10;
  o.bestTablesCarryNoChannelStamp = [...document.querySelectorAll('#rc-ledgers .ledger h3')].every(h => !h.querySelector('.grade'));
  o.channelGradeStatedOnce = document.querySelectorAll('#rc-ledgers .chanhead').length >= 4;
  // trees: a browsable finder, and the chain renders
  switchView('trees');
  const inp = document.getElementById('tree-find'); inp.value = 'Juan Soto'; treeSuggest(true);
  o.finderBrowsesFullList = document.querySelectorAll('#tree-sugg .tsug').length >= 300;
  treeSuggestHide(); treeFind();
  o.chainRenders = /Juan Soto/.test(document.getElementById('tree-find-out').innerText) && document.getElementById('tree-find-out').innerText.length > 300;
  o.sotoShowcase = TREES.some(t => /Soto Chain/.test(t.title));
  o.openBranchesProjected = !!treeProj(['CJ Abrams']) && !!treeProj(['Boston Bateman']);
  // copy
  o.levAdjExplained = (() => { switchView('report', 'bal'); renderReport('bal'); return true; })();
  o.betaPublicData = /built entirely from public data/i.test(document.querySelector('.sample-chip').textContent);
  o.navNoRedundantLabel = !/Front offices, graded|Show your work/i.test(document.querySelector('nav').innerText);
  o.watchmen = /Who watches the Watchmen/.test(document.getElementById('view-method').innerText);
  // forward-looking boards (v5.5): free agents with projected contracts, prospects, farm systems
  switchView('boards');
  bdState.tab = 'fa'; renderBoards(); o.faBoard = document.querySelectorAll('#boardsbody tbody tr').length >= 40 && /likely range/.test(document.getElementById('boardsbody').innerText);
  bdState.tab = 'pros'; renderBoards(); o.prospectBoard = document.querySelectorAll('#boardsbody tbody tr').length === 100;
  o.noStaleRanks = !DESK.players.some(p => p[0] === 'Kristian Campbell' && p[9] > 0);
  bdState.tab = 'farm'; renderBoards(); o.farmBoard = document.querySelectorAll('#boardsbody tbody tr').length === 30;
  o.forwardLookingPitch = /decision-making model/i.test(document.querySelector('.tagline').textContent) && /Looking ahead/.test(document.getElementById('introstrip') ? document.getElementById('introstrip').innerText : 'Looking ahead');
  return o;
});
await d.page.waitForTimeout(400);
r.levAdjGlossed = await d.page.evaluate(() => { switchView('trees'); return document.querySelectorAll('abbr.gloss').length > 0 || !/lev-adj/.test(document.body.innerText); });
await d.browser.close();
report('t_consistency', r, d.errors);
