// rollback race: a visitor holds the candidate page and cards.js in cache but never got the second part (it was
// blocked on visit 1). The server is then rolled back. Visit 2 reuses the cached page URL.
import { createRequire } from 'module'; import { execSync } from 'child_process'; import fs from 'fs';
const require = createRequire(import.meta.url); const { chromium } = require(execSync('npm root -g').toString().trim() + '/playwright');
const [CAND, RB, TRUTH] = process.argv.slice(2);
const sw = d => { fs.rmSync('/tmp/cachetest/cur', {force: true}); fs.symlinkSync('/tmp/cachetest/' + d, '/tmp/cachetest/cur'); };
sw(CAND);
const b = await chromium.launch(); const ctx = await b.newContext(); const p = await ctx.newPage();
const cdp = await ctx.newCDPSession(p); await cdp.send('Network.enable'); await cdp.send('Network.setBlockedURLs', {urls: ['*cards2*']});
const got = []; p.on('response', r => { if(/cards/.test(r.url())) got.push(r.url().replace(/.*\//, '') + ' ' + r.status()); });
const probe = async (ms) => { await p.waitForFunction(() => window.CARDS_READY === true, null, {timeout: ms}).catch(() => {});
  return await p.evaluate(async () => { const D = window.CARD_DETAIL || {}; const s = JSON.stringify(Object.keys(D).sort().map(k => [k, D[k]]));
    const h = [...new Uint8Array(await crypto.subtle.digest('SHA-256', new TextEncoder().encode(s)))].map(x => x.toString(16).padStart(2, '0')).join('').slice(0, 12);
    const fail = document.getElementById('cards-fail');
    return {ready: window.CARDS_READY === true, clubs: Object.keys(D).length, fp: h, banner: fail ? fail.textContent.trim().slice(0, 60) : null}; }); };
await p.goto('http://127.0.0.1:8766/?visit=1'); console.log('visit 1 on', CAND, 'with part 2 blocked', JSON.stringify(await probe(8000)), got.join(', '));
await cdp.send('Network.setBlockedURLs', {urls: []}); sw(RB); got.length = 0;
await p.goto('http://127.0.0.1:8766/?visit=1'); console.log('visit 2 after rollback to', RB, JSON.stringify(await probe(12000)), got.join(', '), '| truth for the cached candidate page', TRUTH);
await b.close();
