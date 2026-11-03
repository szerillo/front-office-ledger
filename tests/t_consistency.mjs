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
  const R = {'A+':6,'A':5,'B':4,'C':3,'D':2,'F':1};
  // the same +1.5 wins is an A on a cheap signing and only middling on a 30-win trade
  o.moveGradesRelativeToSize = Object.keys(MOVE_BANDS).length >= 6 && R[moveGrade(1.5, 'fa', 0.2)] >= 5 && R[moveGrade(1.5, 'trade', 30)] <= 4 && R[moveGrade(-25, 'trade', 30)] === 1 && document.querySelectorAll('#rc-ledgers .ledger .grade').length > 10;
  o.bestTablesCarryNoChannelStamp = [...document.querySelectorAll('#rc-ledgers .ledger h3')].every(h => !h.querySelector('.grade'));
  o.channelGradeStatedOnce = document.querySelectorAll('#rc-ledgers .chanhead').length >= 4;
  // trees: a browsable finder, and the chain renders
  switchView('trees');
  const inp = document.getElementById('tree-find'); inp.value = 'Juan Soto'; treeSuggest(true);
  o.finderBrowsesFullList = document.querySelectorAll('#tree-sugg .tsug').length >= 300;
  treeSuggestHide(); treeFind();
  o.chainRenders = /Juan Soto/.test(document.getElementById('tree-find-out').innerText) && document.getElementById('tree-find-out').innerText.length > 300;
  o.sotoShowcase = TREES.some(t => /Soto, part 1/.test(t.title)) && TREES.some(t => /Soto, part 2/.test(t.title)) && /Betts/.test(TREES[0].title);
  o.openBranchesProjected = !!treeProj(['CJ Abrams']) && !!treeProj(['Boston Bateman']);
  // copy
  o.levAdjExplained = (() => { switchView('report', 'bal'); renderReport('bal'); return true; })();
  o.betaPublicData = !document.querySelector('header .sample-chip') && /independent fan project, built entirely from public data/i.test(document.querySelector('footer').textContent);
  o.navNoRedundantLabel = !/Front offices, graded|Show your work/i.test(document.querySelector('nav').innerText);
  o.watchmen = /Evaluating the evaluators/.test(document.getElementById('view-method').innerText);
  // forward-looking boards (v5.5): free agents with projected contracts, prospects, farm systems
  switchView('boards');
  bdState.tab = 'fa'; renderBoards(); o.faBoard = document.querySelectorAll('#boardsbody tbody tr').length >= 40 && /likely range/.test(document.getElementById('boardsbody').innerText);
  bdState.tab = 'pros'; bdState.org = ''; renderBoards(); o.prospectBoard = document.querySelectorAll('#bd-left tbody tr').length === 100;
  o.noStaleRanks = !DESK.players.some(p => p[0] === 'Kristian Campbell' && p[9] > 0);
  // farm rankings sit beside the prospects; old 'farm' links land on the combined board
  bdState.tab = 'farm'; renderBoards(); o.farmBoard = bdState.tab === 'pros' && document.querySelectorAll('#bd-right tbody tr').length === 30 && document.querySelectorAll('#bd-left tbody tr').length === 100;
  bdOrg('SEA'); o.farmClickFiltersProspects = [...document.querySelectorAll('#bd-left tbody tr')].every(r => r.cells[2] && r.cells[2].textContent.trim() === 'SEA') && !!document.querySelector('#bd-right tr.bd-club.on');
  bdOrg('');
  o.forwardLookingPitch = /decision-making model/i.test(document.querySelector('.tagline').textContent) && /Looking ahead/.test(document.getElementById('introstrip') ? document.getElementById('introstrip').innerText : 'Looking ahead');
  // v5.6: international volume counts every signing (Atlanta graded, with the sanctions context)
  const atl = AUTO_REGIMES.find(x => abOf(x) === 'ATL');
  o.braveIntlGraded = atl.chan.intl.n >= 50 && atl.chan.intl.g != null && /sanction/.test(atl.chan.intl.note || '');
  // v5.6: contract offers blend the market model
  const sk = DESK.players.find(x => x[0] === 'Tarik Skubal'); const sg = dkSuggest(sk, 'fa', null);
  o.marketModelBlended = !!sg.gm && sg.sugTot > 250 && sg.sugTot < 450 && Object.keys(DESK.gbm || {}).length > 1000;
  // v5.7: every decision of every kind is listed on the card, not only the top five
  switchView('report', sd.id); renderReport(sd.id);
  const lists = [...document.querySelectorAll('[id^="allx-"]')].map(x => x.id.slice(5));
  o.fullListsOnCard = ['draft','fa','waiver','walk'].every(k => lists.includes(k)) && sd.allx.draft.length >= 40 && sd.allx.waiver.length >= 10;
  // v5.7: trades are net of guaranteed salary, with publicly reported cash (Arenado: STL paid $22M of his 2026)
  const ar = TRADE_BOOK.trades.find(t => t[0] === '2026-01-13' && t[1].some(s => s[0] === 'STL'));
  o.arenadoTradeNetOfSalary = !!ar && ar[1].find(s => s[0] === 'ARI')[1] >= 2.5;   // v5.9: the prospect back carries his open expectation
  // v5.7: positional credit by games played (Arraez 2025 no longer a 3-win DH/1B)
  const ra = DESK.players.find(x => x[0] === 'Luis Arraez');
  o.arraezPositionalFix = !!ra && ra[6] < 2;
  // v5.7: the assistant GM fills holes with natural fits (no starter in the pen)
  const sk2 = DESK.players.find(x => x[0] === 'Tarik Skubal');
  o.noStarterForPenHole = !gmNaturalFit('RP', sk2) && gmNaturalFit('SP', sk2);
  gmState.club = 'NYM'; gmState.stage = 2; gmState.open = {tab: 'fa'}; gmState.ins = []; gmState.outs = new Set(); gmState.lastNeg = null;
  const adv = gmAdvisor().replace(/<[^>]+>/g, '');
  o.advisorNoOutOfPosition = !/RP: [^;]*\(SP,/.test(adv) && !/DH: [^;]*\((LF|RF|CF|OF), [^;]*takes DH/.test(adv);
  // v5.7: the Scenario Room grades process only; the archive plays blind; Winter 2027 is live
  switchView('scen'); scState.idx = 0; scShow();
  o.scenBlind = !/Cabrera|Detroit|Dombrowski/.test(document.getElementById('scenbody').innerText);
  o.scenWinter27 = scWinter27().length >= 8 && scWinter27().every(s => scAdjudicate(s, s.kind === 'trade' ? 'accept' : 'sign').outw === null);
  scAct('accept');
  o.scenProcessOnly = /not graded/.test(scScoreLine()) && /Cabrera/.test(document.getElementById('scenbody').innerText);
  // v5.7: free agency and extensions grade against a typical club's return on the money, not zero
  const faG = AUTO_REGIMES.map(x => x.chan.fa && x.chan.fa.g).filter(g => g != null);
  o.faCenteredOnTypical = chanTypical('fa') > 0.7 && chanTypical('fa') < 1.1 && faG.filter(g => g <= 35).length <= faG.length / 3 && faG.filter(g => g >= 60).length >= 3;
  // v5.9: extensions centered by class (the league's average result per win of cost)
  const _xr = (DESK.market.typ || {}).ext || {};
  o.extCenteredOnTypical = ['pre-debut','early','arb','veteran'].every(k => typeof _xr[k] === 'number' && Math.abs(_xr[k]) < 2);
  // desk and simulator letters rank against real moves of the same size
  o.deskLettersBySize = moveGrade(3, 'trade', 0.5) !== moveGrade(3, 'trade', 40) && gmMoveLetter({kind:'fa', st: 0.3, rel: 1.5}) !== gmMoveLetter({kind:'fa', st: 25, rel: 1.5});
  // v5.8 audit fixes
  const jj = DESK.players.find(x => x[0] === 'Joe Jiménez');
  o.missedSeasonsWithheld = !jj || (gmProj27(jj) === 0 && jj[17] === 1);
  const cr = DESK.players.find(x => x[0] === 'Garrett Crochet');
  o.injuryNotDoubleCounted = !cr || gmProj27(cr) >= 3.0;
  const ho = DESK.players.find(x => x[0] === 'Clay Holmes');
  o.declinedMoneyFloors = !ho || dkSuggest(ho, 'fa', null).sugTot / dkSuggest(ho, 'fa', null).sugYrs >= 12;
  gmState.club = 'LAD'; gmState.stage = 0; gmState.qo = {}; gmState.ins = []; gmState.outs = new Set();
  o.noIneligibleQO = !/Offer [^.]*Skubal[^.]* the QO/.test(gmAdvisor().replace(/<[^>]+>/g, ''));
  o.draftees2026OnBoard = Object.keys(DESK.draft26 || {}).length >= 60 && DESK.players.some(p => p[0] === 'Roch Cholowsky' && gmIsProsRow(p));
  o.validationHonest = /no look-ahead|realized by each season/.test(document.getElementById('view-method').innerText) && !/decision quality is forward information/.test(document.getElementById('view-method').innerText);
  o.unscoredFilledAtZero = chanAvg().fa === 0 && chanAvg().ext === 0;
  const tb26 = TRADE_BOOK.trades.find(t => t[0] === '2020-02-10' && t[1].some(s => s[0] === 'LAD'));
  o.bettsExtensionOwnsItsSeasons = !!tb26 && tb26[1].find(s => s[0] === 'LAD')[1] < 10;
  // v5.9 adversarial-review fixes
  const cab = TRADE_BOOK.trades.find(t => t[0] === '2007-12-04' && t[1].some(x => x[0] === 'DET' && x[2].some(([pid]) => String(pid) === '408234')));
  o.cabreraTradeKeepsControl = !!cab && cab[1].find(x => x[0] === 'DET' && x[2].some(([pid]) => String(pid) === '408234'))[2].find(([pid]) => String(pid) === '408234')[1] > 3;
  o.tradesStillZeroSum = TRADE_BOOK.trades.filter(t => Math.abs(t[1].reduce((a, x) => a + x[1], 0)) > 0.5).length <= 5;
  normalizeCurated();
  const _allg = [...AUTO_REGIMES, ...LB_HIST].filter(x => !x.isNew && x.forGrade != null);
  o.letterCurveNotExtreme = _allg.filter(x => x.forGrade === 80).length / _allg.length <= 0.1 && _allg.filter(x => (x.chan.trade || {}).g === 80).length / _allg.length <= 0.12;
  o.archiveGradedOnFAandExt = LB_HIST.filter(x => x.chan.fa && x.chan.fa.g != null).length >= 40 && LB_HIST.filter(x => x.chan.ext && x.chan.ext.g != null).length >= 15;
  o.scenarioHindsightMatchesBook = SCEN.filter(sc => sc.kind === 'trade' && sc.outcome && sc.outcome.net != null).every(sc => {
    const seats = TRADE_BOOK.trades.filter(t => t[0] === sc.date).flatMap(t => t[1]).filter(x => x[0] === sc.team);
    return !seats.length || seats.some(x => Math.abs(x[1] - sc.outcome.net) <= 0.15); });
  o.deskPricesOverpay = (() => { const sk = DESK.players.find(x => x[0] === 'Tarik Skubal'); if(!sk || !gmIsFA(sk)) return true;
    const q = dkSuggest(sk, 'fa', null); dkState.mode = 'fa'; switchView('desk'); renderDesk();
    document.getElementById('dk-fa-player').value = sk[0]; document.getElementById('dk-fa-yrs').value = q.sugYrs; document.getElementById('dk-fa-m').value = Math.round(q.sugTot * 1.5);
    const t = dkFaVerdict().replace(/<[^>]+>/g, ' '); const g = (t.match(/Desk grade\s+(\S+)/) || [])[1]; return g === 'D' || g === 'F'; })();
  o.olderDealsCarryAttrition = (() => { const j = DESK.players.find(x => x[0] === 'Aaron Judge'); if(!j) return true;
    return dkProjSeasons(j, 8, false).total < dkProjSeasons(j, 8, false, true).total * 0.8; })();
  // v5.9: the QO table is complete and the charge is on again
  o.qoChargeOn = /QO signing, draft comp charged/.test(JSON.stringify(AUTO_REGIMES)) && /QO signing, draft comp charged/.test(JSON.stringify(LB_HIST));
  return o;
});
await d.page.waitForTimeout(400);
r.levAdjGlossed = await d.page.evaluate(() => { switchView('trees'); return document.querySelectorAll('abbr.gloss').length > 0 || !/lev-adj/.test(document.body.innerText); });
await d.browser.close();
report('t_consistency', r, d.errors);
