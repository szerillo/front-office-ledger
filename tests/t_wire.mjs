// Nov 2026: The Wire. The league's live transaction feed is replaced by a
// fixture (Nov 1-9, 2026) plus synthetic moves, so the checks are stable.
import { open, report } from './_common.mjs';
import fs from 'fs';
const fx = JSON.parse(fs.readFileSync(new URL('./fixtures/wire_tx.json', import.meta.url))).transactions;
const d = await open();
const R = await d.page.evaluate(async (fx) => {
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
  o.standings = st.length >= 5 && st[0].net >= st[st.length - 1].net && /Who has won the offseason/.test(document.getElementById('wirebody').textContent);
  // QO calls: make one, see it once the decision is in
  const other = Object.keys(DESK.qo27).find(k => ![aro[1], lowe[1], bau[1]].map(String).includes(k));
  try { localStorage.removeItem('fol-qo-call-' + other); } catch(e){}
  wireQoCall(other, 'decline'); await wait(30);
  o.qoCallSaved = /Your call: he declines/.test(document.querySelector('.wire-qo').textContent);
  wireQoCall(bau[1], 'decline'); await wait(30);
  o.qoCallScored = /You called it/.test(document.querySelector('.wire-qo').textContent) && /You are 1 for 1/.test(document.querySelector('.wire-qo').textContent);
  try { localStorage.removeItem('fol-qo-call-' + other); localStorage.removeItem('fol-qo-call-' + bau[1]); } catch(e){}
  // new since your last visit, then marked seen
  o.newCount = wireNewCount() > 0;
  wireMarkSeen(); o.markSeen = wireNewCount() === 0;
  // deep link to one move
  location.hash = '#view=wire&id=990002'; await wait(300);
  o.deepLink = WIRE.focus === '990002' && !!document.querySelector('#wi-990002.wi-focus');
  // Deal Desk from a wire trade
  wireDesk('990003'); await wait(400);
  o.openInDesk = dkState.you === 'TB' && dkState.them === 'NYY' && dkState.recv.length === 1 && dkState.send.length === 1;
  // home: the latest graded moves at the top
  WIRE.focus = ''; switchView('home'); await wait(200);
  o.homeStrip = document.querySelectorAll('#hub-wire .hw-row').length >= 3 && /Qualifying offer decisions due|Rule 5|Non-tender|labor deal/.test(document.getElementById('hub-wire').textContent);
  o.navWire = !!document.querySelector('nav button[data-view="wire"]');
  // Trade Grade: days in a row played
  const day = Math.floor(Date.now() / 864e5); folQuizStore('day-' + (day - 1), [true]); folQuizStore('day-' + (day - 2), [false]); try { localStorage.removeItem('fol-quiz-day-' + day); } catch(e){}
  o.quizDaysInARow = folQuizDays() === 2;
  try { localStorage.removeItem('fol-quiz-day-' + (day - 1)); localStorage.removeItem('fol-quiz-day-' + (day - 2)); } catch(e){}
  return o;
}, fx);
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
