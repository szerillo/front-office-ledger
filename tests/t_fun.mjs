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
  o.pickerHas30 = document.querySelectorAll('#homebody .tchip').length === 30;
  o.heistOfDay = !!document.querySelector('#homebody .heist') || /Heist of the day/.test(document.getElementById('homebody').textContent);
  o.hubTeasers = ['Who won', 'Best front offices', 'Offseason simulator', 'Scenario room'].every(x => document.getElementById('homebody').textContent.includes(x));
  o.hubOrder = (() => { const ks = [...document.querySelectorAll('#homebody .hub-grid .home-kick')].map(k => k.textContent.trim().toLowerCase()); return ks[0] === 'heist of the day' && ks[1] === 'leaderboard' && ks[2] === 'daily game' && ks[3] === 'offseason simulator' && ks[4] === 'scenario room' && ks.length >= 10; })();
  o.hubSections = document.querySelectorAll('#homebody .hub-sec').length === 3 && /Signing of the day/.test(document.getElementById('homebody').textContent) && /Draft steal of the day/.test(document.getElementById('homebody').textContent);
  document.getElementById('hub-find').value = 'Friedman'; folHubFind();
  o.hubSearch = /Andrew Friedman/.test(document.getElementById('hub-find-out').textContent) && /report card/.test(document.getElementById('hub-find-out').textContent);
  document.getElementById('hub-find').value = 'Mookie'; folHubFind();
  o.hubSearchPlayer = /Mookie Betts/.test(document.getElementById('hub-find-out').textContent);
  document.getElementById('hub-find-out').innerHTML = '';
  o.hubNoDemeaning = !/Is your GM any good/i.test(document.getElementById('homebody').textContent);
  folPickTeam('BOS'); await wait(50);
  const hb = document.getElementById('teambody').textContent;
  o.teamPage = !document.getElementById('view-team').hidden && !!document.querySelector('#teambody .team-band') && /Craig Breslow/.test(hb);
  o.teamNoListTabs = ![...document.querySelectorAll('#teambody button')].some(b => /^(Prospects|Free agents)$/.test(b.textContent.trim()));
  o.teamReportFirst = /Full report card/.test(document.querySelector('#teambody .actions button').textContent);
  o.teamRemembered = folTeam() === 'BOS';
  o.teamBestWorst = /Best move/.test(hb) && /Worst move/.test(hb);
  o.teamTimelinePins = document.querySelectorAll('#teambody svg circle').length >= 3;
  o.navOrder = [...document.querySelectorAll('nav [data-view]')].map(b => b.dataset.view).slice(0, 8).join() === 'home,leaderboard,report,champs,dna,h2h,heists,trees' || [...document.querySelectorAll('nav [data-view]')].map(b => b.dataset.view).join();
  o.navQuizUnderPlayGM = (() => { const g = [...document.querySelectorAll('nav [data-view]')].map(b => b.dataset.view); return g.slice(-4).join() === 'gm,desk,scen,quiz'; })();
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
  folTeamDefaults._done = {}; switchView('desk'); await wait(400);
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
  switchView('dna'); await wait(300); DNA_CLUB = ''; renderDnaTab(); await wait(30);
  o.dnaLeaders = document.querySelectorAll('#dna-leaders .dna-lead').length === 6;
  o.dnaCards = document.querySelectorAll('#dna-cards .dna-card').length === document.querySelectorAll('#dnatable tbody tr').length && document.querySelectorAll('#dna-cards .dna-card').length >= 25;
  o.dnaTableFolded = !document.querySelector('#view-dna details.dna-tablewrap').open;
  document.getElementById('dna-sort').value = 'draft'; renderDnaTab(); await wait(20);
  o.dnaSortDraft = /Guardians|Dodgers|Diamondbacks/.test(document.querySelector('#dna-cards .dna-card .dna-nm').textContent);
  document.getElementById('dna-sort').value = ''; renderDnaTab();
  switchView('report', 'bos'); await wait(300);
  const dp = document.getElementById('dnapanel');
  o.reportDnaBeforeLedgers = !!dp && dp.nextElementSibling === document.getElementById('rc-ledgers') && /Picks signed over slot/i.test(dp.textContent) && /IL stints a season/i.test(dp.textContent) && /Trades, net/.test(dp.textContent);
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
