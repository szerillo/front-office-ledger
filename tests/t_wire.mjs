// Nov 2026: The Wire. The league's live transaction feed is replaced by a
// fixture (Nov 1-9, 2026) plus synthetic moves, so the checks are stable.
import { open, report } from './_common.mjs';
import fs from 'fs';
const fx = JSON.parse(fs.readFileSync(new URL('./fixtures/wire_tx.json', import.meta.url))).transactions;
const dz = JSON.parse(fs.readFileSync(new URL('../dudes.json', import.meta.url)));
const d = await open();
const R = await d.page.evaluate(async ({fx, dz}) => {
  const o = {}, wait = ms => new Promise(z => setTimeout(z, ms));
  // with the feed unreachable (the harness blocks it) the page says so and keeps working
  await wireLoad(true);
  o.feedDownHandled = /did not answer/.test(WIRE.err) && Array.isArray(WIRE.items);
  const P = n => DESK.players.find(x => x[0] === n);
  const team = ab => ({id: 1, name: CLUB_NAME[ab]});
  const aro = P('Randy Arozarena'), lowe = P('Brandon Lowe'), bau = P('Jake Bauers');
  const star = DESK.players.find(x => x[2] === 'TB' && !gmIsFA(x) && !gmIsProsRow(x) && gmSurplus(x) > 2);
  const pros = DESK.players.filter(x => gmIsProsRow(x) && x[2] === 'NYY').sort((a, b) => gmPV(b) - gmPV(a))[0];
  const extra = [
    {id: 990001, date: '2026-11-09', typeCode: 'SFA', typeDesc: 'Signed as Free Agent', person: {id: aro[1], fullName: aro[0]}, toTeam: team('SEA'), description: `Seattle Mariners signed free agent LF ${aro[0]}.`},
    {id: 990002, date: '2026-11-09', typeCode: 'SFA', typeDesc: 'Signed as Free Agent', person: {id: lowe[1], fullName: lowe[0]}, toTeam: team('NYM'), description: `New York Mets signed free agent 2B ${lowe[0]}.`},
    {id: 990003, date: '2026-11-09', typeCode: 'TR', typeDesc: 'Trade', person: {id: star[1], fullName: star[0]}, fromTeam: team('TB'), toTeam: team('NYY'), description: `Tampa Bay Rays traded ${star[0]} to New York Yankees for ${pros[0]}.`},
    {id: 990004, date: '2026-11-09', typeCode: 'TR', typeDesc: 'Trade', person: {id: pros[1], fullName: pros[0]}, fromTeam: team('NYY'), toTeam: team('TB'), description: `Tampa Bay Rays traded ${star[0]} to New York Yankees for ${pros[0]}.`},
    {id: 990005, date: '2026-11-09', typeCode: 'SFA', typeDesc: 'Signed as Free Agent', person: {id: bau[1], fullName: bau[0]}, toTeam: team('BOS'), description: `Boston Red Sox signed free agent 1B ${bau[0]}.`},
  ];
  try { localStorage.setItem('fol-wire-seen', '949000'); localStorage.removeItem('fol-wire-mine'); localStorage.removeItem('fol-qo-call-' + bau[1]); } catch(e){}
  wireLoadData(fx.concat(extra), {terms: {[lowe[1]]: {yrs: 3, tot: 60}}, qo: {}, extra: []});
  const I = id => WIRE.items.find(x => x.id === String(id));
  // trades: both sides graded, duplicates in the feed folded into one deal
  const tr = I(990003);
  o.tradeBothSides = tr && tr.sides.length === 2 && tr.sides.every(s => /^[A-F]\+?$/.test(s.g)) && Math.abs(tr.sides[0].net + tr.sides[1].net) < Math.abs(tr.sides[0].net) * 1.5 + 0.01;
  o.tradeDupesFolded = WIRE.items.filter(x => x.kind === 'trade' && /Eduardo Rivera/.test(x.desc)).length === 1 && I(WIRE.items.find(x => /Eduardo Rivera/.test(x.desc)).id).who.length === 2;
  o.depthTradeNoLetter = (() => { const t = WIRE.items.find(x => /Reifert/.test(x.desc)); return t && t.depth && t.sides.every(s => !s.g) && /depth deal/.test(wireShareText(t)); })();
  // the QO player re-signing with his own club before the deadline is the acceptance
  o.qoAcceptFromFeed = I(990001).kind === 'qo-accept' && I(990001).terms.tot === 23.15 && /^[A-F]/.test(I(990001).g);
  o.qoStatusAccepted = wireQoStatus(aro[1]) === 'accepted';
  // a QO player signing elsewhere: graded with the forfeited pick, and his QO counts as declined
  const lw = I(990002);
  o.signingGraded = lw.fa && /^[A-F]/.test(lw.g) && lw.fa.qoP && lw.player && /market/.test(lw.player.call[0]);
  o.qoStatusDeclined = wireQoStatus(lowe[1]) === 'declined';
  // terms not reported: the Ledger's number and a grade-it box
  const ba = I(990005);
  o.termsPendingBox = !ba.fa && !!ba.sg;
  switchView('wire'); await wait(100);
  o.wireRendered = !document.getElementById('view-wire').hidden && document.querySelectorAll('#wirebody .wire-item').length >= 8 && /\#view=wire/.test(location.hash);
  document.getElementById('wty-990005').value = 2; document.getElementById('wtt-990005').value = 30; wireTry('990005');
  o.gradeItYourself = /for the Red Sox/.test(document.getElementById('wto-990005').textContent);
  // the deal screen: the Desk's own sheet for the real trade and the real signing
  o.tradeSheet = !!document.querySelector('#wi-990003 .wi-sheet .dk-sheet') && /From both seats/.test(document.getElementById('wi-990003').textContent) && /Market check/.test(document.getElementById('wi-990003').textContent) && !/Will it get done/.test(document.getElementById('wi-990003').textContent);
  o.sheetGradeMatches = (() => { const el = document.querySelector('#wi-990003 .dk-grade .grade'); return el && el.textContent.trim() === I(990003).sides[0].g; })();
  o.faSheet = !!document.querySelector('#wi-990002 .wi-sheet .dk-sheet') && /What he brings/.test(document.getElementById('wi-990002').textContent);
  o.playerContext = /WAR 2024-26/.test(document.getElementById('wi-990005').textContent);
  // copy link copies the link alone
  let copied = ''; const cw = navigator.clipboard && navigator.clipboard.writeText;
  try { Object.defineProperty(navigator, 'clipboard', {value: {writeText: t => { copied = t; return Promise.resolve(); }}, configurable: true}); } catch(e){}
  wireCopy('990003'); await wait(20);
  o.copyLinkOnly = copied === 'https://frontofficeledger.com/#view=wire&id=990003';
  // sharing: text with the letters, a link to the move, X intent and replies
  let opened = ''; const wo = window.open; window.open = u => { opened = u; return null; };
  wireX('990003'); o.xIntent = /x\.com\/intent\/post\?text=Ledger%20grades/.test(opened) && /view%3Dwire%26id%3D990003/.test(opened);
  wireX('990003', 'https://x.com/someone/status/1987654321098765432'); o.xReply = /in_reply_to=1987654321098765432/.test(opened);
  window.open = wo;
  // your grade beside the Ledger's
  wireMine('990003', 'B'); await wait(30);
  o.yourGrade = /Ledger: [A-F]/.test(document.getElementById('wi-990003').textContent);
  // filters: one club, trades only
  wireSetFilt('club', 'TB'); await wait(30);
  o.clubFilter = [...document.querySelectorAll('#wirebody .wire-item')].every(e => e.querySelector('.wi-tc') && [...e.querySelectorAll('.wi-tc')].some(t => t.textContent === 'TB')) && /id=tb/.test(location.hash);
  wireSetFilt('club', ''); wireSetFilt('kind', 'trade'); await wait(30);
  o.tradeFilter = [...document.querySelectorAll('#wirebody .wire-item')].every(e => /Trade/.test(e.querySelector('.wi-kind').textContent));
  wireSetFilt('kind', 'mlb');
  // the winter so far
  const st = wireStandings(WIRE.items);
  o.winterClubMoves = (() => { const d = document.querySelector('.wire-winter .ww-club'); return d && d.querySelectorAll('.ww-mv').length >= 1 && /Every .* move this winter/.test(d.textContent); })();
  o.standings = st.length >= 5 && st[0].net >= st[st.length - 1].net && /Who has won the offseason/.test(document.getElementById('wirebody').textContent);
  // QO calls: make one, see it once the decision is in
  const other = Object.keys(DESK.qo27).find(k => ![aro[1], lowe[1], bau[1]].map(String).includes(k));
  try { localStorage.removeItem('fol-qo-call-' + other); } catch(e){}
  wireQoCall(other, 'decline'); await wait(30);
  o.qoCallSaved = /Your call: he declines/.test(document.querySelector('.wire-qo').textContent);
  // a poll: once you vote you see how everyone voted, and the vote is locked in
  o.qoPollShown = !!document.querySelector('.wire-qo .wq-bar') && /say he declines/.test(document.querySelector('.wire-qo').textContent);
  wireQoCall(other, 'accept'); o.qoVoteLocked = wireQoMine(other) === 'decline';
  wireQoCall(bau[1], 'decline'); await wait(30);
  o.qoCallScored = /You called it/.test(document.querySelector('.wire-qo').textContent) && /You are 1 for 1/.test(document.querySelector('.wire-qo').textContent);
  try { localStorage.removeItem('fol-qo-call-' + other); localStorage.removeItem('fol-qo-call-' + bau[1]); } catch(e){}
  // free agent pick'em: over/under on the Ledger's number, then the exact deal, then your record
  const pk = pkPool(); o.pickemPool = pk.length >= 10 && pk.every(x => x.sg.sugTot >= 10);
  const pp = pk.find(x => !wireActual(x.p[1])).p[1];
  try { localStorage.removeItem('fol-pk-' + pp); } catch(e){}
  pkOU(pp, 'over'); await wait(150);
  pkOU(pp, 'under'); o.pickemLocked = pkMine(pp).ou === 'over';
  o.pickemCrowdBar = /% over/.test(document.querySelector('.wire-pk').textContent);
  pkOpen(pp); await wait(150);
  document.getElementById('pky-' + pp).value = 4; document.getElementById('pkt-' + pp).value = 100; pkPredict(pp); await wait(150);
  o.pickemPredicted = pkMine(pp).yrs === 4 && Math.abs(pkMine(pp).aav - 25) < 0.01 && /Your call/.test(document.querySelector('.wire-pk').textContent);
  o.pickemCrowdMedian = (() => { const c = pkCrowd(pp); return c && c.yrs >= 1 && c.aav > 0; })();
  o.myCalls = /Over\/unders/.test((document.querySelector('.wire-my') || {}).textContent || '');
  // every projection on a signing card: Ledger, published, model, fair, comps
  o.projTable = (document.querySelector('#wi-990005 .wp-tab') || {}).textContent && /Ledger offer/.test(document.querySelector('#wi-990005 .wp-tab').textContent) && /Model-fair/.test(document.querySelector('#wi-990005 .wp-tab').textContent);
  o.projVsActual = /Off by/.test((document.querySelector('#wi-990002 .wp-tab') || {}).textContent || '');
  try { localStorage.removeItem('fol-pk-' + pp); } catch(e){}
  // new since your last visit, then marked seen
  o.newCount = wireNewCount() > 0;
  wireMarkSeen(); o.markSeen = wireNewCount() === 0;
  // deep link to one move
  location.hash = '#view=wire&id=990002'; await wait(300);
  o.deepLink = WIRE.focus === '990002' && !!document.querySelector('#wi-990002.wi-focus');
  // Deal Desk from a wire trade
  wireDesk('990003'); await wait(400);
  o.openInDesk = dkState.you === I(990003).sides[0].ab && dkState.recv.length === 1 && dkState.send.length === 1 && !!document.querySelector('#dk-out .dk-sheet');
  // the assistant GM leaves a depth swap alone (no closer thrown into a deal of fringe arms), and roster needs
  // only come up when proven big leaguers change hands
  wireDesk(WIRE.items.find(x => /Eduardo Rivera/.test(x.desc)).id); await wait(300);
  const nSend = dkState.send.length; dkAgm(); await wait(50);
  o.agmDepthFair = dkState.send.length === nSend && /Fair as built/.test(document.getElementById('dk-agm-note').textContent);
  dkEval(); await wait(50);
  o.noNeedsOnDepth = !/address its needs|Fills a real need/.test((document.getElementById('dk-out') || {}).textContent || '');
  // a trade with a player who is not on our boards still opens whole
  wireDesk(WIRE.items.find(x => /Eduardo Rivera/.test(x.desc)).id); await wait(400);
  o.deskUnknownPiece = [...dkState.recv, ...dkState.send].some(pc => pc.kind === 'other' && /Juan Garc/.test(pc.nm)) && !!document.querySelector('#dk-out .dk-sheet');
  // home: the latest graded moves at the top
  WIRE.focus = ''; switchView('home'); await wait(200);
  o.homeWinter = !!document.querySelector('#hub-winter .wire-winter .ww-club');
  o.homeStrip = document.querySelectorAll('#hub-wire .hw-row').length >= 3 && /Qualifying offer decisions due|Rule 5|Non-tender|labor deal/.test(document.getElementById('hub-wire').textContent);
  o.navWire = !!document.querySelector('nav button[data-view="wire"]');
  // the offseason hub: a club's winter, the money, the reports, the labor clock
  WIRE.focus = ''; WIRE.filt = {club: 'TB', kind: 'mlb'}; WIRE.tab = 'feed'; switchView('wire'); await wait(150);
  o.clubPanel = /The Rays winter/.test(document.querySelector('.wire-club').textContent) && /2027 payroll/.test(document.querySelector('.wire-club').textContent) && /Out:.*Junior Caminero|Out:.*/.test(document.querySelector('.wire-club').textContent);
  o.clubFlows = (() => { const c = wireClubWinter('NYY'); return c.ins.some(x => x.w.pid === star[1]) && c.dWar > 0; })();
  o.moneyCard = document.querySelectorAll('.wire-money .wm-row').length === 30;
  o.laborClock = /until the labor deal expires|Lockout|labor deal/.test(document.querySelector('.wire-labor').textContent);
  WIRE.filt.club = ''; location.hash = '#view=wire&id=daily'; await wait(300);
  o.dailyReport = WIRE.tab === 'daily' && /The Ledger Daily/.test(document.getElementById('wire-daily').textContent) && document.querySelectorAll('#wire-daily .wr-mv').length >= 1;
  location.hash = '#view=wire&id=weekly'; await wait(300);
  o.weeklyReport = WIRE.tab === 'weekly' && document.querySelectorAll('#wire-weekly .wr-club').length === 30;
  WIRE.tab = 'feed';
  // Remember Some Dudes: ten a day across the eras, over/under on career WAR, a link to each player's page
  dudesLoadData(dz); DUDES.st = null; try { localStorage.removeItem('fol-dudes-day-' + dudeDay()); } catch(e){}
  switchView('dudes'); await wait(100);
  o.dudesTen = DUDES.st && DUDES.st.qs.length === 10 && DUDES.st.qs.filter(q => q.y0 < 1960).length >= 3 && /Career WAR: over or under/.test(document.getElementById('dudesbody').textContent);
  const q0 = DUDES.st.qs[0]; dudesCall(q0.war > q0.line ? 'over' : 'under'); await wait(50);
  o.dudesReveal = DUDES.st.ans[0] === true && !!document.querySelector('#dudesbody a[href^="https://www.baseball-reference.com/players/"]');
  for(let k = 1; k < 10; k++){ dudesNext(); dudesCall('over'); } dudesNext(); await wait(50);
  o.dudesDone = DUDES.st.done && /Remember Some Dudes \d+\/10/.test(dudesShareText()) && !!dudesStore('day-' + dudeDay());
  o.dudesLinesFair = (() => { const xs = DUDES.rows.map(dudeOf); const over = xs.filter(q => q.war > q.line).length / xs.length; return over > 0.4 && over < 0.6; })();
  try { localStorage.removeItem('fol-dudes-day-' + dudeDay()); } catch(e){}
  // games have their own links: pick'em lands on its card, open
  location.hash = '#view=wire&id=pickem'; await wait(400);
  o.pickemLink = !document.getElementById('view-wire').hidden && document.querySelector('.wire-pk').open && document.querySelector('.wire-pk').classList.contains('wi-focus');
  // the deal ledger on a heist: WAR and salary separately, the new-contract note on Santana
  folPartsData({'2008-02-02|276371|NYM': [0, 0, null, null, 0, 1], '2008-02-02|460576|MIN': [10.4, 0.6, 2008, 2013, 0, 0]});
  const sant = folTrades().find(x => x.d === '2008-02-02' && x.S.some(s => s.ab === 'NYM'));
  o.dealLedger = !!sant && /signed a new contract/.test(folDealLedger(sant)) && /\+10\.4/.test(folDealLedger(sant)) && /Gave up/.test(folDealLedger(sant));
  // Trade Grade: days in a row played
  const day = Math.floor(Date.now() / 864e5); folQuizStore('day-' + (day - 1), [true]); folQuizStore('day-' + (day - 2), [false]); try { localStorage.removeItem('fol-quiz-day-' + day); } catch(e){}
  o.quizDaysInARow = folQuizDays() === 2;
  try { localStorage.removeItem('fol-quiz-day-' + (day - 1)); localStorage.removeItem('fol-quiz-day-' + (day - 2)); } catch(e){}
  return o;
}, {fx, dz});
await d.browser.close();
// phones: the wire fits
const m = await open({width: 390, height: 844});
Object.assign(R, await m.page.evaluate(async (fx) => {
  const o = {}, wait = ms => new Promise(z => setTimeout(z, ms));
  wireLoadData(fx, WIRE_FALLBACK); switchView('wire'); await wait(200);
  o.phoneWireFits = document.documentElement.scrollWidth - document.documentElement.clientWidth <= 2;
  o.phoneQoFolded = !document.querySelector('.wire-qo').open;
  return o;
}, fx));
await m.browser.close();
report('t_wire', R, [...d.errors, ...m.errors]);
