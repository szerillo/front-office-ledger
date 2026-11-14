#!/usr/bin/env python3
# Round 56 one-command rollback: python3 rollback_r56.py <out dir>
# Fetches the pre-deploy version (commit 8eb5b40) of every file the round 56 deploy changed (changed_files.txt, next to
# this script), checks the index md5, and writes them into <out dir> with their repo paths, ready for the GitHub web
# upload folder by folder. Files that did not exist before (og/t/clubs-manifest.json) are left in
# place: nothing links to them once index.html is rolled back.
import sys, os, hashlib, urllib.request, urllib.error
BASE = 'https://raw.githubusercontent.com/szerillo/front-office-ledger/8eb5b40/'
here = os.path.dirname(os.path.abspath(__file__))
FILES = [l.strip() for l in open(os.path.join(here, 'changed_files.txt')) if l.strip()]
out = sys.argv[1] if len(sys.argv) > 1 else 'rollback_r56'
n = skipped = 0
for f in FILES:
    try: b = urllib.request.urlopen(BASE + f, timeout=60).read()
    except urllib.error.HTTPError as e:
        if e.code == 404: skipped += 1; continue
        raise
    os.makedirs(os.path.join(out, os.path.dirname(f)), exist_ok=True)
    open(os.path.join(out, f), 'wb').write(b); n += 1
m = hashlib.md5(open(os.path.join(out, 'index.html'), 'rb').read()).hexdigest()
WANT = '0aa79edec616aa9854039c62ae68fc3e'
print('files', n, 'new files left in place', skipped, 'index md5', m, 'OK' if m == WANT else 'MISMATCH')
sys.exit(0 if m == WANT else 1)
