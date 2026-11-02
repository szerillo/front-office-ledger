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
  // the Deal Desk reads the same winter and the same farms
  switchView('desk'); dkState.mode = 'trade'; dkState.you = 'NYM'; dkState.them = 'TB'; renderDesk();
  o.deskNoRankNumberBox = !document.getElementById('dk-rank-recv') && document.getElementById('dk-farm-recv').options.length >= 16;
  const inp = document.getElementById('dk-in-send'); inp.value = 'Tarik Skubal'; dkAdd('send');
  o.deskFreeAgentNotATradePiece = !dkState.send.some(pc => pc.p && pc.p[0] === 'Tarik Skubal');
  dkState.mode = 'fa'; renderDesk();
  document.getElementById('dk-fa-player').value = 'Teruaki Sato'; document.getElementById('dk-fa-yrs').value = 4; document.getElementById('dk-fa-m').value = 62; dkEval();
  o.deskChargesPostingFee = /posting fee/.test(document.getElementById('dk-out').innerText);
  document.getElementById('dk-fa-player').value = 'Chris Sale'; dkSuggestNow('fa');
  o.deskSaysUnderContract = /under contract with ATL through 2027/.test(document.getElementById('dk-suggest').innerText);
  return o;
});
await d.browser.close();
report('t_winter', r, d.errors);
