(async () => {
  const wait = ms => new Promise(z => setTimeout(z, ms)), P = n => DESK.players.find(x => x[0] === n), out = [];
  const pc = n => { const p = P(n); return {kind: 'player', p, ctrl: gmIsProsRow(p) ? 6 : gmCtrlOf(p)}; };
  switchView('desk'); dkState.mode = 'trade'; await wait(100);
  const run = async (tag, you, them, ask, offer, agm) => {
    dkState.you = you; dkState.them = them; dkState.recv = ask.map(pc); dkState.send = offer.map(pc); renderDesk();
    let note = '';
    if(agm){ try { dkAgm(); } catch(e){ note = 'ERR ' + e; } await wait(30); note = note || (document.getElementById('dk-agm-note') || {textContent: ''}).textContent.replace(/^Assistant GM/, ''); }
    let ver = '';
    if(dkState.recv.length && dkState.send.length){ try { const c = dkCounterpartyCheck(); const h = dkTradeVerdict(); const d = document.createElement('div'); d.innerHTML = h; const grades = [...d.querySelectorAll('.grade')].slice(0, 3).map(e => e.textContent).join('/'); ver = (c.ok ? 'CP-YES ' : c.blocked.length ? 'CP-BLOCKED ' : 'CP-NO ') + c.txt.replace(/<[^>]+>/g, '').slice(0, 150) + ' | grades ' + grades; } catch(e){ ver = 'ERR ' + e; } }
    out.push(`#${tag} ${you}<-${them} recv[${dkState.recv.map(x => x.p[0]).join(', ')}] send[${dkState.send.map(x => x.p[0]).join(', ')}]\n   AGM: ${note.slice(0, 420)}\n   VER: ${ver}`);
  };
  await run(1, 'COL', 'LAD', [], [], 1);
  await run(2, 'LAA', 'MIL', [], [], 1);
  await run(3, 'ATH', 'NYY', [], [], 1);
  await run(4, 'NYY', 'LAA', ['Zach Neto'], [], 1);
  await run(5, 'LAD', 'KC', ['Bobby Witt Jr.'], ['Alex Call'], 1);
  await run(6, 'NYY', 'ATH', ['Nick Kurtz'], [], 1);
  await run(7, 'KC', 'LAD', ['Alex Call'], ['Bobby Witt Jr.'], 1);
  await run(8, 'NYY', 'PIT', ['Paul Skenes'], [], 1);
  await run(9, 'SD', 'COL', ['Jimmy Herget'], ['Xander Bogaerts'], 1);
  await run(10, 'SD', 'COL', [], ['Xander Bogaerts'], 1);
  await run(11, 'SF', 'LAD', ['Shohei Ohtani'], ['Jerar Encarnacion'], 0);
  await run('11b', 'SF', 'LAD', ['Shohei Ohtani'], ['Jerar Encarnacion'], 1);
  await run(12, 'BOS', 'NYM', ['Juan Soto'], ['Connor Wong'], 0);
  await run(13, 'BOS', 'NYY', ['Aaron Judge'], ['Connor Wong'], 0);
  await run(14, 'NYY', 'HOU', ['Jeremy Peña'], ['Austin Wells'], 1);
  await run(15, 'MIL', 'COL', [], [], 1);
  const sur = ['Shohei Ohtani', 'Juan Soto', 'Aaron Judge', 'Mookie Betts', 'Bobby Witt Jr.', 'Fernando Tatis Jr.', 'Xander Bogaerts', 'Ketel Marte', 'Zach Neto', 'Paul Skenes', 'Nick Kurtz', 'Hunter Goodman', 'Max Muncy', 'George Kirby', 'Gunnar Henderson'].map(n => { const p = P(n); return n + ' ' + gmSurplusRaw(p).toFixed(1) + '>' + gmSurplus(p).toFixed(1) + (gmFranchise(p) ? ' F' : '') + (gmUntouchable(p, p[2]) ? ' U' : ''); });
  const post = ['COL', 'LAA', 'ATH', 'KC', 'DET', 'SD', 'TB', 'NYM', 'PIT', 'WSH', 'LAD', 'MIL', 'NYY', 'ATL'].map(ab => { const f = folPosture(ab); return ab + ':' + f.key + '(' + f.last + '/' + f.proj + ')'; });
  return out.join('\n') + '\nSUR ' + sur.join(' | ') + '\nPOST ' + post.join(' ');
})()
