// v5.4: the public-launch pass. Each check is a defect found in the
// pre-launch review (Nov 2 2026) or a promise made in the page copy.
import { open, report } from './_common.mjs';
const d = await open();
const r = await d.page.evaluate(() => {
  const o = {};
  const pl = nm => DESK.players.find(x => x[0] === nm);
  const body = document.body.innerText;
  // jargon and copy
  o.noLVMJargon = !/\bLVM\b/.test(document.documentElement.innerHTML);
  o.noOverclaim = !/Nothing is an opinion/.test(body);
  o.aboutDisclaimer = /Not affiliated with, endorsed by, or sponsored by Major League Baseball/.test(document.querySelector('footer').innerText) && !!document.querySelector('footer a[href*="github.com/szerillo/front-office-ledger"]');
  o.themeLabelPlain = /^(Dark|Light) mode$/.test(document.getElementById('themebtn').textContent.trim());
  o.pluralHelper = pz(1, 'pennant', 'pennants') === '1 pennant' && pz(2, 'pennant', 'pennants') === '2 pennants';
  o.noDeadAccountingSelect = !document.getElementById('realsel');
  o.warExplained = /Reading the numbers, in one minute/.test(document.getElementById('view-method').innerHTML) && /How to read a row/.test(document.getElementById('view-leaderboard') ? document.getElementById('view-leaderboard').innerHTML : document.body.innerHTML);
  o.noEscapedQuote = !/\\u2019/.test(body);
  // free-agent deals end in free agency, not arbitration (Senga)
  const senga = pl('Kodai Senga');
  o.sengaControlEndsWithDeal = !senga || gmCtrlEnd(senga) === (hzBookEnd()[senga[1]] || gmCtrlEnd(senga));
  // in-season-start extensions cover the season they were signed in
  const end = hzBookEnd();
  o.acunaDealEnds2026Base = DESK.book.some(c => c[0] === 'Ronald Acuña Jr.' || c[0] === 'Ronald Acuna Jr.' ? (c[12] === 1 && c[1] + c[3] === 2026) : false);
  o.griffinThrough2034 = (end[(pl('Konnor Griffin') || [])[1]] || 0) === 2034;
  o.altuveThrough2029 = (end[(pl('Jose Altuve') || [])[1]] || 0) === 2029;
  // champions use the club's name in that season
  const champs = ALL_CHAMPS();
  const fla = champs.find(x => x.year === 2003), ana = champs.find(x => x.year === 2002);
  o.eraNames = /Florida Marlins/.test(fla.team) && /Anaheim Angels/.test(ana.team);
  o.champRegimeStillResolves = !!regimeForChamp(fla).exec && !!regimeForChamp(ana).exec;
  // Scenario Room: no future data, extension priced against extensions
  const sc = SCEN.find(s => s.id.endsWith('betts'));
  o.bettsNoFutureSeason = sc.recv.concat(sc.send).every(p => !p.mlb || p.cur === p.plat);
  const ram = SCEN.find(s => s.kind === 'ext');
  o.ramirezSpring2017 = ram.date.startsWith('2017') && ram.ctx.season === 2016 && ram.market.ext === 1 && ram.market.mktTot < 120 && ram.player.age === 24;
  const gr = SCEN.find(s => s.id.endsWith('greinke'));
  o.greinkeHasOdorizzi = gr.send.some(p => p.name === 'Jake Odorizzi');
  o.liveSetupMatchesStanding = !/edge of the wild-card race/.test(SCEN.find(s => s.id.startsWith('live')).setup);
  // simulator comps see recent winters' trades
  o.recentWintersHaveTrades = [2024, 2025].every(y => GMC.winters.filter(w => w.w === y).reduce((a, w) => a + w.trN, 0) > 50);
  // curated cards agree with the computed trade book on the Burnes deal
  const tb = TRADE_BOOK.trades.find(t => t[0] === '2024-02-01');
  const balNet = tb[1].find(s => s[0] === 'BAL')[1];
  const balCard = REGIMES.find(x => x.id === 'bal');
  const milCard = REGIMES.find(x => x.id === 'mil');
  const find = (card, re) => [].concat(...['bestTrades', 'worstTrades', 'ledger', 'top', 'bottom'].map(k => card[k] || [])).find(x => re.test(x.h || ''));
  const b1 = JSON.stringify(balCard).match(/RHP Corbin Burnes from MIL[^}]*?war:(-?[0-9.]+)/);
  // v5.7: the cards carry whatever the book computes (the number moved with the salary and positional fixes)
  const bv = Math.abs(balNet).toFixed(1).replace('.', '\\.');
  o.burnesCuratedMatchesBook = balNet < -3 && new RegExp('war":-' + bv).test(JSON.stringify(balCard)) && new RegExp('"war":' + bv).test(JSON.stringify(milCard));
  return o;
});
await d.browser.close();
report('t_launch', r, d.errors);
