// shared harness: TARGET=live runs against the deployed page, default local
import { createRequire } from 'module';
import { execSync } from 'child_process';
const require = createRequire(import.meta.url);
let chromium;
try { ({ chromium } = require('playwright')); }
catch {
  const g = execSync('npm root -g').toString().trim();
  ({ chromium } = require(g + '/playwright'));
}
export async function open(viewport){
  const url = process.env.TARGET === 'live'
    ? 'https://szerillo.github.io/front-office-ledger/prototype/?v=' + Date.now()
    : 'file://' + (process.env.PAGE || '/work/front-office-ledger-prototype.html');
  const browser = await chromium.launch();
  const page = await browser.newPage({viewport: viewport || {width:1500, height:1000}});
  const errors = [];
  page.on('pageerror', e => errors.push(e.message.slice(0, 160)));
  await page.goto(url, {waitUntil: 'load', timeout: 120000});
  await page.waitForTimeout(2600);
  return {browser, page, errors};
}
export function report(name, results, errors){
  const fails = Object.entries(results).filter(([k, v]) => v === false);
  console.log(name, JSON.stringify(results, null, 1));
  console.log('page errors:', errors.length ? errors : 'none');
  if(fails.length || errors.length){ console.log('FAIL:', fails.map(([k]) => k).join(', ')); process.exitCode = 1; }
  else console.log('PASS');
}
