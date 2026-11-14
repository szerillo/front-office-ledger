// Round 55 (Nov 14 audit, blocker 3): on every report card, the "Every trade" table's stated sum equals its rows,
// and when the trade grade's total differs by more than 0.05 the page says by how much and why: a note whose parts
// (record-completed deals + the rest) add up to the gap, one "record completed" mark per such row, and never the old
// "before each player's value is rounded" wording. Exit 1 on any miss. Usage: [TARGET=live LIVE_URL=<site>] [PAGE=<file>] node tradetotal_check.mjs
import { open, report } from './_common.mjs';
const d = await open();
await d.page.waitForFunction(() => window.BOOK_READY === true, null, {timeout: 90000}).catch(() => {});
const r = await d.page.evaluate(async () => {
  if (typeof cardsReady === 'function') { try { await cardsReady(); } catch (e) {} }
  normalizeCurated();
  const pages = [...(typeof REGIMES !== 'undefined' ? REGIMES : []), ...AUTO_REGIMES, ...LB_HIST.filter(x => x.realCard)];
  const seen = new Set(), problems = []; let n = 0, gaps = 0, rep = 0, oldText = 0;
  const num = t => parseFloat(String(t).replace(/[^\d.\-+]/g, ''));
  for (const reg of pages) {
    if (seen.has(reg.id) || reg.isNew) continue; seen.add(reg.id);
    const rows = regimeTrades(reg); if (!rows.length) continue;
    const box = document.createElement('div'); box.innerHTML = allTradesTable(reg); n++;
    const txt = box.textContent;
    if (/before each player's value is rounded/.test(txt)) { oldText++; problems.push(reg.id + ': old rounding wording'); }
    const sum = rows.reduce((a, x) => a + x.net, 0);
    const m = box.querySelector('summary').textContent.match(/rows sum to ([+\-−]?[\d.]+)/);
    if (!m || Math.abs(num(m[1].replace('−', '-')) - sum) > 0.051) problems.push(reg.id + ': stated sum ' + (m && m[1]) + ' vs rows ' + sum.toFixed(2));
    const ch = (reg.chan.trade || {}).net, gap = ch != null && Math.abs(ch - sum) > 0.05;
    const note = box.querySelector('[data-tdgap]');
    const marks = box.querySelectorAll('[data-rep]').length, repN = rows.filter(x => x.rep != null).length; rep += repN;
    if (marks !== repN) problems.push(reg.id + ': marks ' + marks + ' vs completed rows ' + repN);
    if (gap) { gaps++;
      if (!note) { problems.push(reg.id + ': gap ' + (ch - sum).toFixed(2) + ' with no note'); continue; }
      if (Math.abs(parseFloat(note.dataset.tdgap) - (ch - sum)) > 0.051) problems.push(reg.id + ': note gap ' + note.dataset.tdgap + ' vs ' + (ch - sum).toFixed(2));
      if (repN && !/record completed/.test(note.textContent)) problems.push(reg.id + ': completed rows not explained');
    } else if (note) problems.push(reg.id + ': note with no gap');
  }
  return {cards: n, gaps, completedRows: rep, oldText, problems};
});
console.log('problems:', r.problems.length, r.problems.slice(0, 15));
report('tradetotal_check', {cards_checked_over_100: r.cards > 100, gap_notes: r.gaps, completed_rows: r.completedRows, old_wording_0: r.oldText === 0, problems_0: r.problems.length === 0}, d.errors);
await d.browser.close();
