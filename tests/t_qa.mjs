// Launch-day QA regressions (Nov 10 2026): every check is a case from the outside walk-through of the
// Deal Desk, the Assistant GM and the copy. Star contracts are not dead weight, "Make it fair" respects
// where a club stands, and the site agrees with itself on one deal.
import { open, report } from './_common.mjs';
const { browser, page, errors } = await open();
import fs from 'fs';
const offsJson = JSON.parse(fs.readFileSync(new URL('../offseasons.json', import.meta.url), 'utf8'));
const R = await page.evaluate(async (offsJson) => {
  const o = {}, wait = ms => new Promise(z => setTimeout(z, ms)), P = n => DESK.players.find(x => x[0] === n);
  const pc = n => { const p = P(n); return {kind: 'player', p, ctrl: gmIsProsRow(p) ? 6 : gmCtrlOf(p)}; };
  switchView('desk'); dkState.mode = 'trade'; await wait(80);
  const set = (you, them, ask, offer) => { dkState.you = you; dkState.them = them; dkState.recv = ask.map(pc); dkState.send = offer.map(pc); renderDesk(); };
  const note = () => (document.getElementById('dk-agm-note') || {textContent: ''}).textContent.replace(/^Assistant GM/, '').trim();
  const oht = P('Shohei Ohtani'), soto = P('Juan Soto'), judge = P('Aaron Judge');
  // B1: a star contract is not dead weight
  o.ohtaniPresentValue = gmSurplusRaw(oht) > -5 && gmSurplus(oht) >= gmProj27(oht) - 0.01;
  o.starsNeverLiabilities = [oht, soto, judge].every(p => gmSurplus(p) >= 0);
  set('SF', 'LAD', ['Shohei Ohtani'], ['Jerar Encarnacion']);
  o.ohtaniNotForNothing = dkCounterpartyCheck().ok === false && !/would take it/.test(dkCounterpartyCheck().txt);
  set('BOS', 'NYM', ['Juan Soto'], ['Connor Wong']);
  o.sotoNotForNothing = dkCounterpartyCheck().ok === false;
  set('BOS', 'NYY', ['Aaron Judge'], ['Connor Wong']);
  o.judgeNotForNothing = dkCounterpartyCheck().ok === false;
  o.realDumpsStillCount = gmSurplus(P('Xander Bogaerts')) < -3;
  // B2: a rebuilding club sells; it is never handed a rental for a controlled regular
  const rebuild = Object.keys(DESK.teams).filter(ab => folPosture(ab).key === 'rebuilding'), contend = Object.keys(DESK.teams).filter(ab => folPosture(ab).key === 'contender');
  let sells = 0, bad = [];
  for(const you of rebuild.slice(0, 5)){
    set(you, contend[0], [], []); dkAgm(); await wait(20);
    const out = dkState.send.filter(x => !gmIsProsRow(x.p)), inn = dkState.recv;
    if(out.length && out.every(x => x.ctrl <= 2 || x.p[4] + 1 >= 30)) sells++;
    if(inn.some(x => !gmIsProsRow(x.p) && !(gmCtrlOf(x.p) >= 3 && x.p[4] + 1 <= 28))) bad.push(you + ':' + inn.map(x => x.p[0]).join('+'));
    if(!note()) bad.push(you + ':blank');
  }
  o.rebuilderStartsFromASale = rebuild.length >= 2 && sells >= Math.min(rebuild.length, 5) - 1 && bad.length === 0; if(bad.length) o.rebuilderBad = bad.join(' ');
  // the note and the verdict use one test
  const pairs = [['NYY', 'LAA', ['Zach Neto']], ['LAD', 'MIL', []], ['MIL', 'COL', []], ['NYY', 'HOU', ['Jeremy Peña']], ['SEA', 'STL', []], ['PHI', 'LAA', ['Zach Neto']], ['ATL', 'WSH', []], ['TOR', 'MIN', []]];
  const mism = [];
  for(const [you, them, ask] of pairs){
    set(you, them, ask, []); dkAgm(); await wait(20);
    const n = note(), built = dkState.recv.length && dkState.send.length, ok = built ? dkCounterpartyCheck().ok : false;
    if(!n) mism.push(you + '-' + them + ':blank');
    if(/Done:|Fair as built/.test(n) && !ok) mism.push(you + '-' + them + ':done-but-no');
    if(/Still short|have not built/.test(n) && ok) mism.push(you + '-' + them + ':short-but-yes');
  }
  o.doneMeansTheyAccept = mism.length === 0; if(mism.length) o.doneMismatch = mism.join(' ');
  // a dump is not balanced by attaching a star
  set('SD', 'COL', ['Jimmy Herget'], ['Xander Bogaerts']); dkAgm(); await wait(20);
  o.dumpAddsNobody = dkState.send.length === 1 && /cash/.test(note()) && !/Tatis/.test(note());
  set('SD', 'COL', [], ['Xander Bogaerts']); dkAgm(); await wait(20);
  o.dumpAloneExplained = /cash/.test(note()) && !/cheaper target/.test(note()) && dkState.recv.length === 0;
  // paying a star for a bench bat: the assistant asks for more instead of printing nothing
  set('KC', 'LAD', ['Alex Call'], ['Bobby Witt Jr.']); dkAgm(); await wait(20);
  o.overpayNeverBlank = note().length > 30 && (dkState.recv.length > 1 || /over their price/.test(note()));
  // the assistant never pays with a cornerstone or a four-win player on its own
  let paidStar = [];
  for(const [you, them, ask] of pairs){ set(you, them, ask, []); dkAgm(); await wait(10); dkState.send.forEach(x => { if(!gmIsProsRow(x.p) && (gmFranchise(x.p) || gmProj27(x.p) >= 4)) paidStar.push(x.p[0]); }); }
  o.neverPaysWithAStar = paidStar.length === 0; if(paidStar.length) o.paidStar = paidStar.join(', ');
  // cornerstones are off the table on every kind of club unless they are in trade reports
  o.cornerstonesStay = ['Paul Skenes', 'Bobby Witt Jr.', 'Nick Kurtz'].every(n => { const p = P(n); return dkRumor(p[1]) || !isFinite(gmAskCore(p, p[2])); });
  // one posture function behind every label
  o.onePosture = Object.keys(DESK.teams).every(ab => { const k = folPosture(ab).key; return gmClubPosture(ab) === (k === 'contender' ? 'contender' : k === 'rebuilding' ? 'rebuilding' : 'middle') && dkPosture(ab) === (k === 'contender' ? 'c' : k === 'rebuilding' ? 'r' : 'm'); }) && /wins last year, \d+ projected/.test(folPosture('SD').why);
  dkState.send = []; dkState.recv = [];
  // B3: the site's own offer is not an F by its own grade, and the grade follows the board's fair value
  const fas = DESK.players.filter(x => gmIsFA(x) && !gmIsProsRow(x)).sort((a, b) => gmProj27(b) - gmProj27(a)).slice(0, 20);
  const gradeAt = (p, yrs, tot) => { const d = document.createElement('div'); d.innerHTML = dkFaVerdict({p, yrs, tot, club: p[2], done: 'test'}); return {g: (d.querySelector('.dk-grade .grade') || {}).textContent, t: d.textContent}; };
  const sk = P('Tarik Skubal'), sgS = dkSuggest(sk, 'fa', null), vS = gradeAt(sk, sgS.sugYrs, sgS.sugTot);
  o.skubalOfferNotAnF = !/^[DF]/.test(vS.g) && new RegExp('fair value for these ' + sgS.sugYrs + ' years: \\$' + sgS.fairSame + 'M').test(vS.t);
  o.gradeFollowsFairValue = fas.every(p => { const sg = dkSuggest(p, 'fa', null), f = dkFaFair(p, sg.sugYrs); if(Math.abs(Math.round(f.fair) - sg.fairSame) > 1) return false;
    const g = gradeAt(p, sg.sugYrs, sg.sugTot).g, gap = (sg.fairSame - sg.sugTot) / Math.max(sg.sugTot, 1); return gap > 0.1 ? !/^[DF]/.test(g) : gap < -0.25 ? !/^[AB]/.test(g) : true; });
  o.oneWarTotalPerScreen = !/projected WAR/.test(dkSuggestHtml(sk, 'fa', null)) && !/projected WAR/.test(dkSuggestHtml(P('Paul Skenes'), 'ext', 'pre-debut'));
  o.wireGradesTheSameWay = (() => { const w = wireFa(sk, sgS.sugYrs, sgS.sugTot, sk[2], 1); return w.g === vS.g; })();
  // batch 1: relievers, opening asks, deadlines, stamps, labels
  o.relieverYearsCapped = DESK.players.filter(x => gmIsFA(x) && x[13] === 'RP' && !(DESK.posted || {})[x[1]]).every(x => dkSuggest(x, 'fa', null).sugYrs <= 4);
  gmState.club = 'LAD';
  o.campOpensAboveOurNumber = fas.every(p => { const a = gmAsk(p, true), sg = dkSuggest(p, 'fa', null); return a.tot > sg.sugTot || (a.yrs > sg.sugYrs); });
  const cd = document.createElement('div'); cd.innerHTML = wireCountdown(); const when = [...cd.querySelectorAll('.wd-when')].map(e => e.textContent);
  o.sameDateSameCount = Date.now() > Date.parse('2026-11-17T21:00:00Z') || when.length < 2 || when[0] === when[1];
  const lad = [...REGIMES, ...AUTO_REGIMES].find(r => abOf(r) === 'LAD'), txt = JSON.stringify(lad);
  o.nominalTerms = /Ohtani · 10 yr \/ \$700M \(CBT value \$460\.8M\)/.test(txt) && !/Ohtani · 10 yr \/ \$460\.8M/.test(txt) && /Betts · 12 yr \/ \$365M \(CBT value \$306\.7M\)/.test(txt);
  heistState.kind = 'signings'; heistState.club = ''; heistState.era = 'all'; switchView('heists'); renderHeists(); await wait(120);
  const cards = [...document.querySelectorAll('#view-heists .heist')].slice(0, 20);
  o.signingStampRoundsOnce = cards.length >= 10 && cards.every(c => { const st = (c.querySelector('.stamp') || {}).textContent || '', nt = (c.querySelector('.sg-net b') || {}).textContent || ''; const a = (st.match(/[+\-−][\d.]+/) || [''])[0].replace('−', '-'), b = (nt.match(/[+\-−][\d.]+/) || [''])[0].replace('−', '-'); return !nt || a === b; });
  o.disasterMeansLittleBack = folSignings().every(({x}) => { const n = folSigningNums(x); return folSignStamp(x) !== 'Disaster' || !n || n.prod < n.typical / 3; });
  heistState.kind = 'trades'; routeApply('#view=heists&id=nyy'); await wait(60); routeApply('#view=heists'); await wait(60);
  o.heistsRouteClearsClub = heistState.club === '';
  o.heistWording = !/produced for the club that got him/.test(document.getElementById('view-heists').textContent) && !/buying at the deadline/.test(document.getElementById('view-heists').textContent);
  // the home feed leads with trades and signings; a waiver claim shows a value, not a letter
  const team = ab => ({id: 1, name: CLUB_NAME[ab]});
  const star = DESK.players.find(x => x[2] === 'TB' && !gmIsFA(x) && !gmIsProsRow(x) && gmSurplus(x) > 2), pros = DESK.players.filter(x => gmIsProsRow(x) && x[2] === 'NYY').sort((a, b) => gmPV(b) - gmPV(a))[0], dep = DESK.players.find(x => x[2] === 'MIA' && !gmIsFA(x) && !gmIsProsRow(x) && gmProj27(x) < 1);
  wireLoadData([
    {id: 990011, date: '2026-11-08', typeCode: 'TR', typeDesc: 'Trade', person: {id: star[1], fullName: star[0]}, fromTeam: team('TB'), toTeam: team('NYY'), description: `Tampa Bay Rays traded ${star[0]} to New York Yankees for ${pros[0]}.`},
    {id: 990012, date: '2026-11-08', typeCode: 'TR', typeDesc: 'Trade', person: {id: pros[1], fullName: pros[0]}, fromTeam: team('NYY'), toTeam: team('TB'), description: `Tampa Bay Rays traded ${star[0]} to New York Yankees for ${pros[0]}.`},
    {id: 990013, date: '2026-11-09', typeCode: 'CLW', typeDesc: 'Claimed Off Waivers', person: {id: dep[1], fullName: dep[0]}, fromTeam: team('MIA'), toTeam: team('BOS'), description: `Boston Red Sox claimed ${dep[0]} off waivers from Miami Marlins.`}], {terms: {}, qo: {}, extra: []});
  switchView('home'); wireHomeFill(); await wait(150);
  const rows = [...document.querySelectorAll('#hub-wire .hw-row')];
  o.homeFeedLeadsWithTrades = rows.length >= 2 && /traded|get|for/.test(rows[0].textContent) && rows[0].querySelectorAll('.grade').length >= 1 && rows.some(r => /claim/.test(r.textContent)) && rows.filter(r => /claim/.test(r.textContent)).every(r => !r.querySelector('.grade'));
  WIRE.items = null;
  // the later list: big trades named for their best-known players, wins on every winter card, one per-season number
  const mega = folTrades().find(t => t.d === '2012-11-19' && t.S.some(x => x.ab === 'TOR') && t.S.some(x => x.ab === 'MIA'));
  const megaHead = (() => { const d = document.createElement('div'); d.innerHTML = folHeistCard(mega, {}); return d.querySelector('.h-head').textContent; })();
  o.bigTradeNamedForItsStars = /Buehrle and \d+ others/.test(megaHead) && /others from the/.test(megaHead) && !/^Marlins got Jake Marisnick from/.test(megaHead);
  o.smallTradeTitleUnchanged = (() => { const t = folTrades().find(x => x.S.length === 2 && x.S.reduce((a, q) => a + q.got.length, 0) === 2 && x.win.got.length === 1); const d = document.createElement('div'); d.innerHTML = folHeistCard(t, {}); return !/others/.test(d.querySelector('.h-head').textContent); })();
  const wrows = offsLoadData(offsJson);
  o.everyWinterHasWins = wrows.filter(r => r.w <= 2025).every(r => r.prevW != null && r.nextW != null) && (() => { const r = wrows.find(x => x.ab === 'ARI' && x.w === 1998); return r.prevW === 65 && r.nextW === 100; })();
  o.megaTradeMoveLine = wrows.find(x => x.ab === 'TOR' && x.w === 2012).moves.some(m => /Got Mark Buehrle and 4 others for/.test(m[2]));
  o.troutExtensionMonth = DESK.book.some(c => c[0] === 'Mike Trout' && /^2019-03/.test(c[15] || '')) && !/2019-01-15","Extended Mike Trout/.test(JSON.stringify([...REGIMES, ...AUTO_REGIMES, ...LB_HIST]));
  const cle = [...REGIMES, ...AUTO_REGIMES].find(r => abOf(r) === 'CLE');
  folGoTeam('CLE'); await wait(200);
  const tp = document.getElementById('view-report').textContent;
  o.onePerSeasonScore = new RegExp('Score: \\+' + cle.gradeRate.toFixed(1).replace('.', '\\.') + ' wins a season').test(tp) && /Unadjusted, the ledger reads/.test(tp);
  const box = [...document.querySelectorAll('#view-report .hub-row')].filter(r => r.querySelector('.grade') && r.querySelector('a'));
  o.rankBoxShowsTheScore = box.length >= 3 && (() => { const v = box.map(r => parseFloat(r.lastElementChild.textContent.replace('−', '-'))); return v.every((x, i) => i === 0 || x <= v[i - 1] + 0.001); })();
  // Nov 10 afternoon: Org DNA ranks all 30, the Play card order, the tree tile, the reigning champion, one-line rows
  switchView('dna'); await wait(200);
  const Ld = dnaLeague();
  o.dnaRanksAllThirty = Ld.draft.n === 30 && [...document.querySelectorAll('#dna-leaders .dna-lead')].every(c => [...c.querySelectorAll('.hub-row strong')].map(e => e.textContent).join(',') === '1,2,3,30,29,28') && /All 30 clubs are ranked/.test(document.querySelector('.dna-leadnote').textContent);
  o.dnaNewClubsNotNamedWorst = Object.values(Ld).every(L => L.xs.slice(0, 3).concat(L.xs.slice(-3)).every(x => !x.fill));
  switchView('home'); await wait(250);
  o.playOrder = [...document.querySelectorAll('#homebody .hub-play .hp-row strong')].map(e => e.textContent).join('|') === "Deal Desk|Offseason Simulator|Scenario of the day|Pick'em|Trade Grade|Remember Some Dudes";
  const champ = CHAMPS_AUTO.slice().sort((a, b) => b.year - a.year)[0];
  o.championAnchored = new RegExp('How the ' + champ.label.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + ' were built').test(document.getElementById('homebody').textContent) && champ.year === 2026;
  const oi = TREES.findIndex(t => /Ortiz/.test(t.title)), realNow = Date.now;
  if(oi >= 0){ const day0 = Math.floor(realNow() / 864e5), shift = ((oi - day0 % TREES.length) + TREES.length) % TREES.length; Date.now = () => realNow() + shift * 864e5; renderHome(); await wait(200);
    const kids = [...document.querySelectorAll('#homebody .arch-tree .at-kid')];
    o.ortizTileShowsTheChain = /Ortiz/.test(document.querySelector('#homebody .arch-tree .at-root').textContent) && kids.length >= 3 && kids.some(k => /Burnes/.test(k.textContent)) && !/not on file/.test(document.querySelector('#homebody .arch-tree').textContent);
    Date.now = realNow; renderHome(); }
  switchView('leaderboard'); await wait(200);
  const lrows = [...document.querySelectorAll('.lb-tablecard tbody tr')].filter(t => !t.classList.contains('lb-div')).slice(0, 28);
  o.rankRowsOneLine = lrows.length >= 20 && lrows.every(tr => !/seasons? in the seat/.test(tr.textContent) && (!tr.querySelector('.execcell .tm') || tr.querySelector('.execcell .tm').getBoundingClientRect().height < 22)) && new Set(lrows.map(tr => Math.round(tr.getBoundingClientRect().height))).size <= 2;
  // a player page has its own link; a near-miss spelling still finds him
  treeOverlay('605141', 'LAD', 'Mookie Betts'); await wait(400);
  o.playerLink = /player=605141/.test(location.hash) && !!document.getElementById('tree-ov');
  closeTreeOverlay(); await wait(60);
  o.playerLinkClears = !/player=/.test(location.hash);
  switchView('home'); await wait(100);
  document.getElementById('hub-find').value = 'Mooky Bets'; folHubFind();
  o.nearSpellingFinds = /Mookie Betts/.test(document.getElementById('hub-find-out').textContent);
  document.getElementById('hub-find').value = ''; folHubFind();
  // Nov 10 evening: short tenures listed under the ranked ones, the score explained, letters explained
  switchView('leaderboard'); await wait(200);
  const trs = [...document.querySelectorAll('#lb tbody tr')], di = trs.findIndex(t => t.classList.contains('lb-div'));
  o.shortTenuresUnranked = di > 15 && trs.slice(0, di).every(t => t.querySelector('.rk').textContent.trim() === '')   /* Nov 12 (r43): no rank numbers */ && trs.slice(di + 1).every(t => t.querySelector('.rk').textContent.trim() === '') && /Under two seasons in the seat/.test(trs[di].textContent) && folActiveRank().every(r => !lbShort(r)) && folActiveRank().length === di;
  o.overallScoreExplained = /number under each Overall grade is the score, in wins a season/.test(document.getElementById('view-leaderboard').textContent) && /wins a season/.test(document.querySelector('#lb th.lb-overall').textContent);
  const ranked = folActiveRank()[0]; switchView('report', ranked.id); await wait(250);
  o.rankPoolExplained = /of the \d+ front offices with two or more seasons in the seat/.test(document.getElementById('view-report').textContent) && /graded but not ranked yet/.test(document.getElementById('view-report').textContent);
  REG_BY_ID_CUR = ranked;
  o.tradeLettersExplained = /grades each trade against other trades of its size/.test(allTradesTable(ranked));
  // "stays" calls settle on Opening Day; pitchers are not aged faster than the record supports
  try { Object.keys(localStorage).filter(k => /^fol-tp-/.test(k)).forEach(k => localStorage.removeItem(k)); } catch(e){}
  WIRE.items = []; const tpl = tpPool(), pa = tpl[0].p[1], pb = tpl[1].p[1];
  tpCall(pa, 'n'); tpCall(pb, 'y'); await wait(60);
  const before = [tpResult(pa), tpResult(pb)], nowFn = Date.now;
  Date.now = () => TP_SETTLE + 864e5;
  o.staysScoredOnOpeningDay = before[0] === null && before[1] === null && tpResult(pa) === true && tpResult(pb) === false;
  Date.now = nowFn; try { Object.keys(localStorage).filter(k => /^fol-tp-/.test(k)).forEach(k => localStorage.removeItem(k)); } catch(e){} WIRE.items = null;
  const mk = pit => { const q = DESK.players.find(x => !!x[3] === pit && !gmIsProsRow(x) && x[4] >= 27 && x[4] <= 29 && gmProj27(x) >= 3); return dkProjSeasons(q, 6, false).per; };
  const hp = mk(false), pp = mk(true);
  o.pitcherAgingNotHarsherThanTested = pp[5] / pp[0] > 0.15 && pp[5] / pp[0] <= hp[5] / hp[0] + 0.25 && /0\.03 : 0/.test(dkProjSeasons.toString());
  treeOverlay('605141', 'LAD', 'Mookie Betts'); await wait(700);
  o.extensionOnTheTradeLine = /traded BOS to LAD · control years only\. Under the LAD extension that followed: [+\-−][\d.]+ WAR in \d+ seasons so far/.test(document.getElementById('tree-ov').textContent.replace(/\s+/g, ' '));
  o.primeHittersNote = /Hitters in their prime\./.test(document.getElementById('view-method').textContent) && /Sixty-two hitters moved/.test(document.getElementById('view-method').textContent);
  { const qp = Object.keys(DESK.qo27 || {}).map(id => DESK.players.find(x => x[1] == id)).filter(Boolean)[0];
    const club = ['LAD', 'NYY', 'KC'].find(c => c !== DESK.qo27[qp[1]]), sg = dkSuggest(qp, 'fa', null);
    const t = dkFaVerdict({p: qp, yrs: sg.sugYrs, tot: sg.sugTot, club, done: 'Nov 10'}).replace(/<[^>]*>/g, ' ').replace(/\s+/g, ' ');
    o.qoPickSentence = /The forfeited draft picks? accounts? for \d\.\d wins of the cost/.test(t) && !/flat 1\.0 win for the forfeited pick/.test(t); }
  closeTreeOverlay(); await wait(60);
  o.betaLabels = /Beta/.test(document.getElementById('view-desk').textContent.slice(0, 600)) && /Beta/.test(document.getElementById('view-gm').textContent.slice(0, 600));
  return o;
}, offsJson);
// phones: the Deal Desk rosters start folded, and a search opens them
const ph = await open({width: 390, height: 844});
Object.assign(R, await ph.page.evaluate(async () => {
  const o = {}, wait = ms => new Promise(z => setTimeout(z, ms));
  switchView('desk'); dkState.mode = 'trade'; dkState.you = 'NYY'; dkState.them = 'LAA'; dkState.f = {q: '', pos: '', view: 'all', sort: 'proj'}; dkState.ro = {}; renderDesk(); await wait(200);
  const ds = () => [...document.querySelectorAll('#deskbody details.dk-rost')];
  o.phoneRostersFolded = ds().length === 2 && ds().every(d => !d.open) && document.documentElement.scrollHeight < 4000;
  dkState.f.q = 'neto'; renderDesk(); await wait(150);
  o.phoneSearchOpensRosters = ds().every(d => d.open) && /Zach Neto/.test(document.getElementById('deskbody').textContent);
  dkState.f.q = ''; return o;
}));
R.phoneErrors = ph.errors.length === 0;
await ph.browser.close();
await browser.close();
report('t_qa', R, errors);
