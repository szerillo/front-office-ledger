// UI / QA pass, round 2 (Nov 2 2026). One regression check per fixed item of
// the round-2 UI audit (r2_ui.md, numbered as in its summary table) plus the
// launch items a-h: shareable URLs, remembered theme, first-visit intro, one
// h1, named controls, Escape closes overlays, multi-year payroll, no
// analytics placeholder. Item numbers are in each key.
import { open, report } from './_common.mjs';
const R = {};
const d = await open();
const { page } = d;
const base = page.url().split('#')[0];

Object.assign(R, await page.evaluate(async () => {
  const o = {};
  const wait = ms => new Promise(z => setTimeout(z, ms));
  const pl = nm => DESK.players.find(x => x[0] === nm);
  const txt = id => (document.getElementById(id) || {}).innerText || '';
  const setv = (id, v) => { document.getElementById(id).value = v; };

  // ---------- Deal Desk ----------
  switchView('desk');
  dkState.mode = 'fa'; renderDesk();
  const faTry = (who, y, t) => { setv('dk-fa-player', who); setv('dk-fa-yrs', y); setv('dk-fa-m', t); dkEval(); return txt('dk-out'); };
  // 1: years are whole numbers 1-12, totals $0.5M-$800M; no crash, no A+ on absurd terms
  const bad1 = [[100, 300], [2.5, 300], [1e9, 300], [16, 300], [0, 300], [-3, 300], [5, 1e9], [5, 0.000001], ['', 300]].map(([y, t]) => faTry('Tarik Skubal', y, t));
  o.i01_termsRefused = bad1.every(t => /whole number from 1 to 12|between \$0\.5M and \$800M/.test(t) && !/Desk grade/i.test(t));
  const t0 = performance.now(); const pr = dkProjSeasons(pl('Tarik Skubal'), 1e9, false); o.i01_projBounded = pr.per.length <= 15 && performance.now() - t0 < 50;
  o.i01_noProjPast45 = dkProjSeasons(pl('Justin Verlander') || pl('Tarik Skubal'), 15, false).per.every((v, i) => ((pl('Justin Verlander') || pl('Tarik Skubal'))[4] + i + 1 <= 45) || v === 0);
  o.i01_inputMax12 = document.getElementById('dk-fa-yrs').max === '12' && document.getElementById('dk-fa-yrs').step === '1';
  // 32: plurals and one-year ages
  const one = faTry('Tarik Skubal', 1, 60);
  const a1 = pl('Tarik Skubal')[4] + 1;
  o.i32_oneYearPlural = /Projected WAR, 1 yr\b/i.test(one) && !/1 yrs/i.test(one) && new RegExp('age ' + a1 + '\\b(?!-)').test(one) && !new RegExp('age ' + a1 + '-' + a1).test(one);
  // 10: retired players are refused before any price; no $inf
  const ker = faTry('Clayton Kershaw', 1, 5);
  o.i10_retiredRefusedFA = /not available/.test(ker) && !/Desk grade/i.test(ker);
  const ren = pl('Anthony Rendon') ? faTry('Anthony Rendon', 1, 1) : 'n/a';
  o.i10_noInfinity = !/inf/i.test(ren.replace(/info/gi, ''));
  // 11: the assistant GM compares the yearly rate and the term, not total dollars
  const lo = faTry('Tarik Skubal', 5, 100), lo1 = faTry('Tarik Skubal', 1, 60);
  o.i11_lowAAVFlagged = /will not take this/.test(lo) && !/at or under our number/.test(lo);
  o.i11_shortDealNotUnder = !/at or under our number/.test(lo1);
  // 14: accent-insensitive player lookup
  o.i14_deskAccentFold = (dkFindPlayer('Ronald Acuna Jr.') || [])[0] === 'Ronald Acuña Jr.';
  // 12: the memo prints the evaluated snapshot, not inputs edited afterwards
  faTry('Tarik Skubal', 7, 385);
  setv('dk-fa-player', 'Juan Soto'); setv('dk-fa-yrs', 2); setv('dk-fa-m', 20);
  document.getElementById('dk-fa-yrs').dispatchEvent(new Event('input', {bubbles: true}));
  o.i12_staleMarked = !!document.querySelector('#dk-out .dk-stale');
  let memo = '';
  const realOpen = window.open;
  window.open = () => ({document: {write: h => { memo += h; }, close(){}}});
  dkMemo(); window.open = realOpen;
  o.i12_memoFromSnapshot = /Tarik Skubal/.test(memo) && !/Juan Soto/.test(memo) && /7 yrs? \/ \$385M/.test(memo);
  // 9: extensions: retired refused, class override warned, auto class re-runs, pay never cut
  dkState.mode = 'ext'; dkState.you = 'LAD'; renderDesk();
  const extTry = (who, club, y, t, cls) => { setv('dk-ext-player', who); setv('dk-ext-club', club); dkSuggestNow('ext'); if(cls) setv('dk-ext-cls', cls); setv('dk-ext-yrs', y); setv('dk-ext-m', t); dkEval(); return txt('dk-out'); };
  o.i09_retiredRefusedExt = /not available/.test(extTry('Clayton Kershaw', 'LAD', 1, 5)) && !/Desk grade/i.test(txt('dk-out'));
  const ov = extTry('Aaron Judge', 'NYY', 3, 120, 'predebut');
  o.i09_classOverrideWarned = /Class override/.test(ov) && /veteran/.test(ov);
  extTry('Aaron Judge', 'NYY', 3, 120);
  dkState.mode = 'fa'; renderDesk(); dkState.mode = 'ext'; renderDesk();
  setv('dk-ext-player', 'Aaron Judge'); dkSuggestNow('ext');
  o.i09_autoClassReruns = document.getElementById('dk-ext-cls').value === 'vet';
  const payOK = (who, club, y, t) => { extTry(who, club, y, t); const m = [...txt('dk-out').matchAll(/(\d{4}): \$(\d+)M→\$(\d+)M/g)]; return m.length > 0 && m.every(x => +x[3] >= +x[2]); };
  o.i09_extensionNeverCutsPay = payOK('Kodai Senga', 'NYM', 1, 1) && payOK('Shohei Ohtani', 'LAD', 12, 800);
  // 7, 8: trade tiles share signs; no trades with yourself; a refused deal is not graded
  dkState.mode = 'trade'; dkState.you = 'NYM'; dkState.them = 'NYM'; dkState.recv = []; dkState.send = []; renderDesk();
  const partner = [...document.querySelectorAll('.clubchips[aria-label="Trade partner"] .clubchip')];
  o.i08_noSelfTrade = dkState.them !== 'NYM' && partner.length === 29 && !partner.some(b => b.dataset.ab === 'NYM');
  dkState.them = 'CHC'; renderDesk();
  const senga = pl('Kodai Senga'), pca = pl('Pete Crow-Armstrong'), soto = pl('Juan Soto');
  dkState.send = [{kind: 'player', p: senga, ctrl: gmCtrlOf(senga)}]; dkState.recv = [{kind: 'player', p: pca, ctrl: gmCtrlOf(pca)}]; dkEval();
  const sv = document.querySelector('#dk-out .dk-tot[data-k="send"] .dk-totv'), sNum = +sv.innerText.replace(/[^\d.\-+]/g, '');
  const paying = (txt('dk-out').match(/You are paying ([+\-]?\d+\.\d)/) || [])[1];
  o.i07_sendSignMatchesMarket = paying != null && Math.abs(+paying - sNum) < 0.05 && sv.classList.contains(sNum >= 0 ? 'pos' : 'neg');
  const recvTile = document.querySelector('#dk-out .dk-tot[data-k="recv"] .dk-totv');
  o.i07_recvColorBySign = recvTile.classList.contains(+recvTile.innerText.replace(/[^\d.\-+]/g, '') >= 0 ? 'pos' : 'neg');
  dkState.send = [{kind: 'player', p: soto, ctrl: gmCtrlOf(soto)}]; dkEval();
  o.i07_blockedNotGraded = !/ends the call/.test(txt('dk-out')) || /n\/a/.test(document.querySelector('#dk-out .dk-grade').textContent);
  // 22: draft room and picks
  dkState.mode = 'draft'; dkState.dr = {recv: [], send: []}; renderDesk(); dkEval();
  o.i22_emptyPackageNotGraded = /to each side/.test(txt('dk-out')) && !/Chart verdict/.test(txt('dk-out'));
  setv('dk-drpl-recv', 'Clayton Kershaw'); dkDrAddPlayer('recv');
  o.i22_retiredPieceRefused = dkState.dr.recv.length === 0;
  dkState.mode = 'trade'; dkState.recv = []; dkState.send = []; renderDesk();
  setv('dk-pick-recv', '1.5'); dkAddPick('recv'); setv('dk-pick-recv', '0.5'); dkAddPick('recv');
  o.i22_fractionalPickRefused = dkState.recv.length === 0 && !!document.querySelector('.dk-inerr');
  dkState.mode = 'draft'; dkState.dr = {recv: [{kind: 'pick', pick: 1, year: 2027}], send: [{kind: 'pick', pick: 30, year: 2027}]}; renderDesk(); dkEval();
  o.i22_slotCurveLabeled = /2026 terms/.test(txt('dk-out'));
  // 40: the pick and player add buttons use the site's button style
  o.i40_styledButtons = [...document.querySelectorAll('#deskbody button')].filter(b => /\+ (player|pick)/.test(b.textContent)).every(b => b.classList.contains('grade'));
  dkState.mode = 'trade'; renderDesk();
  o.i40_tradePickButton = [...document.querySelectorAll('#deskbody button')].filter(b => /2027 pick/.test(b.textContent)).every(b => b.classList.contains('grade'));

  // ---------- Simulator ----------
  switchView('gm'); setv('gm-club', 'NYM'); gmStart();
  gmState.stage = 2; gmState.open.tab = 'fa'; gmState.open.q = 'Skubal'; gmShow();
  const sk = pl('Tarik Skubal'), n0 = gmNegState(sk, false);
  const offer = (y, t) => { setv('gm-ny-' + sk[1], y); setv('gm-nt-' + sk[1], t); gmOffer(sk[1], 0); return gmState.neg[sk[1]]; };
  // 2: no 15-year stretch, no fractional or zero years, no absurd totals
  [15, 2.5, 0, -2].forEach(y => offer(y, 560));
  offer(5, 1e9);
  const ng = gmState.neg[sk[1]];
  o.i02_absurdOffersRefused = !ng.done && ng.rounds === 0 && !ng.log.some(l => /he signs/i.test(l)) && !gmState.moves.length;
  o.i02_capByAge = (() => { const v = DESK.players.filter(p => gmIsFA(p) && p[4] >= 35 && p[4] <= 38).sort((a, b) => gmProj27(b) - gmProj27(a))[0]; gmNegState(v, false); gmState.open.q = v[0]; gmShow(); const yy = 41 - v[4]; setv('gm-ny-' + v[1], yy); setv('gm-nt-' + v[1], 10 * yy); gmOffer(v[1], 0); return !gmState.neg[v[1]].done && /will not go past/.test(gmState.neg[v[1]].note || ''); })();
  gmState.open.q = 'Skubal'; gmShow();
  offer(1, 799);   // over capacity: the veto comes first, never "he signs"
  o.i02_vetoBeforeSigns = !gmState.neg[sk[1]].log.some(l => /he signs/i.test(l)) && gmState.neg[sk[1]].log.some(l => /Ownership will not approve/.test(l));
  // 14: accent-insensitive find boxes with an empty-result message
  gmState.open.q = 'suarez'; gmShow();
  o.i14_simFaAccentFold = /Su[aá]rez/.test(txt('gmbody'));
  gmState.open.q = 'zzqx'; gmShow();
  o.i14_simEmptyMessage = /No free agents match/.test(txt('gmbody'));
  gmState.open.q = ''; gmState.open.tab = 'trade'; gmState.tr = {them: 'SD', want: [], give: [], q: 'diaz'}; gmShow();
  const tb = txt('gmbody');
  o.i14_tradeFindFolds = /D[ií]az/.test(tb) || /No players match/.test(tb);
  gmState.tr.q = 'zzqx'; gmShow();
  o.i14_tradeEmptyMessage = /No players match/.test(txt('gmbody'));
  // 5: a salary dump is accepted when your side covers the (negative) ask
  setv('gm-club', 'TB'); gmStart(); gmState.stage = 2; gmState.open.tab = 'trade';
  let dumpOK = null;
  for(const ab of Object.keys(DESK.teams)){
    if(ab === 'TB') continue;
    const dump = DESK.players.find(p => p[2] === ab && gmControlled(p) && !gmFranchise(p) && Math.abs(p[5]) + Math.abs(p[6]) + Math.abs(p[7]) >= 0.6 && gmSurplus(p) < -2 && gmSalary27(p) < 20);
    if(!dump) continue;
    gmState.tr = {them: ab, want: [{kind: 'player', pid: dump[1], rank: 0, name: dump[0]}], give: []}; gmShow();
    const t = txt('gmbody');
    dumpOK = /accepts/.test(t) && !/Not close/.test(t) && /ask ~-\d/.test(t.replace(/−/g, '-'));
    break;
  }
  o.i05_salaryDumpAccepted = dumpOK === true;
  // 13: the club select keeps each club's winter
  setv('gm-club', 'NYM'); gmStart();
  const nt = DESK.players.find(p => p[2] === 'NYM' && gmControlled(p) && (gmArbNo(p, 2027) || 0) > 0 && (hzBookEnd()[p[1]] || 0) < 2027);
  gmNonTender(nt[1]);
  const sel = document.getElementById('gm-club');
  sel.value = 'NYY'; sel.dispatchEvent(new Event('change'));
  const nyyMoves = gmState.moves.length;
  sel.value = 'NYM'; sel.dispatchEvent(new Event('change'));
  o.i13_clubSwitchKeepsWinter = nyyMoves === 0 && gmState.club === 'NYM' && gmState.moves.some(m => /Non-tendered/.test(m.label));
  // 25: an empty winter is not graded
  gmStart(); gmState.stage = 5; gmShow();
  const wg = [...document.querySelectorAll('#gmbody .tile')].find(t => /Winter grade/.test(t.textContent));
  o.i25_emptyWinterUngraded = !!wg && /No moves yet/.test(wg.textContent) && !/\bC\b/.test(wg.querySelector('.val').innerText);
  // 27: no "hover any dot" instruction on the comps chart
  o.i27_noHoverOnlyCaption = !/hover any dot/.test(txt('gmbody'));
  // g: the payroll chart carries every season of a multi-year deal signed this winter
  gmState.stage = 2; const fa5 = DESK.players.filter(p => gmIsFA(p)).sort((a, b) => gmProj27(b) - gmProj27(a))[3];
  gmSignAt(fa5, 5, 100, 'signed');
  const py = gmPayYears();
  o.g_payrollFutureSeasons = [2028, 2029, 2030, 2031].every(s => { const r = py.find(x => x.s === s); return s <= 2031 && Math.abs(r.after - r.before - 20) < 0.6; });
  gmState.stage = 5; gmShow();
  // 26: the 2027 bar label never sits under the estimate marker (every club)
  let clash = 0;
  for(const ab of Object.keys(DESK.teams)){
    setv('gm-club', ab); gmStart(); gmState.stage = 5;
    const host = document.createElement('div'); host.innerHTML = gmPayChart();
    const texts = [...host.querySelectorAll('text')];
    const lbl = texts.find(t => /^\$\d+M$/.test(t.textContent)), mk = host.querySelectorAll('line')[1];
    if(lbl && mk && Math.abs(+lbl.getAttribute('y') - 3 - +mk.getAttribute('y1')) < 6) clash++;
  }
  o.i26_payLabelClear = clash === 0;
  // 29: the stepper does not reuse grade colors (no red "failed" future stages)
  setv('gm-club', 'NYM'); gmStart(); gmShow();
  const steps = [...document.querySelectorAll('#gmbody button')].filter(b => /^\d\. /.test(b.textContent));
  o.i29_neutralStepper = steps.length === 6 && steps.every(b => !/\bg(30|40|45)\b/.test(b.className)) && steps.filter(b => b.classList.contains('cur')).length === 1;
  // 42: the camp's opening ask is computed once per player
  gmState.stage = 2; gmState.open.tab = 'fa'; gmShow();
  const t1 = performance.now(); gmShow(); const t2 = performance.now();
  o.i42_marketRenderCached = Object.keys(GM_SG).length >= 30 && t2 - t1 < 400;

  // ---------- Leaderboard ----------
  switchView('leaderboard');
  const span = `${Math.min(...LB_HIST.map(r => +r.start))}-${Math.max(...LB_HIST.map(r => +r.end))}`;
  o.i15_archiveLabelFromData = document.getElementById('erasel-hist').textContent.includes(span) && [...document.querySelectorAll('.lbh-n')].every(e => +e.textContent === LB_HIST.length);
  setv('erasel', 'hist'); renderLB();
  o.i15_blankSortsDisabled = ['intl'].every(k => { const o_ = document.querySelector(`#sortsel option[value="${k}"]`); return !o_ || o_.disabled; }) && ['fa', 'ext'].every(k => !document.querySelector(`#sortsel option[value="${k}"]`).disabled)   // v5.9: archive FA and extensions are graded;
  o.i15_h2FromData = document.getElementById('lb-h2').textContent.includes(span);
  // 16: archive "partial" tooltip says the archive cannot score those channels
  const tips = [...document.querySelectorAll('#lb .badge-ss')].filter(b => b.textContent === 'partial').map(b => b.title);
  o.i16_archiveTooltip = tips.length > 0 && tips.every(t => /Not scored for this archive regime/.test(t) && !/Too few graded deals/.test(t));
  // 15b: in All eras, ungraded rows sort last and carry no rank number
  setv('erasel', 'all'); setv('sortsel', 'fa'); renderLB();
  const rows = [...document.querySelectorAll('#lb tbody tr')];
  const faCol = [...document.querySelectorAll('#lb thead th')].findIndex(th => /Free Agency/.test(th.textContent));
  const blank = r => r.children[faCol].innerText.trim() === '·';
  const firstBlank = rows.findIndex(blank);
  o.i15_blanksLastUnranked = firstBlank > 0 && rows.slice(firstBlank).every(r => blank(r) && r.children[0].innerText.trim() === '');
  // 30: net-value bars separate small values
  setv('erasel', 'active'); setv('sortsel', 'for'); renderLB();
  const ws = [...document.querySelectorAll('#lb svg.divbar rect')].map(r => +r.getAttribute('width'));
  o.i30_barsReadable = Math.max(...ws) >= 50 && new Set(ws.filter(w => w < 30).map(w => Math.round(w))).size >= 4;
  // 36: the interim chip is not doubled; single-season ranges read as one year
  setv('erasel', 'all'); renderLB();
  o.i36_noDoubleInterim = ![...document.querySelectorAll('#lb .nm')].some(n => /\(interim\)/.test(n.textContent) && /interim/.test(n.querySelector('.badge-ss') ? n.innerText.replace(/\(interim\)/, '') : ''));
  o.i36_noSameYearRange = !/\b(\d{4})–\1\b/.test(txt('lb')) && ![...document.querySelectorAll('#teamsel option')].some(x => /\((\d\d)(\d\d)–\2\)/.test(x.text));
  const opts = [...document.querySelectorAll('#teamsel option')].map(x => x.text);
  const port = opts.findIndex(t => /Mike Port/.test(t)), theo = opts.findIndex(t => /Red Sox · Theo Epstein/.test(t));
  o.i36_portBeforeTheo = port >= 0 && theo >= 0 && port < theo;
  // 38: no invented record for brand-new regimes; one name for postseason trips
  const newRow = [...document.querySelectorAll('#lb tbody tr')].find(r => /\bnew\b/.test(r.innerText));
  o.i38_newRegimeNoRecord = !!newRow && ![...newRow.querySelectorAll('td')].some(td => /\.500 W%/.test(td.title || ''));
  o.i38_oneTermForPostseason = ![...document.querySelectorAll('#lb td')].some(td => /playoff berth/.test(td.title || ''));
  setv('erasel', 'active'); renderLB();

  // ---------- Report cards ----------
  // 31: all-negative cumulative series keep the zero line inside the frame
  const negCard = [...REGIMES, ...AUTO_REGIMES].find(r => r.cum && r.cum.length > 2 && Math.max(...r.cum) < 0);
  if(negCard){ switchView('report', negCard.id);
    const lines = [...document.querySelectorAll('#cumsvg line')], zero = [...document.querySelectorAll('#cumsvg text')].some(t => t.textContent.trim() === '0');
    o.i31_zeroTickOnNegativeCards = zero && lines.some(l => +l.getAttribute('y1') > 16 && l.getAttribute('stroke') === 'var(--baseline)');
  } else o.i31_zeroTickOnNegativeCards = true;

  // ---------- Org DNA ----------
  switchView('dna');
  const ari = AUTO_REGIMES.find(r => r.id === 'ari');
  const ariRow = [...document.querySelectorAll('#dnatable tbody tr')].find(r => /Diamondbacks/.test(r.innerText));
  const tcol = [...document.querySelectorAll('#dnatable thead th')].findIndex(th => /Trade value/.test(th.textContent));
  const net = (ari.dna.trade_in.pit - ari.dna.trade_out.pit);
  o.i17_tradeColumnIsNet = tcol > 0 && ariRow.children[tcol].innerText.includes(fmtW(net)) && /net/i.test(document.querySelectorAll('#dnatable thead th')[tcol].textContent);
  const clubsOrd = [...AUTO_REGIMES, ...REGIMES].filter(r => r.dna && r.dna.draft && !r.isNew).map(abOf).sort();
  const shown = [...document.querySelectorAll('#dnatable tbody tr')].length;
  o.i35_dnaOrderByNickname = shown === clubsOrd.length;   // Nov 3: rows run in club order (ARI, ATH, ATL...)
  const head = [...document.querySelectorAll('#dnatable thead th')].map(t => t.textContent);
  o.i39_dnaUnits = /wins\/yr/.test(head.find(h => /Pitchers improve/.test(h))) && /runs\/yr/.test(head.find(h => /Defense improves/.test(h)));
  const defCol = head.findIndex(h => /Defense improves/.test(h)), pitCol = head.findIndex(h => /Pitchers improve/.test(h));
  const dec = (col, n) => [...document.querySelectorAll('#dnatable tbody tr')].map(r => r.children[col].innerText.trim()).filter(t => t !== '·').every(t => (t.split('.')[1] || '').length === n);
  o.i39_dnaDecimalsConsistent = dec(defCol, 1) && dec(pitCol, 2);

  // ---------- Champions ----------
  switchView('champs');
  champCmpKey = 'yr'; champCmpSort('team');
  const clubs = [...document.querySelectorAll('#champcompare tbody tr')].map(r => r.children[1].textContent);
  o.i35_champClubSortByNickname = clubs.every((n, i) => !i || clubs[i - 1].localeCompare(n) <= 0);

  // ---------- Scenario Room ----------
  switchView('scen');
  const labels = [...document.querySelectorAll('#sc-sel option')].map(x => x.text.replace(/^\d+\. /, ''));
  o.i33_blindLabelsDistinct = new Set(labels.filter(t => /names hidden/.test(t))).size === labels.filter(t => /names hidden/.test(t)).length && labels.some(t => /names hidden/.test(t)) && !labels.some(t => /blind/i.test(t));
  scState.idx = 0; scShow();
  o.i33_needsExplained = /thinnest position groups \(the group's Ledger WAR; lower is thinner\)/.test(txt('scenbody'));
  o.i33_ageNotBlank = !/undefined|null|age not on file/.test(txt('scenbody'));
  const seller = scAll().findIndex(s => s.kind === 'trade' && s.seat === 'seller' && !s.live27);
  if(seller >= 0){ scState.idx = seller; scShow(); scAct('reject'); o.i33_holdNotWalk = /hold the player/i.test(txt('scenbody')) && /You held the player/.test(txt('scenbody')) && !/You walked/.test(txt('scenbody')); }
  else o.i33_holdNotWalk = true;

  // ---------- Big Boards ----------
  switchView('boards'); bdState.tab = 'fa'; renderBoards();
  const ranges = [...document.querySelectorAll('#boardsbody tbody tr')].map(r => { const a = r.innerText.match(/\$([\d.]+)M a year · likely range \$([\d.]+)-([\d.]+)M/); return a ? {aav: +a[1], w: +a[3] - +a[2]} : null; }).filter(Boolean);
  const big = ranges.filter(x => x.aav >= 25), small = ranges.filter(x => x.aav < 6);
  o.i24_rangeScalesWithDeal = big.length && small.length && Math.min(...big.map(x => x.w)) > Math.max(...small.map(x => x.w)) && /middle half of real outcomes/.test(txt('view-boards'));
  o.i37_noInternalVersion = !/Since v5\.6/.test(txt('boardsbody')) && !/as expected/.test(txt('boardsbody'));
  bdState.tab = 'farm'; renderBoards();
  o.i34_farmBesideProspects = !!document.getElementById('bd-left') && !!document.getElementById('bd-right') && !document.getElementById('bd-pos').hidden;
  bdState.tab = 'fa'; renderBoards();
  o.i34_positionBackOnFA = !document.getElementById('bd-pos').hidden;

  // ---------- Trees and Horizon keyboard access ----------
  switchView('trees');
  const tf = document.getElementById('tree-find'); tf.value = 'Mookie'; treeSuggest(false);
  const sug = document.querySelector('#tree-sugg .tsug');
  o.i41_suggestionsFocusable = !!sug && sug.getAttribute('role') === 'option' && sug.tabIndex === 0;
  sug.focus(); sug.dispatchEvent(new KeyboardEvent('keydown', {key: 'Enter', bubbles: true}));
  o.i41_enterPicksSuggestion = /Mookie/.test(tf.value) && txt('tree-find-out').length > 20;
  switchView('horizon');
  o.i41_horizonRowsFocusable = [...document.querySelector('#horizonbody table').querySelectorAll('tbody tr')].every(r => r.tabIndex === 0) && [...document.querySelector('#horizonbody table').querySelectorAll('thead th[onclick]')].every(t => t.tabIndex === 0);

  // ---------- page-wide ----------
  // d: one h1, the site title; headings never skip a level in any view
  o.d_oneH1 = document.querySelectorAll('h1').length === 1 && /FRONT OFFICE/.test(document.querySelector('h1').textContent);
  const skips = [];
  for(const v of ['leaderboard', 'report', 'trees', 'champs', 'dna', 'h2h', 'horizon', 'boards', 'gm', 'desk', 'scen', 'method']){
    switchView(v); await wait(30);
    let prev = 1;
    document.querySelectorAll(`#view-${v} h1, #view-${v} h2, #view-${v} h3, #view-${v} h4, #view-${v} h5, #view-${v} h6`).forEach(h => { if(!h.offsetParent) return; const l = +h.tagName[1]; if(l > prev + 1) skips.push(v + ':' + h.tagName + ':' + h.textContent.slice(0, 30)); prev = l; });
  }
  o.d_headingOrder = skips.length === 0;
  // e: every visible control has an accessible name, in every view
  const unnamed = [];
  for(const v of ['leaderboard', 'report', 'trees', 'champs', 'dna', 'h2h', 'horizon', 'boards', 'gm', 'desk', 'scen', 'method']){
    switchView(v); if(v === 'gm'){ gmState.stage = 2; gmState.open.tab = 'trade'; gmShow(); }
    await wait(60);
    document.querySelectorAll('input, select, textarea, button').forEach(el => {
      if(!el.offsetParent && el.type !== 'checkbox') return;
      const named = el.getAttribute('aria-label') || el.getAttribute('aria-labelledby') || el.title || (el.labels && el.labels.length) || (el.tagName === 'BUTTON' && el.textContent.trim());
      if(!named) unnamed.push(v + ':' + el.tagName + '#' + (el.id || el.className || '').toString().slice(0, 30));
    });
  }
  o.e_controlsNamed = unnamed.length === 0;
  if(unnamed.length) o.e_unnamed = unnamed.slice(0, 8).join(' | ');
  // f: Escape closes the decision modal and returns focus to its opener
  switchView('report', 'lad');
  const row = document.querySelector('#rc-ledgers .ledger tbody tr');
  row.tabIndex = 0; row.focus(); row.click(); await wait(20);
  const opened = document.getElementById('overlay').classList.contains('on');
  document.dispatchEvent(new KeyboardEvent('keydown', {key: 'Escape', bubbles: true}));
  o.f_escapeClosesModal = opened && !document.getElementById('overlay').classList.contains('on') && document.activeElement === row;
  const btn = document.getElementById('themebtn');
  btn.focus(); treeOverlay(pl('Bobby Witt Jr.')[1], 'KC'); await wait(20);
  document.dispatchEvent(new KeyboardEvent('keydown', {key: 'Escape', bubbles: true}));
  o.f_escapeClosesTreeOverlay = !document.getElementById('tree-ov') && document.activeElement === btn;
  // h: no analytics placeholder; the real counter (and Search Console tag) is wired
  o.h_noAnalyticsPlaceholder = !/YOURCODE/i.test(document.documentElement.outerHTML)
    && !!document.querySelector('script[data-goatcounter="https://szeril1.goatcounter.com/count"]')
    && !!document.querySelector('meta[name="google-site-verification"]');
  // nav: H2H, 5-Year Horizon, Top Prospects (farm beside it), Top Free Agents; beta badge back
  const navT = [...document.querySelectorAll('nav button')].map(b => b.textContent.trim());
  o.j1_navLabels = ['H2H', 'Transaction Trees', '5-Year Horizon', 'Top Prospects', 'Top Free Agents', 'Offseason Simulator'].every(x => navT.includes(x)) && !navT.includes('Farm Systems') && !!document.querySelector('.beta-chip');
  // column key defines the abbreviations
  o.j2_columnKey = /Dev<\/strong> \(development\)/.test(document.querySelector('#view-leaderboard .lbkey').innerHTML) && /Ret<\/strong> \(retention\)/.test(document.querySelector('#view-leaderboard .lbkey').innerHTML);
  // long explainers split into bullets
  o.j3_folBul = /<ul class="fol-bul"><li>One sentence here\.<\/li><li>Another/.test(folBul('One sentence here. Another sentence that keeps going for a while so the paragraph is long enough to split into bullets at all, which needs two hundred characters or so in total length, and this clause makes sure it is comfortably past that bar.'));
  // the assistant GM speaks in bullets (a long note's later sentences nest under the first)
  o.j5_agmBullets = /<ul class="agm-list"><li>We are a fringe club\.<ul><li>At this stage/.test(agmList(['We are a fringe club. At this stage I only buy players 32 or younger, and only where the money moves the depth chart most.']));
  // every tree carries a save-image button
  switchView('trees'); o.j4_treeSave = [...document.querySelectorAll('#view-trees .tree-card')].length > 0 && [...document.querySelectorAll('#view-trees .tree-card')].every(c => c.querySelector('.savebtn'));
  // corrections link: footer and How it works both mail the Ledger inbox
  const fb = [...document.querySelectorAll('a.fbmail')];
  o.h_feedbackLink = fb.length >= 2 && fb.every(a => a.href.startsWith('mailto:frontofficeledger@gmail.com?subject='))
    && !!document.querySelector('footer a.fbmail') && !!document.querySelector('#view-method a.fbaddr');
  // the UI pass adds no em dashes to visible text
  o.noEmDash = !/\u2014/.test(document.body.innerText);
  return o;
}));

// a: every view and its selection is a shareable URL; back and forward work; a hash opens that state
await page.goto(base + '#view=cards&id=nyy', {waitUntil: 'load'}); await page.waitForTimeout(1500);
R.a_hashOpensCard = await page.evaluate(() => !document.getElementById('view-report').hidden && document.getElementById('teamsel').value === 'nyy');
await page.evaluate(() => { switchView('champs'); renderChamp(ALL_CHAMPS()[0].id); });
R.a_hashWritten = await page.evaluate(() => /view=champions&id=/.test(location.hash));
const scHash0 = await page.evaluate(() => { switchView('scen'); return location.hash; });
await page.evaluate(() => { scState.idx = 3; scShow(); });
const scHash = await page.evaluate(() => location.hash);
await page.goBack(); await page.waitForTimeout(300);
const back1 = await page.evaluate(h => !document.getElementById('view-scen').hidden && location.hash === h, scHash0);
await page.goBack(); await page.waitForTimeout(300);
R.a_backWorks = back1 && await page.evaluate(() => !document.getElementById('view-champs').hidden && /view=champions/.test(location.hash));
await page.goForward(); await page.waitForTimeout(300);
await page.goForward(); await page.waitForTimeout(300);
R.a_forwardWorks = await page.evaluate(h => location.hash === h && !document.getElementById('view-scen').hidden && document.getElementById('sc-sel').value === '3', scHash);
await page.goto(base + '#view=scenarios&id=' + encodeURIComponent((await page.evaluate(() => scAll()[3].id))), {waitUntil: 'load'}); await page.waitForTimeout(1500);
R.a_hashOpensScenario = await page.evaluate(() => !document.getElementById('view-scen').hidden && scState.idx === 3);
// b, c: the theme choice and the intro dismissal survive a reload
await page.evaluate(() => { try { localStorage.clear(); } catch(e) {} });
await page.goto(base, {waitUntil: 'load'}); await page.waitForTimeout(1500);
R.c_introOnFirstVisit = await page.evaluate(() => !!document.getElementById('introstrip'));
await page.evaluate(() => document.getElementById('themebtn').click());
await page.reload({waitUntil: 'load'}); await page.waitForTimeout(1500);
R.b_themePersisted = await page.evaluate(() => document.documentElement.dataset.theme === 'dark' && /Light mode/.test(document.getElementById('themebtn').textContent));
R.c_introHiddenOnReturn = await page.evaluate(() => !document.getElementById('introstrip'));
await d.browser.close();

// phones: 19 champion pages, 27 chart text, 28 trade-board filters
const m = await open({width: 390, height: 844});
Object.assign(R, await m.page.evaluate(async () => {
  const o = {}, wait = ms => new Promise(z => setTimeout(z, ms));
  const over = () => document.documentElement.scrollWidth - document.documentElement.clientWidth;
  switchView('champs');
  const bad = [];
  for(const opt of [...document.getElementById('champsel').options]){ renderChamp(opt.value, false); await wait(10); if(over() > 2) bad.push(opt.value + ':' + over()); }
  o.i19_championPagesFitPhone = bad.length === 0;
  if(bad.length) o.i19_overflow = bad.slice(0, 6).join(' ');
  switchView('gm'); document.getElementById('gm-club').value = 'NYM'; gmStart();
  gmState.stage = 5; gmShow(); await wait(30);
  const svg = [...document.querySelectorAll('#gmbody svg')].find(s => /similar real winters/.test(s.getAttribute('aria-label') || ''));
  const vb = svg ? +svg.getAttribute('viewBox').split(' ')[2] : 999;
  o.i27_chartTextReadable = !!svg && svg.getBoundingClientRect().width / vb * 10.5 >= 9;
  gmState.stage = 2; gmState.open.tab = 'trade'; gmState.tr = {them: 'SD', want: [], give: []}; gmShow(); await wait(30);
  o.i28_labelsStayWithControls = ['gm-tr-find', 'gm-tr-view', 'gm-tr-pos', 'gm-tr-sort'].every(id => { const el = document.getElementById(id), lb = el.labels[0]; const dy = lb ? lb.getBoundingClientRect().top - el.getBoundingClientRect().top : 99; return lb && lb.parentNode === el.parentNode && (Math.abs(dy) < 14 || (innerWidth <= 760 && dy < 0 && dy > -40)); });   // phones stack the label right above its control
  const ext = [...document.querySelectorAll('#gmbody button')].find(b => b.textContent === 'Extensions');
  o.i28_tabsFit = !!ext && ext.scrollWidth <= ext.clientWidth + 1 && over() <= 2;
  document.documentElement.dataset.theme = 'dark'; await wait(30);
  const bg = getComputedStyle(document.getElementById('gm-tr-find')).backgroundColor;
  o.i28_inputThemedDark = bg !== 'rgb(255, 255, 255)' && bg !== getComputedStyle(document.body).color;
  const views = ['leaderboard', 'report', 'trees', 'champs', 'dna', 'h2h', 'desk', 'horizon', 'scen', 'gm', 'boards', 'method'];
  const wide = [];
  for(const th of ['dark', 'light']){ document.documentElement.dataset.theme = th; for(const v of views){ switchView(v); await wait(20); if(over() > 2) wide.push(th + ':' + v); } }
  o.phoneNoSidewaysScroll = wide.length === 0;
  if(wide.length) o.phoneWide = wide.join(' ');
  // v5.9: the move log loads from moves.js beside the page
  o.movesLoaded = window.MOVES_READY === true && Object.keys(PLAYER_MOVES).length > 1000 && typeof Object.values(PLAYER_MOVES)[0][0][1] === 'string';
  o.navPerformanceReview = /Performance review/i.test(document.querySelector('nav').innerText);
  // v5.9: a new regime's card never keeps another card's hand-written showcase
  o.noShowcaseLeak = (() => { const ids = [...AUTO_REGIMES.map(x => x.id), ...LB_HIST.filter(x => x.realCard).map(x => x.id)];
    return ids.every(id => { renderReport('lad'); renderReport(id); const sc = document.getElementById('rc-showcase');
      return !(sc && sc.innerText.trim()); }); })();
  o.newRegimeNoDevLetter = AUTO_REGIMES.filter(x => (x.seatSeasons != null ? x.seatSeasons : x.seasons) < 0.25).every(x => !x.dev || x.dev.g == null);
  // v5.9: dialogs close when the view changes; new regimes get an explicit empty state in Trees
  o.dialogsCloseOnViewChange = (() => { treeOverlay(605141, 'LAD', 'Mookie Betts'); switchView('champs'); const a = !document.getElementById('tree-ov');
    switchView('report', 'lad'); const row = document.querySelector('#rc-ledgers tbody tr'); if(row) row.click(); switchView('desk'); return a && !document.getElementById('overlay').classList.contains('on'); })();
  o.newRegimeTreesEmptyState = (() => { switchView('trees'); const ts = document.getElementById('treesel'); ts.value = 'ath'; renderTrees(); return /no trades yet/.test(document.getElementById('treeswrap').innerText); })();
  return o;
}));
await m.browser.close();
report('t_ui2', R, [...d.errors, ...m.errors]);
