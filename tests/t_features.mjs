// Feature presence and integrity across tabs.
import { open, report } from './_common.mjs';
const { browser, page, errors } = await open();
const r = await page.evaluate(() => {
  const out = {};
  // leaderboard alignment
  out.lbColsMatch = document.querySelectorAll('#lb thead th').length ===
                    document.querySelector('#lb tbody tr').children.length;
  // no internal version labels in visible text
  out.noVersionLabels = !document.body.innerText.match(/Ledger WAR v\d|sweep v\d|Projection v\d/);
  // charts
  out.calibScatter = document.querySelectorAll('#calib-chart circle').length > 1000;
  // styles + h2h
  switchView('dna'); out.styleHeader = document.body.innerHTML.includes('<th>Org</th><th>Style</th>');
  switchView('h2h'); if(typeof renderH2hTab === 'function') renderH2hTab();
  out.busiestLines = document.getElementById('h2hfreq').innerHTML.includes('show the deals');
  // tree endings + overlay
  switchView('trees');
  const tw = document.body.innerHTML;
  out.fateEndings = /No MLB appearances after|Still with the club through|Left without a graded move/.test(tw);
  const witt = DESK.players.find(x => x[0] === 'Bobby Witt Jr.');
  treeOverlay(witt[1], 'KC');
  out.overlayOpens = !!document.getElementById('tree-ov');
  document.getElementById('tree-ov').remove();
  // champions compare
  switchView('champs');
  out.champCompare = document.getElementById('champcompare').innerHTML.includes('side by side');
  // GM surfaces
  switchView('gm'); document.getElementById('gm-club').value = 'MIL'; gmStart();
  const body = () => document.getElementById('gmbody').innerHTML;
  out.agmInlineCalls = /AGM: (tender|non-tender candidate|offer it|let him walk)/.test(body());
  out.depthStrip = body().includes('live, after your moves');
  gmState.stage = 2; gmState.open.tab = 'money'; gmShow();
  out.salaryBook = body().includes('salary book, 2027-2031');
  gmState.stage = 3; gmShow();
  out.diamond = body().includes('<svg') && body().includes('ROTATION');
  gmState.stage = 4; gmShow();
  out.reportCharts = body().includes('Where the money sits');
  // horizon salary
  switchView('horizon'); if(typeof renderHorizon === 'function') renderHorizon();
  out.horizonSalary = document.getElementById('view-horizon').innerHTML.includes('salary book, season by season');
  // methodology integrity
  switchView('method');
  const mt = document.getElementById('view-method').innerHTML;
  out.methodComplete = mt.includes('Validation: does the metric hold up') && mt.includes('About this project');
  switchView('report');
  out.reportClean = !document.getElementById('view-report').innerHTML.includes('Validation: does the metric hold up');
  return out;
});
report('t_features', r, errors);
await browser.close();
