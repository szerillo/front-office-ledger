import { open } from './_common.mjs';
import fs from 'fs';
const d = await open();
const per = await d.page.evaluate(() => { const W = GMC.winters || []; const pick = prevW => W.map(x => ({x, d: Math.abs(x.prevW - prevW) / 10 + Math.abs(x.faM - 0) / 120 + Math.abs(x.faN - 0) / 2.5 + Math.abs(x.trN - 0) / 2.5})).sort((a, b) => a.d - b.d).slice(0, 5);
  return Object.fromEntries(Object.keys(DESK.teams || {}).sort().map(ab => { const c = pick((GMC.wins2026 || {})[ab] || 81); return [ab, +(c.reduce((a, y) => a + (y.x.nextW - y.x.prevW), 0) / c.length).toFixed(3)]; })); });
fs.writeFileSync(process.env.OUT, JSON.stringify(per)); console.log(Object.keys(per).length); await d.browser.close();
