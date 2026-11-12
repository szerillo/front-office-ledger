# Step 0 sandbox guard (prereg 3f0018a). Fail closed: any network use, or a write outside the sandbox, ends
# the process with exit 97 (os._exit, so a try/except in the script cannot swallow it). Logs every file opened.
import sys, os, json, time as _time, datetime as _dt
LOG = os.environ.get("GUARD_LOG", "/tmp/sbx/guard.log")
ALLOW_W = ("/work/", "/tmp/sbx/run/", "/tmp/sbx/runs/", "/tmp/chain.log", "/dev/null") + ((os.environ.get("GUARD_CACHE", "/tmp/sbx/frozen/http") + "/",) if os.environ.get("GUARD_MODE") == "record" else ())
DENY_R = ("/tmp/sbx/realwork",)
_seen = set()
def _log(kind, what):
    k = (kind, what)
    if k in _seen: return
    _seen.add(k)
    with open(LOG, "a") as f: f.write(json.dumps([kind, what, os.path.basename(sys.argv[0] if sys.argv else "")]) + "\n")
def _abort(msg):
    try: _log("ABORT", msg)
    except Exception: pass
    sys.stderr.write("GUARD ABORT: " + msg + "\n"); sys.stderr.flush(); os._exit(97)
def _hook(ev, args):
    if ev == "open":
        path, mode, flags = args[0], args[1], args[2]
        if isinstance(path, int) or path is None: return
        p = os.path.abspath(os.fsdecode(path))
        writing = (mode and any(c in mode for c in "wax+")) or (flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_APPEND))
        if p == LOG: return
        if p.startswith(DENY_R): _abort("touched the real /work copy: " + p)
        if writing:
            if not p.startswith(ALLOW_W): _abort("write outside sandbox: " + p)
            _log("write", p)
        else: _log("read", p)
    elif os.environ.get("GUARD_MODE") == "record" and ev in ("socket.connect", "socket.getaddrinfo", "socket.gethostbyname", "urllib.Request", "http.client.connect", "socket.sendto"):
        _log("net-record", f"{ev} {str(args[:2])[:100]}")
    elif ev in ("socket.connect", "socket.getaddrinfo", "socket.gethostbyname", "urllib.Request", "http.client.connect", "socket.sendto"):
        _abort(f"network: {ev} {args[:2]!r}")
    elif ev == "subprocess.Popen" and os.path.basename(str(args[0])) == "lscpu":
        _log("env", "lscpu (CPU count probe)")
    elif ev in ("subprocess.Popen", "os.system", "os.exec", "os.posix_spawn"):
        _abort(f"subprocess: {ev} {str(args)[:120]}")
    elif ev == "os.getenv" or ev == "os.putenv":
        _log("env", str(args[0]))
sys.addaudithook(_hook)
# frozen clock: time.time, datetime.now/today and date.today all fixed (time-machine patches at C level, so
# pandas keeps working; replacing the datetime classes crashed pandas' C extension)
import time_machine as _tm
CLOCK = os.environ.get("GUARD_CLOCK", "2026-11-11T12:00:00+00:00")
_trav = _tm.travel(_dt.datetime.fromisoformat(CLOCK), tick=False); _trav.start()
# environment reads through os.environ are logged too
class _Env(type(os.environ)):
    pass
_orig_get = os.environ.__class__.__getitem__
def _getitem(self, k):
    if not str(k).startswith(("GUARD_", "PYTHON", "PATH", "HOME", "LANG", "LC_", "TERM", "PWD")): _log("env", str(k))
    return _orig_get(self, k)
os.environ.__class__.__getitem__ = _getitem

# ---- frozen network cache: GUARD_MODE=record saves every response once; replay (default) serves only from it ----
import urllib.request as _ur, hashlib as _hl, io as _io
MODE = os.environ.get("GUARD_MODE", "replay")
CACHE = os.environ.get("GUARD_CACHE", "/tmp/sbx/frozen/http")
_real_urlopen = _ur.urlopen
class _Resp(_io.BytesIO):
    status = 200
    def getcode(self): return 200
    def __enter__(self): return self
    def __exit__(self, *a): self.close()
    headers = {}
def _key(req, data):
    url = req.full_url if hasattr(req, "full_url") else str(req)
    body = data if data is not None else getattr(req, "data", None)
    return url, _hl.sha256((url + "|" + repr(body)).encode()).hexdigest()
def _urlopen(req, data=None, timeout=None, *a, **k):
    url, h = _key(req, data)
    p = f"{CACHE}/{h}"
    if os.path.exists(p):
        _log("http-replay", url); return _Resp(open(p, "rb").read())
    syn = _synth_people(url)
    if syn is not None:
        _log("http-synth", url); return _Resp(syn)
    if MODE != "record": _abort("network (not in frozen cache): " + url)
    r = _real_urlopen(req, data, timeout, *a, **k) if timeout else _real_urlopen(req, data, *a, **k)
    body = r.read(); os.makedirs(CACHE, exist_ok=True)
    open(p, "wb").write(body); open(p + ".url", "w").write(url)
    _log("http-record", url); return _Resp(body)
_PEOPLE_IDX = {}
_PEOPLE_ASKED = {}
def _people_index(suffix):
    # per-player records from every recorded /people?personIds=... batch with this exact query suffix
    if suffix in _PEOPLE_IDX: return _PEOPLE_IDX[suffix], _PEOPLE_ASKED[suffix]
    idx, asked = {}, set()
    for f in os.listdir(CACHE):
        if not f.endswith(".url"): continue
        u = open(f"{CACHE}/{f}").read()
        if not u.startswith("https://statsapi.mlb.com/api/v1/people?personIds="): continue
        ids, _, suf = u[len("https://statsapi.mlb.com/api/v1/people?personIds="):].partition("&")
        if suf != suffix: continue
        asked |= set(ids.split(","))
        for x in json.loads(open(f"{CACHE}/{f[:-4]}", "rb").read()).get("people", []): idx[str(x["id"])] = x
    _PEOPLE_IDX[suffix], _PEOPLE_ASKED[suffix] = idx, asked
    return idx, asked
def _synth_people(url):
    # fix pass 1: a /people batch asked in a different order or grouping than it was recorded. Rebuilt from the
    # per-player records recorded with the same query; any player never asked in the record means a real miss.
    pre = "https://statsapi.mlb.com/api/v1/people?personIds="
    if not url.startswith(pre): return None
    ids, _, suf = url[len(pre):].partition("&")
    if not ids or not all(c.isdigit() or c == "," for c in ids): return None
    idx, asked = _people_index(suf)
    want = ids.split(",")
    if not all(i in asked for i in want): return None
    return json.dumps({"people": [idx[i] for i in want if i in idx]}).encode()
_ur.urlopen = _urlopen

# R6: reverse the order of every unordered SELECT on every connection
if os.environ.get("GUARD_REVERSE") == "1":
    import sqlite3 as _sq
    _real_connect = _sq.connect
    def _connect(*a, **k):
        c = _real_connect(*a, **k); c.execute("PRAGMA reverse_unordered_selects=ON"); _log("sqlite", "reverse_unordered_selects ON"); return c
    _sq.connect = _connect
