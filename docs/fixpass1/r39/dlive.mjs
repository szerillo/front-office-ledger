import { open } from '/tmp/golive/tree2/tests/_common.mjs'; import fs from 'fs';
const {browser, page} = await open();
const r = await page.evaluate(() => [...AUTO_REGIMES, ...LB_HIST].map(x => ({id: x.id, forGrade: x.forGrade, chan: Object.fromEntries(Object.entries(x.chan || {}).map(([k, c]) => [k, c ? {n: c.n, net: c.net, g: c.g} : null]))})));
fs.writeFileSync('/tmp/note/live_regimes.json', JSON.stringify(r)); console.log(r.length, location ? '' : ''); await browser.close();
