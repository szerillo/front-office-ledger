// v5.2: the 2026-27 winter as it actually happened, the posted class, and
// org prospects in the simulator. Each check is a real decision or a real
// defect from the Nov 1-2 2026 reality pass.
import { open, report } from './_common.mjs';
const d = await open();
const r = await d.page.evaluate(async () => {
  const o = {};
  const pl = nm => DESK.players.find(x => x[0] === nm);
  // real decisions
  o.saleUnderContract = !gmIsFA(pl('Chris Sale')) && gmControlled(pl('Chris Sale')) && Math.abs(gmBookAAVFor(pl('Chris Sale'), 2027) - 27) < 0.01;
  o.hoernerThrough2032 = (hzBookEnd()[pl('Nico Hoerner')[1]] || 0) === 2032;
  o.rasmussenOptionExercised = Math.abs(gmBookAAVFor(pl('Drew Rasmussen'), 2027) - 20) < 0.01 && !gmIsFA(pl('Drew Rasmussen'));
  o.acunaOptionAt17 = Math.abs(gmBookAAVFor(pl('Ronald Acuña Jr.'), 2027) - 17) < 0.01;
  o.declinedAreFree = ['Nick Pivetta', 'Jeff McNeil', 'Clay Holmes', 'Michael King', 'Emilio Pagán', 'Luis Robert Jr.'].every(n => gmIsFA(pl(n)));
  o.optedInStay = ['Bo Bichette', 'Corbin Burnes', 'Tatsuya Imai'].every(n => !gmIsFA(pl(n)));
  o.imaiGuarantee54 = DESK.book.some(c => c[0] === 'Tatsuya Imai' && c[4] === 54);
  o.retiredGone = ['Clayton Kershaw', 'Kyle Hendricks', 'Chad Green'].every(n => !gmIsFA(pl(n)) && !gmControlled(pl(n)));
  o.claseRestricted = !gmIsFA(pl('Emmanuel Clase')) && !gmControlled(pl('Emmanuel Clase'));
  o.pendingTagged = gmStatus(pl('Kenley Jansen'))[0] === 'pendfa' && /Nov 2/.test(gmStatus(pl('Kenley Jansen'))[1]);
  o.onFileNeverComps = DESK.players.slice(0, 400).every(p => dkCompContracts(p, 8).every(c => c[12] === 0));
  o.noMinorLeagueFAsOnBoard = DESK.players.every(p => !(gmIsFA(p) && !(DESK.posted||{})[p[1]] && Math.abs(p[5]) + Math.abs(p[6]) + Math.abs(p[7]) < 0.06));
  // qualifying offers: only players with the club since Opening Day, never a second QO
  o.qoTradedIneligible = !gmQOEligible(pl('Tarik Skubal')) && !gmQOEligible(pl('Clay Holmes'));
  o.qoPriorIneligible = !gmQOEligible(pl('Michael King')) && !gmQOEligible(pl('Sonny Gray'));
  o.qoSuzukiEligible = gmQOEligible(pl('Seiya Suzuki'));
  // posted class
  const posted = ['Teruaki Sato', 'Kaima Taira', 'Hiromi Itoh', 'Si Hwan Roh'].map(pl);
  o.postedPresent = posted.every(p => p && gmIsFA(p) && (DESK.posted||{})[p[1]] && gmStatus(p)[0] === 'posted');
  o.postingFeeTiers = Math.abs(dkPostingFee(20) - 4) < 1e-9 && Math.abs(dkPostingFee(62) - 11.175) < 1e-9 && Math.abs(dkPostingFee(100) - 16.875) < 1e-9;
  o.postedPricedOffPostedMarket = posted.every(p => { const sg = dkSuggest(p, 'fa', null); return sg.pz && sg.comps.length === 0 && sg.mktTot > 0; });
  switchView('gm'); document.getElementById('gm-club').value = 'NYY'; gmStart();
  const sato = pl('Teruaki Sato'); gmSignAt(sato, 4, 60, 'signed');
  const mv = gmState.moves.find(m => /Sato/.test(m.label));
  o.postingFeeInSurplus = !!mv && /posting fee/.test(mv.detail);
  // org prospects: a farm for every club, tradable, promotable
  o.everyClubHasAFarm = Object.keys(DESK.teams).every(ab => gmFarmOf(ab).length >= 15);
  gmStart();
  const tb = gmFarmOf('TB').filter(x => !x[9]).sort((a, b) => gmPV(b) - gmPV(a))[0];
  const mine = gmFarmOf('NYY').sort((a, b) => gmPV(b) - gmPV(a));
  gmState.tr = {them: 'TB', want: [], give: []};
  gmTrAdd('want', 'prospect', tb[1], tb[9], tb[0]);
  mine.slice(0, 2).forEach(p => gmTrAdd('give', 'prospect', p[1], p[9], p[0]));
  const ok = gmGiveVal() >= gmAskPieces().ask * 0.95;
  gmTrExec();
  o.prospectTradeMovesFarms = ok && gmFarmOf('NYY').some(x => x[1] === tb[1]) && !gmFarmOf('TB').some(x => x[1] === tb[1]) && !gmFarmOf('NYY').some(x => x[1] === mine[0][1]);
  gmPromote(tb[1]);
  o.promotedJoinsDepthChart = gmFullRoster().some(x => x[1] === tb[1]) && Math.abs(gmProj27(tb) - gmProsY1(tb)) < 1e-9;
  gmUndo(gmState.moves.find(m => m.kind === 'trade').id);
  o.undoReturnsProspects = !gmState.farmIn.has(tb[1]) && !gmState.outs.has(mine[0][1]) && !gmFullRoster().some(x => x[1] === tb[1]);
  // Phase II: peak projections on prospects; org tier valued by its comps
  const made = pl('Jesús Made');
  o.peakOnTop100 = !!gmPeakOf(made) && /peak/.test(dkProjPlayer(made, 6).how) && Math.abs(dkProjPlayer(made, 6).total - gmVrank(made[9], made[3])) < 1e-9;
  const org = DESK.players.find(p => (DESK.pros||{})[p[1]] && !p[9] && gmPeakOf(p) && Math.abs(p[5])+Math.abs(p[6])+Math.abs(p[7]) === 0);
  o.orgValuedByComps = !!org && Math.abs(gmPV(org) - DESK.pros[org[1]][1]) < 1e-9 && /comparables/.test(dkProjPlayer(org, 6).how);
  o.peakSane = Object.values(DESK.peak).every(k => k[0] >= 0 && k[0] <= 8 && k[2] <= k[1] + 1e-9 && k[1] <= 1 && (k[7].length >= 4 || !k[7].length));   // Top 100 prospects with no minor-league line carry the rank history alone
  o.backtestBeatsBuckets = DESK.peakBacktest.unranked.comps_r > DESK.peakBacktest.unranked.level_age_bucket_r;
  // trees end where the player stands today (v5.3.2)
  const nm2 = Object.assign({}, TRADE_BOOK.names, PLAYER_NAMES); const pidOf = n => Object.keys(nm2).find(k => nm2[k] === n);
  const holmesT = tnode(careerTree(pidOf('Clay Holmes'))).replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ');
  o.holmesEndsAtCubsThenFree = /where it stands Finished 2026 with CHC; free agent this winter \(declined his \$12M player option\)/.test(holmesT);
  o.holmesPiecesCurrent = /Tyrone Taylor\b.{0,80}Finished 2026 with CHC; free agent this winter/.test(holmesT) && /Jefferson Rojas\b.{0,80}No MLB record yet; NYM prospect/.test(holmesT) && !/now under/.test(holmesT);
  const morelT = tnode(careerTree(pidOf('Christopher Morel'))).replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ');
  o.morelMinorLeagueDealToMets = /signed a minor-league deal with NYM/.test(morelT) && /where it stands Finished 2026 with NYM/.test(morelT);
  // v5.9: DESK clubs come from the Stats API's current organization, so a
  // player traded, claimed, signed or released after his last 2026 game is
  // on his new club (Blake Perkins CLE, Richard Fitts STL). The fate keeps
  // the club he finished 2026 with; where they differ, the chain must say
  // where he is now (or carry a winter status), never silently disagree.
  o.fateMatchesCurrentClub = Object.entries(PLAYER_FATE).every(([pid, [ly, lab]]) => { if(ly < 2026) return true; const q = DESK.players.find(x => x[1] === +pid); if(!q || !q[2] || !lab || q[2] === lab) return true;
    return !!(DESK.status||{})[pid] || new RegExp('with ' + q[2] + '\\b').test(chainFate(pid, lab).nm); });
  // the Deal Desk reads the same winter and the same farms
  switchView('desk'); dkState.mode = 'trade'; dkState.you = 'LAD'; dkState.them = 'TB'; dkState.send = []; dkState.recv = []; renderDesk();
  const ids = side => [...document.querySelectorAll(`button[onclick^="dkTake('${side}',"]`)].map(b => +b.getAttribute('onclick').match(/,(\d+)\)/)[1]);
  const recvIds = ids('recv'), sendIds = ids('send');
  o.deskPickersScopedToClubs = !document.getElementById('dk-rank-recv') && recvIds.length >= 30 && recvIds.every(id => DESK.players.find(x => x[1] === id)[2] === 'TB') && sendIds.every(id => DESK.players.find(x => x[1] === id)[2] === 'LAD');
  o.deskFreeAgentNotATradePiece = !sendIds.includes(DESK.players.find(x => x[0] === 'Tarik Skubal')[1]);
  o.deskNoDefaultClub = (() => { const y = dkState.you, t = dkState.them; dkState.you = null; dkState.them = null; renderDesk(); const ok = !document.querySelector('.clubchip.on') && !document.querySelector('[aria-label="Trade partner"]'); dkState.you = y; dkState.them = t; renderDesk(); return ok; })();
  dkEval(); o.deskEmptyTradeNotGraded = /at least one piece on each side/.test(document.getElementById('dk-out').innerText);
  dkTake('send', sendIds[sendIds.length - 1]); dkTake('recv', recvIds[0]); dkEval();
  o.deskAcceptanceCheck = /Would TB accept\?/.test(document.getElementById('dk-out').innerText);
  dkState.send = []; dkState.recv = []; renderDesk(); dkAgm();
  o.deskAgmCompletes = dkState.recv.length >= 1 && dkState.send.length >= 1 && /Assistant GM/.test(document.getElementById('dk-agm-note').innerText) && /Would TB accept\?/.test(document.getElementById('dk-out').innerText);
  dkState.mode = 'fa'; renderDesk();
  document.getElementById('dk-fa-player').value = 'Teruaki Sato'; document.getElementById('dk-fa-yrs').value = 4; document.getElementById('dk-fa-m').value = 62; dkEval();
  o.deskChargesPostingFee = /posting fee/.test(document.getElementById('dk-out').innerText);
  document.getElementById('dk-fa-player').value = 'Chris Sale'; dkSuggestNow('fa');
  o.deskSaysUnderContract = /under contract with ATL through 2027/.test(document.getElementById('dk-suggest').innerText);
  // the live winter: a free agent who signs on the league feed leaves the market and joins his club
  { const sk2 = DESK.players.find(x => x[0] === 'Tarik Skubal'); const was = gmIsFA(sk2);
    liveApply([{person: {id: sk2[1]}, toTeam: {id: 147}, typeCode: 'SFA', date: '2026-12-05', description: 'New York Yankees signed free agent LHP Tarik Skubal.'}]);
    o.liveSigningApplied = was && !gmIsFA(sk2) && sk2[2] === 'NYY' && gmSalary27(sk2) > 20 && /Ledger offer/.test(gmStatus(sk2)[1]); }
  // the simulator: stars ask contenders for less, the rest of the market clears near the Ledger offer
  switchView('gm'); document.getElementById('gm-club').value = 'PIT'; gmStart();
  const skb = DESK.players.filter(x => gmIsFA(x)).sort((a, b) => gmProj27(b) - gmProj27(a))[0];
  const club0 = gmState.club, askPit = gmAsk(skb, false).tot; gmState.club = 'LAD'; const askLad = gmAsk(skb, false).tot; gmState.club = club0;
  o.simStarsDiscountContenders = askLad < askPit;
  gmState.stage = 2; gmState.open.tab = 'trade'; gmState.tr = {them: 'MIA', want: [], give: []}; gmShow(); gmAgmComplete();
  o.simAgmBuildsDeal = gmState.tr.want.length >= 1 && gmState.tr.give.length >= 1 && /Assistant GM/.test(document.getElementById('gmbody').innerText);
  gmState.stage = 5; gmShow();
  const M = gmMarketSim(), sg = M.out.filter(x => x.club), vs = sg.map(x => x.vs).sort((a, b) => a - b);
  o.simMarketClears = sg.length >= 40 && sg.every(x => x.club !== 'PIT') && Math.abs(vs[Math.floor(vs.length / 2)]) <= 0.1 && !/rest of the market/.test(document.getElementById('gmbody').innerText);   // the league market runs but is no longer shown
  // Nov 2026: no club bids past its own free-agent history; the memo is one page, depth chart first
  const SP = gmClubSpend();
  o.simSpendHistory = sg.every(x => !SP[x.club] || x.tot / x.yrs <= Math.max(SP[x.club].max * 1.2, 12) + 0.01);
  gmMemo(); const memo = document.getElementById('gm-memo-page');
  o.memoOnePage = !!memo && !!memo.querySelector('#gm-depth-card') && /The winter, move by move/.test(memo.innerText) && /Winters that looked like yours/.test(memo.innerText) && /Where the money sits/.test(memo.innerText)
    && memo.innerText.indexOf('depth chart') < memo.innerText.indexOf('Winters that looked like yours');
  document.getElementById('gm-memo').remove();
  switchView('desk'); dkState.mode = 'fa'; renderDesk();
  o.deskFaClass = document.querySelectorAll('#dk-fa-class tbody tr').length >= 40 && !!document.getElementById('dk-fa-pos');
  // Nov 3: the memo ends with the league's winter and saves as two images
  gmMemo(); const mm = document.getElementById('gm-memo-page');
  o.memoAroundLeague = /Around the league/.test(mm.innerText) && mm.innerText.indexOf('Around the league') > mm.innerText.indexOf('Where the money sits');
  const parts = gmMemoParts(); o.memoTwoImages = parts.length === 2 && /gm-depth-card/.test(parts[0].inner) && /Winters that looked like yours/.test(parts[1].inner) && !/gm-depth-card/.test(parts[1].inner);
  o.imageBrand = /@SeanZerillo/.test(mm.querySelector('.ff-head').innerText) && /@SeanZerillo/.test(mm.querySelector('.ff-foot').innerText) && !!mm.querySelector('.ff-head svg');
  document.getElementById('gm-memo').remove();
  // trade walk, available players, the two-sided verdict and its memo
  const P = n => DESK.players.find(x => x[0] === n);
  dkState.mode = 'walk'; dkState.you = 'SF'; dkState.walk = P('Logan Webb')[1]; renderDesk();
  const wrows = document.querySelectorAll('#dk-walk-out tbody tr');
  o.tradeWalk = wrows.length >= 6 && [...wrows].every(r => /Open on the board/.test(r.innerText));
  dkWalkLoad(dkWalkOffer(P('Logan Webb'), 'SF', 'SD').buyer);
  o.tradeWalkLoads = dkState.mode === 'trade' && dkState.them === 'SD' && dkState.send.length === 1 && dkState.recv.length >= 1 && /Will it get done\?/.test(document.getElementById('dk-out').innerText);
  dkState.mode = 'avail'; renderDesk(); const AV = dkAvailList();
  o.availList = AV.length >= 40 && AV.every(x => !(gmFranchise(x.p) && gmClubPosture(x.ab) !== 'rebuilding')) && document.querySelectorAll('#deskbody tbody tr').length >= 20;
  dkState.mode = 'trade'; dkState.you = 'BOS'; dkState.them = 'PIT';
  dkState.recv = [{kind: 'player', p: P('Oneil Cruz'), ctrl: gmCtrlOf(P('Oneil Cruz'))}]; dkState.send = [{kind: 'player', p: P('Jarren Duran'), ctrl: gmCtrlOf(P('Jarren Duran'))}]; renderDesk(); dkEval();
  const chip = document.querySelector('.tdeal').innerText;
  o.pieceShowsTerms = /\$\d+\.\dM in 2027/.test(chip) && /years? of control \(through 20\d\d\)/.test(chip) && !document.querySelector('.tdeal button[onclick^="dkCtrl"]');
  const out = document.getElementById('dk-out').innerText;
  o.verdictBothSides = /Boston Red Sox/.test(out) && /Pittsburgh Pirates/.test(out) && !/Sandbox verdict/.test(out);
  const comps = [...document.querySelectorAll('#dk-out .card')].find(c => /Similar real trades/.test(c.textContent));
  o.compsMatchShape = !!comps && (comps.innerText.match(/\(outfielder\) for [^(]+\(outfielder\)/g) || []).length >= 3;
  let dm = ''; const ro = window.open; window.open = () => ({document: {write: h => { dm += h; }, close(){}}}); dkMemo(); window.open = ro;
  o.dealMemoNeutral = !/sandbox verdict|class="foot"|Assistant GM|class="tiles"/i.test(dm) && /Pittsburgh Pirates get/.test(dm) && /@SeanZerillo/.test(dm);
  // Antonetti is one Cleveland tenure from 2010
  const cle = [...AUTO_REGIMES, ...(typeof LB_HIST !== 'undefined' ? LB_HIST : [])].filter(r => /Antonetti/.test(r.exec));
  o.antonettiOneTenure = cle.length === 1 && String(cle[0].startDate || cle[0].start).startsWith('2010');
  // Nov 3 (late): trade block naming, no cornerstone chips, horizon picker on top, 2026 debuts on the boards
  dkState.mode = 'walk'; dkState.you = 'SF'; renderDesk();
  o.tradeBlockNamed = /Trade block/i.test(document.getElementById('deskbody').innerText) && /player to shop/i.test(document.getElementById('deskbody').innerText) && !/Trade walk/.test(document.body.innerText);
  o.noCornerstoneChip = !/CORNERSTONE/.test(document.body.innerHTML);
  switchView('horizon'); hzPick('');
  const hc = document.getElementById('hz-chips');
  o.horizonPickerTop = !!hc && /All 30/.test(hc.innerText) && hc.querySelectorAll('.clubchip').length === 30 && !!(hc.compareDocumentPosition(document.getElementById('horizonbody')) & Node.DOCUMENT_POSITION_FOLLOWING) && !document.querySelector('#horizonbody .clubchips');
  hzPick('BOS'); o.horizonEndsGrouped = !/\(control ends\)|\(contract ends\)/.test(document.getElementById('horizonbody').innerText);
  const before = gmState.club; switchView('gm'); gmRandomClub(); o.simRandomClub = !!gmState.club && gmState.club !== before && document.getElementById('gm-club').value === gmState.club;
  const pratt = P('Cooper Pratt'), dp = P('Josue De Paula');
  o.debutsOnBoards = Object.keys(DESK.deb26 || {}).length >= 50 && (!pratt || !gmIsProsRow(pratt) || bdLvl(pratt) === 'MLB') && (!dp || !gmIsProsRow(dp) || bdLvl(dp) === 'MLB');
  return o;
});
await d.browser.close();
report('t_winter', r, d.errors);
