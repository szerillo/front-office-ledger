# Nov 12 headroom check: red (exit 3) when any file the deploy will upload is over 3.4 MB (the Chrome upload tool
# takes 3.6 MB a file). Usage: size_check.py <site dir> [live dir]. With a live dir, files byte-identical to live
# are not uploaded and so are not checked (they are listed as info). Without one, every file is checked.
import os, sys, hashlib, filecmp
LIMIT = int(os.environ.get('SIZE_LIMIT', 3400000)); d = sys.argv[1]; live = sys.argv[2] if len(sys.argv) > 2 else None
big, info = [], []
for root, dirs, files in os.walk(d):
    dirs[:] = [x for x in dirs if x not in ('.git', 'node_modules')]
    for f in files:
        p = os.path.join(root, f); rel = os.path.relpath(p, d); n = os.path.getsize(p)
        if n <= LIMIT: continue
        lp = os.path.join(live, rel) if live else None
        (info if lp and os.path.isfile(lp) and filecmp.cmp(p, lp, shallow=False) else big).append((rel, n))
if info: print('not uploaded (same as live):', ', '.join(f'{f} {n:,}' for f, n in info))
if big: print('SIZE CHECK RED:', ', '.join(f'{f} {n:,} bytes' for f, n in big)); sys.exit(3)
print('size check green, limit', f'{LIMIT:,}')
