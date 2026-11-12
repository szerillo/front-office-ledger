// returning visitor across a deploy: visit OLD, switch the server to NEW (Pages-style max-age=600), visit again with a
// fresh page URL. No page.route anywhere (routing turns the HTTP cache off).
import { createRequire } from 'module'; import { execSync } from 'child_process'; import fs from 'fs';
const require = createRequire(import.meta.url); const { chromium } = require(execSync('npm root -g').toString().trim() + '/playwright');
const [OLD, NEW] = process.argv.slice(2);
fs.rmSync('/tmp/cachetest/cur', {force: true}); fs.symlinkSync('/tmp/cachetest/' + OLD, '/tmp/cachetest/cur');
const b = await chromium.launch(); const ctx = await b.newContext(); const p = await ctx.newPage();
const got = []; p.on('response', r => { if(/cards/.test(r.url())) got.push(r.url().replace(/.*\//, '') + (r.fromServiceWorker() ? '' : '') + ' ' + r.status()); });
const probe = async () => { await p.waitForFunction(() => window.CARDS_READY === true, null, {timeout: 40000}).catch(() => {});
  return await p.evaluate(async () => { const D = window.CARD_DETAIL || {}; const s = JSON.stringify(Object.keys(D).sort().map(k => [k, D[k]]));
    const h = [...new Uint8Array(await crypto.subtle.digest('SHA-256', new TextEncoder().encode(s)))].map(x => x.toString(16).padStart(2, '0')).join('').slice(0, 12);
    return {ready: window.CARDS_READY === true, clubs: Object.keys(D).length, fp: h, banner: !!document.getElementById('cards-fail')}; }); };
await p.goto('http://127.0.0.1:8766/?visit=1'); console.log(OLD, 'first visit', JSON.stringify(await probe()));
fs.unlinkSync('/tmp/cachetest/cur'); fs.symlinkSync('/tmp/cachetest/' + NEW, '/tmp/cachetest/cur'); got.length = 0;
const p2 = p; await p2.goto('http://127.0.0.1:8766/?visit=2'); console.log(NEW, 'return visit', JSON.stringify(await probe()), 'card requests:', got.join(', '));
const c3 = await b.newContext(); const p3 = await c3.newPage();
const fp3 = await (async () => { await p3.goto('http://127.0.0.1:8766/?visit=3'); await p3.waitForFunction(() => window.CARDS_READY === true, null, {timeout: 40000}).catch(() => {});
  return await p3.evaluate(async () => { const D = window.CARD_DETAIL || {}; const s = JSON.stringify(Object.keys(D).sort().map(k => [k, D[k]]));
    return [...new Uint8Array(await crypto.subtle.digest('SHA-256', new TextEncoder().encode(s)))].map(x => x.toString(16).padStart(2, '0')).join('').slice(0, 12); }); })();
console.log(NEW, 'fresh browser (truth)', fp3);
await b.close();
