#!/usr/bin/env python3
# Round 54 one-command rollback: python3 rollback_r54.py <out dir>
# Fetches the pre-deploy version (commit 579b86d) of every file the round 54 deploy changed, checks md5s, and writes
# them into <out dir> with their repo paths, ready for the GitHub web upload (root files, o/, og/o/, tests/fixtures/,
# engine/). corrections/2026-11-14.html did not exist before; the rollback replaces it with a one-line note.
import sys, os, hashlib, urllib.request
BASE = 'https://raw.githubusercontent.com/szerillo/front-office-ledger/579b86d/'
W = ['2007-bal', '2009-nyy', '2010-mil', '2011-ath', '2011-cin', '2012-mia', '2012-tor', '2013-tex', '2014-bos', '2014-cws', '2014-det',
     '2014-lad', '2014-sd', '2014-wsh', '2016-mia', '2017-stl', '2019-laa', '2020-nym', '2021-tor']
FILES = ['index.html', 'tests/fixtures/page_code.json', 'engine/share_live.mjs'] + [f'o/{w}.html' for w in W] + [f'og/o/{w}.png' for w in W]
out = sys.argv[1] if len(sys.argv) > 1 else 'rollback_r54'
for f in FILES:
    b = urllib.request.urlopen(BASE + f, timeout=60).read()
    os.makedirs(os.path.join(out, os.path.dirname(f)), exist_ok=True)
    open(os.path.join(out, f), 'wb').write(b)
os.makedirs(os.path.join(out, 'corrections'), exist_ok=True)
open(os.path.join(out, 'corrections/2026-11-14.html'), 'w').write('<!doctype html><meta charset="utf-8"><title>Corrections, Nov 14 2026</title><p>Withdrawn: the Nov 14 under-review labels were rolled back. See <a href="/corrections/2026-11-12.html">Nov 12</a>.</p>\n')
m = hashlib.md5(open(os.path.join(out, 'index.html'), 'rb').read()).hexdigest()
print('files', len(FILES) + 1, 'index md5', m, 'OK' if m == 'c3e08d1c55faed0aac0c37bff63e024c' else 'MISMATCH')
sys.exit(0 if m == 'c3e08d1c55faed0aac0c37bff63e024c' else 1)
