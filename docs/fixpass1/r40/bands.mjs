// Challenge A: trade-channel bands before (rb5 = old live) and after (live), Minaya's score, and GMs near a cutoff
import fs from 'fs';
import { open } from '/tmp/r40/repo/tests/_common.mjs';
const {browser, page} = await open();
const out = await page.evaluate(() => {
  const all = [...AUTO_REGIMES, ...LB_HIST];
  all.forEach(r => { try { applyGradePolicy(r); } catch(e){} });
  const SD = gradeSD(), rows = [];
  for(const r of all){
    for(const k of ['draft','trade','fa','waiver','intl','ext']){
      const c = r.chan[k]; if(!c || c.g == null || c.net == null) continue;
      const S = r.seasons + GRADE_K, z = c.net / S / SD[k];
      // distance to nearest cutoff, in wins of channel net
      const d = Math.min(...GRADE_Z.map(([t]) => Math.abs(c.net - t * S * SD[k])));
      rows.push({id: r.id, k, net: c.net, n: c.n, S, z, g: c.g, dWins: d});
    }
  }
  return {SD, K: GRADE_K, Z: GRADE_Z, rows};
});
fs.writeFileSync(process.env.OUT, JSON.stringify(out));
await browser.close();
