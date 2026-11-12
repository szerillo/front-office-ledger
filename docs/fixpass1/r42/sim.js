// Round 42: the pre-registered rank-threshold run (prereg_rank_threshold.md, r41), run in a Baseball-Reference tab
// (same-origin daily WAR files). Fetches its other inputs from this commit on GitHub. Writes window.__SIM.
// Interpretation notes (fixed before the run; see run_notes.md): unit = player-team-season with stint rows summed;
// playing time = B-R PA + IPouts; thirds = tercile cut points of the matched sample; a player's third = mean playing
// time over all his terms; residual vector cycled over his seasons; totals move by sum(coef x residual), the
// production totals being sums of WAR with costs that do not move with WAR. Decision rule: 90% of 2,000 draws.
async function runSim(SHA){
  const raw = p => fetch(`https://raw.githubusercontent.com/szerillo/front-office-ledger/${SHA}/${p}`).then(r => r.json());
  const spec = await raw('docs/fixpass1/r42/winter_spec.json'), samp = await raw('docs/fixpass1/r42/sample300.json');
  const C = await raw('data/lvm_cache.json');
  const B = {};
  for (const f of ['war_daily_bat.txt', 'war_daily_pitch.txt']) {
    const t = await (await fetch('/data/' + f)).text(); const L = t.split('\n'); const h = L[0].split(','); const ix = k => h.indexOf(k);
    const I = {id: ix('mlb_ID'), y: ix('year_ID'), tm: ix('team_ID'), w: ix('WAR'), pa: ix('PA'), ip: ix('IPouts')};
    for (let i = 1; i < L.length; i++) { const c = L[i].split(','); const y = +c[I.y]; if (!(y >= 1998)) continue;
      const k = c[I.id] + '|' + y + '|' + c[I.tm]; const o = B[k] || (B[k] = {b: 0, pt: 0});
      o.b += (c[I.w] === 'NULL' || c[I.w] === '') ? 0 : +c[I.w]; o.pt += f[10] === 'b' ? (+c[I.pa] || 0) : (+c[I.ip] || 0); }
  }
  // team name -> B-R code, learned from single-stint player-years (20+ agreements)
  const byPY = {}; for (const k in B) { const [id, y, tm] = k.split('|'); (byPY[id + '|' + y] = byPY[id + '|' + y] || []).push(tm); }
  const cnt = {}; for (const id in C) { const v = C[id]; if (!v || !v.rows) continue; const per = {};
    v.rows.forEach(r => { if (r[0] >= 1998) (per[r[0]] = per[r[0]] || new Set()).add(r[1]); });
    for (const y in per) { const b = byPY[id + '|' + y]; if (per[y].size === 1 && b && b.length === 1) { const kk = [...per[y]][0] + '>' + b[0]; cnt[kk] = (cnt[kk] || 0) + 1; } } }
  const M = {}; for (const kk in cnt) { const [n, c] = kk.split('>'); if (cnt[kk] >= 20) (M[n] = M[n] || []).push(c); }
  const A = {}; for (const id in C) { const v = C[id]; if (!v || !v.rows) continue; v.rows.forEach(r => { if (r[0] >= 1998) { const k = id + '|' + r[0] + '|' + r[1]; A[k] = (A[k] || 0) + r[2]; } }); }
  const look = (id, y, tn) => { for (const c of (M[tn] || [])) { const o = B[id + '|' + y + '|' + c]; if (o) return o; } return null; };
  // 1. disagreement sample
  const S = []; let miss = 0;
  for (const [id, y, tn] of samp.sample) { const o = look(id, y, tn); if (!o) { miss++; continue; } S.push({id, y, r: A[id + '|' + y + '|' + tn] - o.b, pt: o.pt}); }
  const pts = S.map(s => s.pt).sort((a, b) => a - b), c1 = pts[Math.floor(pts.length / 3)], c2 = pts[Math.floor(2 * pts.length / 3)];
  const third = pt => pt < c1 ? 0 : pt < c2 ? 1 : 2;
  const mean = a => a.reduce((s, x) => s + x, 0) / a.length, sd = a => { const m = mean(a); return Math.sqrt(a.reduce((s, x) => s + (x - m) ** 2, 0) / a.length); };
  const res = {n: S.length, missing: miss, mean: mean(S.map(s => s.r)), sd: sd(S.map(s => s.r)), cuts: [c1, c2], byThird: [0, 1, 2].map(t => { const a = S.filter(s => third(s.pt) === t).map(s => s.r); return [a.length, mean(a), sd(a)]; })};
  const sp = {}; S.forEach(s => (sp[s.id] = sp[s.id] || []).push(s)); const pool = [[], [], []];
  for (const id in sp) { const v = sp[id].sort((a, b) => a.y - b.y); pool[third(mean(v.map(s => s.pt)))].push(v.map(s => s.r)); }
  // 2. winters and players
  const W = Object.keys(spec.tot).map(k => ({k, tot: spec.tot[k], terms: spec.terms[k] || []}));
  const pl = {}; W.forEach(w => w.terms.forEach(([id, y, tn]) => { const o = look(id, y, tn); (pl[id] = pl[id] || []).push(o ? o.pt : 0); }));
  const pid = Object.keys(pl), pidx = Object.fromEntries(pid.map((p, i) => [p, i])), pth = pid.map(p => third(mean(pl[p])));
  W.forEach(w => { const by = {}; w.terms.forEach(t => (by[t[0]] = by[t[0]] || []).push(t)); w.P = Object.entries(by).map(([p, ts]) => [pidx[p], ts.sort((a, b) => a[1] - b[1]).map(t => t[4])]); });
  let s = 20261150 >>> 0; const rnd = () => { s |= 0; s = s + 0x6D2B79F5 | 0; let t = Math.imul(s ^ s >>> 15, 1 | s); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; };
  const NDRAW = 2000, T = W.map(() => new Float64Array(NDRAW)), T2 = W.map(() => new Float64Array(NDRAW));
  for (let d = 0; d < NDRAW; d++) {
    const pick = pth.map(t => pool[t][Math.floor(rnd() * pool[t].length)]);
    const ind = pth.map(t => null);   // sensitivity: an independent draw for every season
    W.forEach((w, i) => { let x = w.tot, x2 = w.tot; w.P.forEach(([pi, coefs]) => { const v = pick[pi];
      coefs.forEach((c, j) => { x += c * v[j % v.length]; const q = pool[pth[pi]][Math.floor(rnd() * pool[pth[pi]].length)]; x2 += c * q[0]; }); }); T[i][d] = x; T2[i][d] = x2; });
  }
  // 3. adjacent pairs, best list (descending) and worst list (ascending), every settled winter
  const ord = W.map((w, i) => i).sort((a, b) => W[b].tot - W[a].tot);
  const pair = (A1, Bx, M) => { let ahead = 0, dd = []; for (let d = 0; d < NDRAW; d++) { const z = M[A1][d] - M[Bx][d]; if (z > 0) ahead++; dd.push(z); } const m = mean(dd); return {p: ahead / NDRAW, gap: W[A1].tot - W[Bx].tot, need: 1.2816 * sd(dd) - (m - (W[A1].tot - W[Bx].tot))}; };
  const best = [], worst = [], all = [];
  for (let i = 0; i + 1 < ord.length; i++) { const q = pair(ord[i], ord[i + 1], T), q2 = pair(ord[i], ord[i + 1], T2); all.push(q.need);
    if (i < 21) best.push([W[ord[i]].k, W[ord[i]].tot, W[ord[i + 1]].k, +q.p.toFixed(3), +q2.p.toFixed(3)]); }
  for (let i = ord.length - 1; i >= ord.length - 21; i--) { const q = pair(ord[i - 1], ord[i], T), q2 = pair(ord[i - 1], ord[i], T2);
    worst.push([W[ord[i]].k, W[ord[i]].tot, W[ord[i - 1]].k, +q.p.toFixed(3), +q2.p.toFixed(3)]); }
  all.sort((a, b) => a - b);
  return window.__SIM = {sha: SHA, res, players: pid.length, winters: W.length, best, worst, medianGapFor10pctFlip: all[Math.floor(all.length / 2)], noB_R: Object.values(pl).flat().filter(x => x === 0).length};
}
