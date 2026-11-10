// Nov 2026: the front door (team picker and team page), heists, the trade quiz,
// the Deal Desk popup with not-interested and make-it-fair, the simulator
// scoreboard and next-decision card, and the phone bottom bar.
import { open, report } from './_common.mjs';
const d = await open();
const R = await d.page.evaluate(async () => {
  const o = {}, wait = ms => new Promise(z => setTimeout(z, ms));
  try { localStorage.removeItem('fol-team'); } catch(e){}
  switchView('home'); await wait(50);
  o.homeIsDefault = typeof routeView === 'function';
  o.pickerHas30 = document.querySelectorAll('#hub-team option').length === 31 && !document.querySelector('#homebody .tchips');
  o.heistOfDay = !!document.querySelector('#homebody .heist') || /Heist of the day/.test(document.getElementById('homebody').textContent);
  o.hubTeasers = ['Trade Grade', 'The best front offices in baseball', 'Run a winter', 'Scenario of the day', 'Signing of the day', 'GM rivalry of the week', 'Remember Some Dudes', 'Featured farm system', 'Champion of the week', "Pick'em"].every(x => document.getElementById('homebody').textContent.includes(x));
  o.hubOrder = [...document.querySelectorAll('#homebody .hub-sec h3')].map(h => h.textContent).join('|') === 'This winter|The front office rankings|From the archive' && document.querySelectorAll('#homebody .hub-arch6 > .card').length === 6 && [...document.querySelectorAll('#homebody .hub-arch6 .home-kick')].map(k => k.textContent).join('|') === 'Trade of the day|Signing of the day|Tree of the day|Champion of the week|Org stat of the day|GM rivalry of the week';
  o.rankByRate = folActiveRank().every((r, i, a) => i === 0 || a[i - 1].gradeRate >= r.gradeRate) && (() => { const rows = [...document.querySelectorAll('#homebody .hub-lbcard .hub-lb:not(.hub-lbhead)')]; const v = rows.map(x => parseFloat(x.querySelector('.hl-ps').textContent)); return rows.length === 8 && /Strength: /.test(rows[0].textContent) && !/Best at/.test(rows[0].textContent) && v.every((x, i) => i === 0 || v[i - 1] >= x); })();
  o.toComeOnReportCard = (() => { const r = curRegOf('MIL'); const rows = regimeTrades(r); return rows.some(x => rcToCome(x, 'MIL') != null) && /Still to come/.test(allTradesTable(r)); })();
  o.champLine48 = Math.abs(folChampLine() - 48) < 1.5;
  o.heistContext = (() => { const t = folTrades().find(x => x.d.startsWith('2003-11') && x.S.some(s => s.ab === 'SF') && x.S.some(s => s.ab === 'MIN')); const c = t && folHeistCtx(t); return c && c.contender && c.r.w === 100; })();
  o.heistsRankedInContext = (() => { const xs = folTrades().slice().sort((a, b) => folHeistAdj(b) - folHeistAdj(a)); return xs.length > 100 && folHeistAdj(xs[0]) >= folHeistAdj(xs[1]); })();
  // Nov 10: Play is one stacked card at the top of the right column (the tile rows took too much room)
  o.hubPlayRail = (() => { const rows = [...document.querySelectorAll('#homebody .hub-cols .hub-right .hub-play .hp-row strong')].map(x => x.textContent); return rows.join('|') === "Deal Desk|Offseason Simulator|Scenario of the day|Pick'em|Trade Grade|Remember Some Dudes" && document.querySelector('#homebody .hub-right').firstElementChild.classList.contains('hub-play'); })() && !!document.querySelector('#homebody .hub-cols .hub-left #hub-wire');
  o.hubSections = /champion line 48/.test(document.getElementById('homebody').textContent) && /Org stat of the day/.test(document.getElementById('homebody').textContent) && /Ledger/.test(document.querySelector('#homebody .hub-fa2').textContent) && /Published/.test(document.querySelector('#homebody .hub-fa2').textContent) && /front offices/.test(document.querySelector('#homebody .hub-stats').textContent) && /\(#\d+ of 30\)/.test(document.getElementById('homebody').textContent);
  document.getElementById('hub-find').value = 'Friedman'; folHubFind();
  o.hubSearch = /Andrew Friedman/.test(document.getElementById('hub-find-out').textContent) && /report card/.test(document.getElementById('hub-find-out').textContent);
  document.getElementById('hub-find').value = 'Mookie'; folHubFind();
  o.hubSearchPlayer = /Mookie Betts/.test(document.getElementById('hub-find-out').textContent);
  document.getElementById('hub-find-out').innerHTML = '';
  folTeamSet('BOS'); folHorizonAll(); await wait(100);
  o.titleRaceAll30 = document.getElementById('hz-club').value === '' && !!document.querySelector('#horizonbody tr.hz-cline');
  try { localStorage.removeItem('fol-team'); } catch(e){}
  switchView('home'); await wait(50);
  o.hubNoDemeaning = !/Is your GM any good/i.test(document.getElementById('homebody').textContent);
  // picking a club opens its report card (the leaderboard's own) with where it stands on top
  folPickTeam('BOS'); await wait(400);
  const rb = document.getElementById('view-report').textContent;
  o.teamPage = !document.getElementById('view-report').hidden && /Craig Breslow/.test(rb) && /#view=cards&id=bos/.test(location.hash);
  o.teamStanding = !!document.querySelector('#rc-standing .rc-standing') && /front offices with two or more seasons in the seat/.test(document.getElementById('rc-standing').textContent) && !document.querySelector('#rc-standing button.actbtn');
  o.teamNotRemembered = folTeam() === '' && (() => { try { return !localStorage.getItem('fol-team'); } catch(e){ return true; } })();
  folOpenAs('BOS', 'gm'); await wait(300);
  o.teamRunWinterOpensClub = !document.getElementById('view-gm').hidden && gmState.club === 'BOS';
  dkState.you = null; switchView('desk'); await wait(100);
  o.noDefaultClubAfter = !dkState.you;
  o.teamTimelinePins = document.querySelectorAll('#view-report svg circle').length >= 3;
  o.teamStandingOnlyCurrent = (() => { const h = LB_HIST.find(x => x.realCard); if(!h) return true; switchView('report', h.id); return !(document.getElementById('rc-standing') || {}).textContent; })();
  // Nov 10: five doors (Home and four sections); the pages of the open section sit in one row under them
  o.navOrder = [...document.querySelectorAll('nav .navtop button')].map(b => b.dataset.view || b.dataset.sec).join() === 'home,winter,fo,hist,play' && [...document.querySelectorAll('nav [data-view]')].length === 20;
  o.navOneRowOpen = (() => { switchView('heists'); const open = [...document.querySelectorAll('nav .navgrp')].filter(g => !g.hidden); const ok = open.length === 1 && open[0].dataset.sec === 'hist' && document.querySelector('nav .navtop button[data-sec="hist"]').classList.contains('on') && document.querySelector('nav button[data-view="heists"]').classList.contains('on'); switchView('home'); return ok && [...document.querySelectorAll('nav .navgrp')].every(g => g.hidden); })();
  o.navDoorOpensFirstPage = (() => { document.querySelector('nav .navtop button[data-sec="fo"]').click(); const ok = routeView() === 'leaderboard'; switchView('home'); return ok; })();
  o.navQuizUnderPlayGM = (() => { const g = [...document.querySelectorAll('nav [data-view]')].map(b => b.dataset.view + (b.dataset.tab ? ':' + b.dataset.tab : '')); return g.slice(-6).join() === 'desk,gm,scen,quiz,dudes,pickem' && g.join().includes('wire:feed,stove,boards:fa,boards:pros,horizon') && g.join().includes('heists,offs,trees') && /Club by Club/.test(document.querySelector('nav button[data-view="stove"]').textContent); })();
  // heists: biggest first, and a club filter shows that club's side
  switchView('heists'); await wait(50);
  const gaps = folTrades().map(t => t.gap).sort((a, b) => b - a);
  o.heistsSorted = document.querySelectorAll('#heistbody .heist').length === 20 && /Luis Gonzalez/.test(document.querySelector('#heistbody .heist').textContent) && Math.abs(folTrades().slice().sort((a, b) => b.gap - a.gap)[0].gap - gaps[0]) < 1e-9;
  heistState.club = 'BOS'; heistState.dir = 'worst'; renderHeists(); await wait(30);
  o.heistsClubWorst = [...document.querySelectorAll('#heistbody .heist')].every(c => /Boston Red Sox got/.test(c.textContent));
  heistState.kind = 'fa'; renderHeists(); await wait(30);
  o.heistsSignings = document.querySelectorAll('#heistbody .heist').length > 0;
  heistState.kind = 'trades'; heistState.club = ''; heistState.dir = 'best';
  // quiz: today's five are the same five for everyone; the right side wins
  quizState = null; switchView('quiz'); await wait(30);
  const a = quizState.qs.map(t => t.key || t.d).join(); quizState = null; renderQuiz(); const b = quizState.qs.map(t => t.key || t.d).join();
  o.quizDailyStable = a === b && quizState.qs.length === 5;
  o.quizMixesContracts = quizState.qs.filter(t => t.kind === 'fa').length === 2 && quizState.qs.filter(t => t.S).length === 3;
  try { localStorage.removeItem('fol-quiz-streak'); localStorage.removeItem('fol-quiz-day-' + quizState.day); } catch(e){}
  quizState.done = false; quizState.ans = []; quizState.i = 0; renderQuiz();
  const t0 = quizState.qs[0], sides = quizState.flip[0] ? [t0.S[1], t0.S[0]] : t0.S, k = sides[0].net >= t0.win.net - 1e-9 ? 0 : 1;
  o.quizPlayerContext = document.querySelectorAll('#quizbody .qp-ctx').length >= 2 && /(Offseason|deadline|In-season) deal/.test(document.getElementById('quizbody').textContent);
  folQuizPick(k); await wait(20);
  o.quizRightAnswer = quizState.ans[0] === true && (folQuizStore('streak') || 0) >= 1 && /Right\./.test(document.getElementById('quizbody').textContent);
  folQuizNext(); await wait(20);
  const f1 = quizState.qs[1], qb = document.getElementById('quizbody').textContent;
  o.quizContractCard = f1.kind === 'fa' && /Did .+ earn his deal\?/.test(qb) && /last three seasons/i.test(qb) && /years, \$/.test(qb);
  folQuizPick(f1.earned ? 0 : 1); await wait(20);
  o.quizContractReveal = quizState.ans[1] === true && /A typical club gets about/.test(document.getElementById('quizbody').textContent);
  o.quizPoolRealized = folQuizPool().every(t => t.d.slice(0, 4) <= '2023' && t.S.length === 2);
  // Deal Desk: a suggested trade, the popup, not interested, make it fair
  dkState.you = null; dkState.them = null; dkState.send = []; dkState.recv = []; dkState.excl = new Set(); dkState.mode = 'trade';
  folOpenAs('BOS', 'desk'); await wait(400);
  o.deskSuggested = dkState.you === 'BOS' && !!dkState.them && dkState.recv.length >= 1 && dkState.send.length >= 1;
  o.suggestNoAutoVerdict = !document.getElementById('dk-out').classList.contains('dk-pop');
  o.suggestNoCornerstone = dkState.recv.every(pc => !gmFranchise(pc.p));
  dkEval(); await wait(30);
  const out = document.getElementById('dk-out');
  o.verdictPopsUp = out.classList.contains('dk-pop') && !!out.querySelector('.dk-pop-x') && !!out.querySelector('.dk-meter') && /Would [A-Z]{2,3} accept\?/.test(out.innerText);
  dkPopClose(); o.popupCloses = !out.classList.contains('dk-pop') && document.body.classList.contains('dk-lock') === false;
  const nixed = dkState.send[0].p[1];
  dkEval(); dkNix('send', 0); await wait(30);
  o.notInterestedRenegotiates = dkExcl().has(nixed) && !dkState.send.some(pc => pc.p && pc.p[1] === nixed) && dkState.send.length >= 1 && document.getElementById('dk-out').classList.contains('dk-pop');
  dkUndo(); await wait(20);
  o.undoRestores = !dkExcl().has(nixed) && dkState.send.some(pc => pc.p && pc.p[1] === nixed);
  dkNix('send', 0); await wait(20);
  o.notInterestedOffBoard = ![...document.querySelectorAll('#deskbody .tboard button')].some(x => x.getAttribute('onclick') && x.getAttribute('onclick').includes(String(nixed)));
  dkPopClose();
  o.memoSkipsPopupChrome = !/Make it fair/.test(dkMemoBody(document.getElementById('dk-out')));
  // simulator: scoreboard and the next decision
  switchView('gm'); await wait(200);
  if(gmState.club !== 'BOS'){ document.getElementById('gm-club').value = 'BOS'; gmClubChange(); }
  gmState.stage = 0; gmShow(); await wait(30);
  o.simScoreboard = /\d{2,3}-\d{2,3}/.test(document.getElementById('gm-score').textContent) && /Payroll/.test(document.getElementById('gm-score').textContent);
  o.simNextCard = !!document.querySelector('#gmbody .gm-next');
  // trees: tabs, the player's main line first, other pieces folded
  switchView('trees'); await wait(300);
  o.treesTabs = document.querySelectorAll('#view-trees .tree-tabs .modechip').length === 3 && document.getElementById('tree-player-panel').hidden && !document.getElementById('treeswrap').hidden;
  document.getElementById('tree-find').value = 'Mookie Betts'; treeFind(); await wait(50);
  o.treesPlayerTab = !document.getElementById('tree-player-panel').hidden && document.getElementById('treeswrap').hidden && document.querySelectorAll('#tree-find-out details.tfold').length >= 1 && [...document.querySelectorAll('#tree-find-out details.tfold')].every(d => !d.open) && /Where the other pieces went/.test(document.getElementById('tree-find-out').textContent);
  vcTrees('BOS'); await wait(50);
  o.treesClubReplacesPlayer = document.getElementById('tree-player-panel').hidden && !document.getElementById('tree-club-panel').hidden && document.querySelectorAll('#treeswrap .tree-card').length >= 1;
  const fb = document.querySelector('#treeswrap .tfold-all'); if(fb) fb.click();
  o.treesOpenAll = !!fb && [...document.querySelector('#treeswrap .tree-card').querySelectorAll('details.tfold')].every(d => d.open);
  // scenario list: no player names while names are hidden
  switchView('scen'); await wait(300);
  o.scenListNoNames = (() => { const ls = [...document.getElementById('sc-sel').options].map(o => o.textContent); return !ls.some(t => /Skubal|De La Cruz|Holmes|Neto/.test(t)); })();
  // Org DNA: leaders, one card per club, the full table folded; the report card carries the profile
  switchView('dna'); await wait(300);
  o.dnaNoClubChips = !document.querySelector('#view-dna .clubchips, #vc-dna');
  o.dnaLeaders = document.querySelectorAll('#dna-leaders .dna-lead').length >= 6 && document.querySelectorAll('#dna-leaders .dna-worst').length >= 6 && /Worst drafters/.test(document.getElementById('dna-leaders').textContent) && /Most IL stints/.test(document.getElementById('dna-leaders').textContent) && (() => { const c = document.querySelector('#dna-leaders .dna-lead'), rk = [...c.querySelectorAll('.hub-row strong')].map(x => +x.textContent); return rk.slice(0, 3).join() === '1,2,3' && rk[3] > rk[4] && rk[4] > rk[5] && rk[3] >= 20; })();
  o.dnaCards = document.querySelectorAll('#dna-cards .dna-card').length === document.querySelectorAll('#dnatable tbody tr').length && document.querySelectorAll('#dna-cards .dna-card').length >= 25;
  o.dnaTableFolded = !document.querySelector('#view-dna details.dna-tablewrap').open;
  document.getElementById('dna-sort').value = 'draft'; renderDnaTab(); await wait(20);
  o.dnaSortDraft = /Guardians|Dodgers|Diamondbacks/.test(document.querySelector('#dna-cards .dna-card .dna-nm').textContent);
  document.getElementById('dna-sort').value = ''; renderDnaTab();
  switchView('report', 'bos'); await wait(300);
  const dp = document.getElementById('dnapanel');
  o.reportDnaBeforeLedgers = !!dp && dp.nextElementSibling === document.getElementById('rc-ledgers') && /Picks signed over slot/i.test(dp.textContent) && /IL stints a season/i.test(dp.textContent) && /Trades, net/.test(dp.textContent);
  // qualifying offers: each further qualified signing costs the next pick(s) down, by club category
  o.qoRules = gmQoPenalty('BOS', 1).picks.join() === '2,5' && gmQoPenalty('BOS', 2).picks.join() === '3,6' && gmQoPenalty('PIT', 1).picks.join() === '3' && gmQoPenalty('PIT', 2).picks.join() === '4' && gmQoPenalty('HOU', 1).picks.join() === '2' && gmQoPenalty('HOU', 2).picks.join() === '3' && gmQoPenalty('BOS', 1).war > gmQoPenalty('PIT', 1).war;
  // simulator: the up-next suggestion steps aside once you pick a player, and a negotiation stays put
  gmState.stage = 2; gmState.open.tab = 'fa'; gmState.open.sel = null; gmState.nextDone2 = false; gmShow(); await wait(30);
  const hadNext = !!document.querySelector('#gmbody .gm-next');
  const fa1 = DESK.players.find(x => gmIsFA(x) && x[2] !== gmState.club && !(gmState.neg || {})[x[1]]);
  gmFaPick(fa1[1]); await wait(30);
  o.simNextStepsAside = hadNext && !document.querySelector('#gmbody .gm-next');
  document.getElementById('gm-ny-' + fa1[1]).value = 2; document.getElementById('gm-nt-' + fa1[1]).value = 1; gmOffer(fa1[1], 0); await wait(30);
  o.simNegotiationStays = gmState.open.sel === fa1[1] && !!document.getElementById('gm-neg-' + fa1[1]) && !/Open negotiations[\s\S]*resume/.test((document.querySelector('#gmbody .card') || {}).textContent || '');
  // sharing: team card, heist links and the heist a shared link points to
  folTeamSet('BOS'); switchView('team'); await wait(50);
  folGoTeam('BOS'); await wait(300);
  o.teamShareButtons = /tc-grade/.test(folTradingCard('BOS'));
  heistState.focus = folHeistId(folHeistOfDay()); switchView('heists'); await wait(50);
  o.heistSharedLink = /Shared with you/.test(document.getElementById('heistbody').textContent) && /Share this heist/.test(document.getElementById('heistbody').textContent);
  heistState.focus = null;
  o.dataParsed = typeof DESK === 'object' && Array.isArray(DESK.players) && Array.isArray(TRADE_BOOK.trades);
  // leaderboard key folds away
  o.lbKeyFolded = document.querySelectorAll('#view-leaderboard .lbkey details').length === 2 && /How to read a row/.test(document.querySelector('#view-leaderboard .lbkey summary').textContent);
  o.sparklines = (() => { bdState.tab = 'fa'; switchView('boards'); return document.querySelectorAll('#boardsbody svg.spark').length > 5; })();
  // Nov 10: prospect bios and stat lines; real prospects in the winter scenarios; the trade block
  const P = n => DESK.players.find(p => p[0] === n);
  o.bioIntl = /International signing, 2022, \$397,500 bonus/.test(gmBio(P('Josue De Paula'))) && /2023, \$525,000 bonus/.test(gmBio(P('Franklin Arias')));
  o.bioDraft = (() => { const d = DESK.players.find(p => (DESK.bio[p[1]] || [])[0] === 'd' && DESK.bio[p[1]][3] === 1); return !!d && /draft, #1 overall, \$[\d.]+M bonus/.test(gmBio(d)); })();
  o.line26 = /^\.\d{3}\/\.\d{3}\/\.\d{3}, \d+ HR/.test(gmLine26(P('Zach Neto'))) && / IP, [\d.]+ ERA/.test(gmLine26(P('Tarik Skubal')));
  const w27 = scWinter27(), trs = w27.filter(s => s.kind === 'trade'), bls = w27.filter(s => s.kind === 'block');
  o.scenRealProspects = trs.length >= 2 && trs.every(s => s.send.length && s.send.every(q => { const p = DESK.players.find(x => x[1] === q.pid); return p && gmIsProsRow(p) && p[2] === s.team; })) && !w27.some(s => /consensus #/.test(s.setup));
  o.scenBlock = bls.length >= 2 && bls.every(s => s.offers.length === 3 && new Set(s.offers.map(q => q.buyer)).size === 3 && Math.max(...['o0', 'o1', 'o2'].map(a => scAdjudicate(s, a).proc)) >= 65 && scAdjudicate(s, 'hold').outw === null);
  o.scenBlockShown = (() => { switchView('scen'); scState.idx = scAll().findIndex(s => s.kind === 'block'); document.getElementById('sc-sel').innerHTML = ''; renderScen(); const t = document.getElementById('scenbody').textContent; const pre = /On the block/.test(t) && /Keep him/.test(t) && !/to you/.test(t); scAct('hold'); return pre && /to you/.test(document.getElementById('scenbody').textContent); })();
  // pick'em: the club, both lines, add a player, the card image
  o.pickemTeam = (() => { const x = pkPool().find(x => !wireActual(x.p[1])); const pid = x.p[1]; try { localStorage.removeItem('fol-pk-' + pid); } catch(e){} pkTeam(pid, 'SEA'); const ok = pkMine(pid).team === 'SEA'; pkLineSet('fair'); pkOU(pid, 'under'); const m = pkMine(pid); pkLineSet('proj'); const ok2 = m.ouf === 'under' && !m.ou; window.FOL_SHARE_KEEP = 1; const el = pkSaveCard(); const ok3 = !!el && /Mariners/.test(el.textContent) && /fair value/.test(el.textContent); if(el) el.remove(); window.FOL_SHARE_KEEP = 0; try { localStorage.removeItem('fol-pk-' + pid); } catch(e){} return ok && ok2 && ok3; })();
  o.pickemAdd = (() => { const base = new Set(pkPool().map(x => x.p[1])); const p = DESK.players.find(p => gmIsFA(p) && !gmIsProsRow(p) && !base.has(p[1]) && gmProj27(p) > 0.8); pkAdd(p[1]); const ok = pkPool().some(x => x.p[1] === p[1] && x.added); pkDrop(p[1]); return ok && !pkPool().some(x => x.p[1] === p[1]); })();
  try { localStorage.removeItem('fol-team'); } catch(e){}
  return o;
});
// Nov 10 (round 2): one name for the offer, reported trade candidates, advanced rates, best seasons,
// the best and worst winters, the Hot Stove pages
import fs from 'fs';
const offsJson = JSON.parse(fs.readFileSync(new URL('../offseasons.json', import.meta.url)));
Object.assign(R, await d.page.evaluate(async (offsJson) => {
  const o = {}, wait = ms => new Promise(z => setTimeout(z, ms));
  const P = n => DESK.players.find(p => p[0] === n);
  bdState.tab = 'fa'; switchView('boards'); await wait(60);
  const faTxt = document.getElementById('view-boards').innerText;
  switchView('pickem'); await wait(60);
  const pkTxt = document.getElementById('view-pickem').innerText;
  o.oneNameLedgerOffer = /Ledger offer/i.test(faTxt) && /Fair value/i.test(faTxt) && /Ledger offer/.test(pkTxt) && !/Ledger projection|Projected contract|Fair Ledger offer|Ledger's number/i.test(faTxt + pkTxt + document.getElementById('homebody').innerText);
  const L = dkAvailList();
  o.blockReported = L.filter(x => x.rep).length >= 30 && L.some(x => x.p[0] === 'Trea Turner' && x.rep && /Nightengale/.test(dkRumorSrc(x.rep))) && !L.some(x => /Acu.a/.test(x.p[0])) && L.length >= 80;
  dkState.mode = 'avail'; dkState.av = {pos: '', club: '', read: 'Reported', sort: 'read'}; switchView('desk'); await wait(60);
  o.blockReportedShown = /Reported/.test(document.getElementById('deskbody').textContent) && /MLB Trade Rumors trade candidates, #1/.test(document.getElementById('deskbody').textContent);
  dkState.av.read = ''; dkState.mode = 'trade';
  o.advRates = /xFIP, [\d.]+ SIERA/.test(gmLine26(P('Tarik Skubal'))) && /\.\d{3} xwOBA/.test(gmLine26(P('Zach Neto')));
  o.dudeBestLine = dudeOf(['x', 'N', 1990, 2000, 0, 10, 3000, 'NYY', 1995, 4, 9.5, '.300/.400/.500, 30 HR, 100 RBI']).bl === '.300/.400/.500, 30 HR, 100 RBI';
  offsLoadData(offsJson); offState.dir = 'best'; offState.club = ''; offState.focus = ''; switchView('offs'); await wait(60);
  const cards = [...document.querySelectorAll('#offsbody .offs-card')];
  o.offsExplorer = cards.length === 15 && /2011-12 Oakland Athletics/.test(cards[0].textContent) && /All-timer/i.test(cards[0].textContent) && cards[0].querySelectorAll('.of-mv a').length >= 3;
  offState.dir = 'worst'; renderOffs();
  o.offsWorst = /2012-13 Toronto Blue Jays/.test(document.querySelector('#offsbody .offs-card').textContent);
  offState.dir = 'best'; offState.club = 'NYM'; renderOffs();
  o.offsClub = [...document.querySelectorAll('#offsbody .offs-card')].every(c => /Mets/.test(c.textContent));
  offState.club = '';
  o.offsSimRank = /would rank <strong>#\d+ of \d+<\/strong>/.test(gmOffsCard(6.5, 4)) && gmOffsCard(0, 0) === '';
  o.offsRoute = (() => { switchView('offs'); return /view=winters/.test(location.hash); })();
  // Hot Stove: the hub and one club
  wireLoadData([], null); stoveGo(''); await wait(60);
  o.stoveHub = document.querySelectorAll('#stovebody .st-club').length === 30;
  stoveGo('ATL'); await wait(60);
  const sv = document.getElementById('stovebody').textContent;
  o.stoveClub = /Atlanta Braves/.test(sv) && /Gained/.test(sv) && /Lost/.test(sv) && /still unsigned/.test(sv) && /On the trade block/.test(sv) && /What the roster still needs/.test(sv) && /view=stove&id=atl/.test(location.hash) && /Braves: the 2026-27 winter/.test(document.title);
  switchView('home'); await wait(60);
  o.stoveTitleReset = !/winter so far/.test(document.title) && !!document.getElementById('hub-offs');
  // Play is one stacked card on the right of the home page: six rows, no tile grid
  o.playStacked = document.querySelectorAll('#homebody .hub-right .hub-play .hp-row').length === 6 && !document.querySelector('#homebody .hp-tiles');
  // the morning line: three boxes, each a kicker, one line and one note; the club picker opens the winter page
  o.morningLine = document.querySelectorAll('#hub-line .ml-box').length === 3 && [...document.querySelectorAll('#hub-line .ml-box')].every(b => b.querySelectorAll('.home-kick').length === 1 && b.querySelectorAll('strong').length === 1 && b.querySelectorAll('.ttype').length === 1) && /Today's games/.test(document.getElementById('hub-line').textContent);
  o.clubPickerToStove = (() => { const sel = document.getElementById('hub-team'); sel.value = 'SEA'; sel.onchange(); const ok = routeView() === 'stove' && stoveState.club === 'SEA'; switchView('home'); return ok; })();
  // share links: a page with its own preview where one is built, the # link otherwise
  shareLoadData({w: ['123'], s: 1, o: ['2011-ath']});
  o.shareLinks = wireUrl({id: '123'}) === 'https://frontofficeledger.com/w/123' && /#view=wire&id=999/.test(wireUrl({id: '999'})) && stoveUrl('NYM') === 'https://frontofficeledger.com/s/nym' && offsUrl('2011-ath') === 'https://frontofficeledger.com/o/2011-ath' && /#view=winters/.test(offsUrl('2001-nym'));
  shareLoadData({});
  // trade pick'em: two dozen reported candidates, a call sticks, a Wire trade scores it, the calls card counts it
  try { Object.keys(localStorage).filter(k => /^fol-tp-/.test(k)).forEach(k => localStorage.removeItem(k)); } catch(e){}
  WIRE.items = []; switchView('pickem'); await wait(80);
  const tpc = () => document.querySelector('#view-pickem .wire-tp');
  const pool = tpPool();
  o.tpCardShown = !!tpc() && pool.length >= 20 && pool.length <= 24 && pool.every(x => !x.r.long) && tpc().querySelectorAll('.wq-row').length === pool.length && /Traded this winter/.test(tpc().textContent);
  const a = pool[0].p, b = pool[1].p;
  tpCall(a[1], 'y'); tpCall(b[1], 'n'); await wait(120);
  o.tpCallSticks = tpMine(a[1]).call === 'y' && tpMine(b[1]).call === 'n' && /Your call: traded/.test(tpc().textContent) && /Your call: stays/.test(tpc().textContent) && !!tpc().querySelector('select[aria-label^="Where"]');
  tpCall(a[1], 'n'); o.tpNoSecondCall = tpMine(a[1]).call === 'y';
  const dest = Object.keys(DESK.teams).find(ab => ab !== a[2]);
  tpTeam(a[1], dest); await wait(60);
  WIRE.items = [{id: 'tp-test', kind: 'trade', d: '2026-11-12', who: [{pid: a[1], name: a[0], from: a[2], to: dest}]}]; pkRedraw(); await wait(80);
  o.tpScored = tpMoved(a[1]).to === dest && /You called the club too/.test(tpc().textContent) && /Trades\s*1 for 1/.test(document.querySelector('#view-pickem').textContent);
  WIRE.items = []; try { Object.keys(localStorage).filter(k => /^fol-tp-/.test(k)).forEach(k => localStorage.removeItem(k)); } catch(e){}
  // price and best fits fold open on a candidate; the offer opens at the Deal Desk
  WIRE.items = []; pkRedraw(); await wait(60);
  const fitP = pool.map(x => x.p).find(p => tpFits(p).offers.length >= 2);
  tpToggle(fitP[1]); await wait(60);
  o.tpFitsOpen = !!tpc().querySelector('.tp-fits') && /The Ledger's price/.test(tpc().querySelector('.tp-fits').textContent) && tpc().querySelectorAll('.tp-fit').length === tpFits(fitP).offers.length;
  tpBuild(fitP[1], tpFits(fitP).offers[0].buyer); await wait(80);
  o.tpFitsToDesk = routeView() === 'desk' && dkState.mode === 'trade' && dkState.you === fitP[2] && dkState.send.length === 1 && dkState.send[0].p[1] === fitP[1] && dkState.recv.length >= 1;
  document.querySelectorAll('.fol-pop, .dk-pop, .modal.on').forEach(e => e.remove()); try { dkPopClose(); } catch(e){}
  dkState.send = []; dkState.recv = []; dkState.mode = 'trade'; tpToggle(fitP[1]);
  // one streak for the three daily games, and one card to copy
  const dday = Math.floor(Date.now() / 864e5), lsKeep = {};
  ['fol-quiz-day-' + dday, 'fol-quiz-day-' + (dday - 1), 'fol-dudes-d2-' + dday, 'fol-dudes-d2-' + (dday - 1), 'fol-dudes-d2-' + (dday - 2), 'fol-daily-sc-' + dday].forEach(k => { lsKeep[k] = localStorage.getItem(k); localStorage.removeItem(k); });
  o.dailyZero = folDailyDays() === 0 && folQuizDays() === 0 && dudesDays() === 0;
  dudesStore('d2-' + (dday - 2), [true, false]); folQuizStore('day-' + (dday - 1), [true, true, false, true, true]);
  o.dailyCarries = folDailyDays() === 2;      // yesterday and the day before, by two different games; today not played yet
  const dly = folDailyScen(); scState.idx = dly.k; switchView('scen'); await wait(80);
  const ds = scAll()[dly.k]; scAct(ds.kind === 'block' ? 'hold' : ds.type === 'trade' || !ds.type ? 'reject' : 'pass'); await wait(60);
  o.dailyScenCounts = !!folDailyGet(dday).s && folDailyDays() === 3 && /Scenario of the day: process \d+\/100/.test(folDailyText()) && /3 days in a row/.test(folDailyText());
  switchView('home'); await wait(120);
  o.dailyFoot = /1 of 3 daily games played/.test(document.querySelector('.hub-play .hp-foot').textContent) && /3 days in a row/.test(document.querySelector('.hub-play .hp-foot').textContent) && document.querySelectorAll('#homebody .hub-right .hub-play .hp-row').length === 6
    && /2 games still to play/.test(document.getElementById('hub-line').textContent);
  Object.entries(lsKeep).forEach(([k, v]) => { if(v == null) localStorage.removeItem(k); else localStorage.setItem(k, v); }); delete scState.played[ds.id];
  // tale of the tape: two front offices, a tally that adds up, a link that restores the pair
  switchView('h2h'); await wait(80);
  const bt = () => document.getElementById('bt-card'), reg = btAll();
  const rws = btRows(reg.find(r => r.id === btState.a), reg.find(r => r.id === btState.b)), tl = btTally(rws);
  o.battleCard = !!bt() && bt().querySelectorAll('.bt-row').length === rws.length + 3 && tl.a + tl.b <= tl.n && rws[0].k === 'overall' && bt().querySelectorAll('.bt-win').length === rws.filter(r => r.w).length && btState.a !== btState.b;
  btPick('a', btState.b); await wait(40);
  o.battleNoSelf = btState.a !== btState.b && /vs=/.test(location.hash);
  const two = reg.slice(-2).map(r => r.id); routeApply('#view=h2h&vs=' + two.join('~')); await wait(80);
  o.battleRoute = btState.a === two[0] && btState.b === two[1] && bt().textContent.includes(reg.find(r => r.id === two[0]).exec);
  btState.set = false;
  // club by club: every tile carries the same three lines
  WIRE.items = []; stoveGo(''); await wait(80);
  const tiles = [...document.querySelectorAll('#stovebody .st-club')];
  o.clubTilesEven = tiles.length === 30 && tiles.every(t => t.querySelectorAll('.wr-best').length === 1 && t.querySelectorAll('.st-last').length === 1) && new Set(tiles.map(t => Math.round(t.getBoundingClientRect().height))).size === 1;
  // trade reports come from rumors.json; a bad file leaves the built-in list alone
  const keep = JSON.parse(JSON.stringify(TRADE_RUMORS)), keepOff = TRADE_OFF, n0 = TRADE_RUMORS.rows.length;
  rumorsLoadData(null); rumorsLoadData({rows: []}); rumorsLoadData({rows: 'x'});
  o.rumorsBadFileIgnored = TRADE_RUMORS.rows.length === n0 && !!TRADE_OFF[660670];
  const tt = DESK.players.find(p => p[0] === 'Trea Turner');
  rumorsLoadData({asof: 'Dec 1', rows: [[tt[1], 1, 'A Reporter', 'test reason'], ['junk'], [0, 1, '', '']], off: {}});
  o.rumorsFileApplied = TRADE_RUMORS.rows.length === 1 && TRADE_RUMORS.asof === 'Dec 1' && dkRumor(tt[1]).why === 'test reason' && !dkRumor(pool[0].p[1]) && !TRADE_OFF[660670] && tpPool().length === 1;
  TRADE_RUMORS.rows = keep.rows; TRADE_RUMORS.asof = keep.asof; TRADE_OFF = keepOff; dkRumor._m = null; dkAvailList._c = null;
  o.rumorsRestored = tpPool().length === pool.length;
  WIRE.items = null;
  return o;
}, offsJson));
await d.browser.close();
// phones: the bottom bar and no sideways scroll on the new views
const m = await open({width: 390, height: 844});
Object.assign(R, await m.page.evaluate(async () => {
  const o = {}, wait = ms => new Promise(z => setTimeout(z, ms));
  const over = () => document.documentElement.scrollWidth - document.documentElement.clientWidth;
  o.phoneBottomBar = getComputedStyle(document.getElementById('mobar')).display === 'flex';
  const wide = [];
  folTeamSet('NYY');
  for(const v of ['home', 'heists', 'quiz', 'desk', 'gm']){ switchView(v); await wait(250); if(over() > 2) wide.push(v + ':' + over()); }
  dkEval(); await wait(30); if(over() > 2) wide.push('popup:' + over());
  // phones: Play sits right after the Wire on home, ahead of the free agent and winter tiles
  switchView('home'); await wait(250);
  const top = q => { const e = document.querySelector(q); return e ? e.getBoundingClientRect().top + scrollY : -1; };
  o.phonePlayAfterWire = top('#hub-wire') < top('.hub-play') && top('.hub-play') < top('.hub-pair') && top('.hub-pair') < top('#hub-winter');
  // phones: the tale of the tape fits without sideways scroll
  switchView('h2h'); await wait(250); if(over() > 2) wide.push('h2h:' + over());
  switchView('pickem'); await wait(250); if(over() > 2) wide.push('pickem:' + over());
  stoveGo(''); await wait(250); if(over() > 2) wide.push('clubs:' + over());
  o.phoneNewViewsFit = wide.length === 0; if(wide.length) o.phoneWide = wide.join(' ');
  try { localStorage.removeItem('fol-team'); } catch(e){}
  return o;
}));
await m.browser.close();
report('t_fun', R, [...d.errors, ...m.errors]);
