# Nov 12 (round 41, staged): deploy gate for the hash-name build. Refuses (exit 3) to clear index.html for upload until
# every data file the STAGED index.html loads (and the cards part the cards file loads) is served at BASE with HTTP 200
# and bytes whose md5 starts with the hash in its name. Run after the data commit; upload index.html only on exit 0.
# Usage: python3 gate_index.py <staged site dir> <base url> [--wait SECONDS]
import hashlib, os, re, sys, time, urllib.request
d, base = sys.argv[1], sys.argv[2].rstrip('/') + '/'
wait = int(sys.argv[sys.argv.index('--wait') + 1]) if '--wait' in sys.argv else 0
LIVE = {'rumors.json', 'share.json', 'wire.json'}
pg = open(os.path.join(d, 'index.html'), encoding='utf-8').read()
names = sorted({n for n in re.findall(r"""['"`]([\w.-]+\.(?:js|json))(?=[?'"`]|\$)""", pg) if n not in LIVE})
cards = [n for n in names if re.fullmatch(r'cards\.[0-9a-f]{10}\.js', n)]
for c in cards: names += re.findall(r"'(cards2[\w.]*\.js)'", open(os.path.join(d, c), encoding='utf-8').read())
op = urllib.request.build_opener(urllib.request.ProxyHandler({}) if '127.0.0.1' in base or 'localhost' in base else urllib.request.ProxyHandler())
def check(n):
    m = re.fullmatch(r'.+\.([0-9a-f]{10})\.(?:js|json)', n)
    if not m: return f'{n}: not content-hash named, refuse'
    try:
        with op.open(f'{base}{n}?gate={int(time.time())}', timeout=30) as r: code, body = r.status, r.read()
    except Exception as e: return f'{n}: {getattr(e, "code", e)}'
    h = hashlib.md5(body).hexdigest()[:10]
    return None if code == 200 and h == m.group(1) else f'{n}: HTTP {code}, md5 {h}'
t0 = time.time()
while True:
    bad = [b for b in (check(n) for n in names) if b]
    if not bad or time.time() - t0 >= wait: break
    time.sleep(20)
print(f'gate: {len(names)} data files checked at {base}; bad {len(bad)}')
for b in bad: print('  ', b)
if bad: print('REFUSE: do not upload index.html'); sys.exit(3)
print('CLEAR: every data file is live with the right bytes; index.html may be uploaded')
