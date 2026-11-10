(async () => {
  const wait = ms => new Promise(z => setTimeout(z, ms)), P = n => DESK.players.find(x => x[0] === n), out = [];
  const fa = (n, club) => { const p = P(n), sg = dkSuggest(p, 'fa', null); const h = dkFaVerdict({p, yrs: sg.sugYrs, tot: sg.sugTot, club, done: 'x'}); const d = document.createElement('div'); d.innerHTML = h; const t = d.textContent.replace(/\s+/g, ' ');
    return `${n} ${sg.sugYrs}/${sg.sugTot} fair ${sg.fairSame}: grade ${(d.querySelector('.dk-grade .grade') || {}).textContent} | ${(t.match(/Net vs a typical signing: [^ ]+ WAR/) || [''])[0]} | ${(t.match(/Projected WAR, \d+ yrs?[^A-Za-z]*/) || [''])[0]} | ${(t.match(/\$[\d.]+M per projected win[^)]*\)/) || [''])[0]}`; };
  ['Tarik Skubal', 'Seiya Suzuki', 'Randy Arozarena', 'Trevor Rogers', 'Michael King', 'Kevin Gausman', 'Adrian Morejon', 'Teruaki Sato'].forEach(n => out.push(fa(n, 'LAD')));
  const adv = async (club, stage, tab) => { switchView('gm'); document.getElementById('gm-club').value = club; gmClubChange(); await wait(200); for(let i = 0; i < stage; i++){ gmAdvance(); await wait(150); } if(tab){ gmState.open.tab = tab; } const tips = gmAdvisor(); return club + ' st' + stage + (tab || '') + ': ' + String(Array.isArray(tips) ? tips.join(' || ') : tips).replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').slice(0, 900); };
  try { out.push(await adv('BAL', 0)); out.push(await adv('SEA', 0)); out.push(await adv('COL', 2, 'fa')); out.push(await adv('COL', 2, 'trade')); out.push(await adv('DET', 2, 'fa')); out.push(await adv('DET', 2, 'trade')); out.push(await adv('LAD', 1)); out.push(await adv('MIL', 0)); } catch(e){ out.push('ERR ' + e + ' ' + (e.stack || '').slice(0, 300)); }
  return out.join('\n');
})()
