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
  o.hubTeasers = ['Trade Grade', 'Best front offices', 'Run a winter', 'Scenario of the day', 'Signing of the day', 'GM rivalry of the day', 'Will they take the QO?'].every(x => document.getElementById('homebody').textContent.includes(x));
  o.hubOrder = (() => { const ks = [...document.querySelectorAll('#homebody .hub-grid > .card > .home-kick, #homebody .hub-links .home-kick')].map(k => k.textContent.trim().toLowerCase()); const once = new Set(ks.map(k => k.split(' · ')[0])).size === ks.length; return ks.includes('leaderboard') && ks.some(k => /^trade of the day · (on this date|this week in history)$/.test(k)) && ks.some(k => k.startsWith('signing of the day')) && ks.length >= 10 && once; })();
  o.rankByRate = folActiveRank().every((r, i, a) => i === 0 || a[i - 1].gradeRate >= r.gradeRate) && /Best at/.test(document.querySelector('#homebody .hub-lb').textContent) && /a season/.test(document.querySelector('#homebody .hub-lb').textContent);
  o.hubPlayRail = [...document.querySelectorAll('#homebody .hub-play .hp-row')].length >= 4 && !!document.querySelector('#homebody .hub-top #hub-wire');
  o.hubSections = [...document.querySelectorAll('#homebody .hub-sec h3')].map(h => h.textContent).join('|') === 'From the archive|The rankings and this winter' && /champion line/.test(document.getElementById('homebody').textContent) && /Org stat of the day/.test(document.getElementById('homebody').textContent) && /Ledger/.test(document.querySelector('#homebody .hub-fa2').textContent) && /Projected/.test(document.querySelector('#homebody .hub-fa2').textContent) && /front offices/.test(document.querySelector('#homebody .hub-stats').textContent) && /free-agent signings/.test(document.getElementById('homebody').textContent);
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
  o.teamStanding = !!document.querySelector('#rc-standing .rc-standing') && /active front offices/.test(document.getElementById('rc-standing').textContent) && /Run the Red Sox winter/.test(document.getElementById('rc-standing').textContent);
  o.teamNotRemembered = folTeam() === '' && (() => { try { return !localStorage.getItem('fol-team'); } catch(e){ return true; } })();
  [...document.querySelectorAll('#rc-standing button')].find(b => /Run the Red Sox winter/.test(b.textContent)).click(); await wait(300);
  o.teamRunWinterOpensClub = !document.getElementById('view-gm').hidden && gmState.club === 'BOS';
  dkState.you = null; switchView('desk'); await wait(100);
  o.noDefaultClubAfter = !dkState.you;
  o.teamTimelinePins = document.querySelectorAll('#view-report svg circle').length >= 3;
  o.teamStandingOnlyCurrent = (() => { const h = LB_HIST.find(x => x.realCard); if(!h) return true; switchView('report', h.id); return !(document.getElementById('rc-standing') || {}).textContent; })();
  o.navOrder = [...document.querySelectorAll('nav [data-view]')].map(b => b.dataset.view).slice(0, 9).join() === 'home,wire,leaderboard,report,champs,dna,h2h,heists,trees' || [...document.querySelectorAll('nav [data-view]')].map(b => b.dataset.view).join();
  o.navQuizUnderPlayGM = (() => { const g = [...document.querySelectorAll('nav [data-view]')].map(b => b.dataset.view); return g.slice(-5).join() === 'gm,desk,scen,quiz,dudes'; })();
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
  o.dnaLeaders = document.querySelectorAll('#dna-leaders .dna-lead').length === 6;
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
  o.teamShareButtons = /Save card image/.test(document.getElementById('rc-standing').textContent) && /tc-grade/.test(folTradingCard('BOS'));
  heistState.focus = folHeistId(folHeistOfDay()); switchView('heists'); await wait(50);
  o.heistSharedLink = /Shared with you/.test(document.getElementById('heistbody').textContent) && /Share this heist/.test(document.getElementById('heistbody').textContent);
  heistState.focus = null;
  o.dataParsed = typeof DESK === 'object' && Array.isArray(DESK.players) && Array.isArray(TRADE_BOOK.trades);
  // leaderboard key folds away
  o.lbKeyFolded = document.querySelectorAll('#view-leaderboard .lbkey details').length === 2 && /How to read a row/.test(document.querySelector('#view-leaderboard .lbkey summary').textContent);
  o.sparklines = (() => { bdState.tab = 'fa'; switchView('boards'); return document.querySelectorAll('#boardsbody svg.spark').length > 5; })();
  try { localStorage.removeItem('fol-team'); } catch(e){}
  return o;
});
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
  o.phoneNewViewsFit = wide.length === 0; if(wide.length) o.phoneWide = wide.join(' ');
  try { localStorage.removeItem('fol-team'); } catch(e){}
  return o;
}));
await m.browser.close();
report('t_fun', R, [...d.errors, ...m.errors]);
