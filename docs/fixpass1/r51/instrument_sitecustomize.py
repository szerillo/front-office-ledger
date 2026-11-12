# Round 51 instrumentation (wraps the round-0 sandbox guard). For each engine step it logs, to $INST_LOG/<step>.json:
#  - every file read and its md5 at first read (the step's inputs),
#  - at exit, every global of the step's module and of each engine module it imported: kind, size, value hash,
#    and whether it looks like a fitted quantity (a number, or a small container of numbers),
#  - every statistics/numpy estimator call: call site, input hash, output hash.
import sys, os, json, hashlib, atexit, builtins
exec(open('/tmp/sbx/guard/sitecustomize.py').read())
_DIR = os.environ.get('INST_LOG'); _STEP = os.path.basename(sys.argv[0]) if sys.argv and sys.argv[0] else '?'
_reads, _calls = {}, []
def _md5f(p):
    try:
        h = hashlib.md5()
        with builtins.__dict__['_inst_open0'](p, 'rb') as f:
            for b in iter(lambda: f.read(1 << 20), b''): h.update(b)
        return h.hexdigest()[:12]
    except Exception: return None
builtins._inst_open0 = builtins.open
def _open(file, mode='r', *a, **k):
    try:
        if isinstance(file, (str, bytes, os.PathLike)) and not any(c in mode for c in 'wax+'):
            p = os.path.abspath(os.fsdecode(file))
            if p.startswith('/work/') and p not in _reads: _reads[p] = _md5f(p)
    except Exception: pass
    return builtins._inst_open0(file, mode, *a, **k)
builtins.open = _open
def _h(x):
    try: s = json.dumps(x, sort_keys=True, default=str)
    except Exception: s = repr(x)
    return hashlib.md5(s.encode()).hexdigest()[:12]
def _numeric(x, depth=0):
    if isinstance(x, bool): return False
    if isinstance(x, (int, float)): return True
    if depth > 3: return False
    if isinstance(x, dict): return 0 < len(x) <= 500 and all(_numeric(v, depth + 1) for v in x.values())
    if isinstance(x, (list, tuple)): return 0 < len(x) <= 500 and all(_numeric(v, depth + 1) for v in x)
    return False
def _wrap(mod, name):
    f = getattr(mod, name, None)
    if not callable(f): return
    def w(*a, **k):
        r = f(*a, **k)
        try:
            fr = sys._getframe(1); site = f'{os.path.basename(fr.f_code.co_filename)}:{fr.f_lineno}'
            if site.split(':')[0] in _ENG or fr.f_code.co_filename.startswith('/work/'):
                _calls.append([site, f'{mod.__name__}.{name}', _h([a, k]), _h(r)])
        except Exception: pass
        return r
    setattr(mod, name, w)
import statistics
for _n in ('mean', 'fmean', 'median', 'pstdev', 'stdev', 'pvariance', 'variance', 'quantiles', 'linear_regression', 'correlation'): _wrap(statistics, _n)
try:
    import numpy as _np
    for _n in ('mean', 'median', 'std', 'var', 'polyfit', 'percentile', 'quantile', 'average', 'corrcoef'): _wrap(_np, _n)
    _wrap(_np.linalg, 'lstsq')
except Exception: pass
_ENG = {f for f in os.listdir('/work') if f.endswith('.py')} if os.path.isdir('/work') else set()
@atexit.register
def _dump():
    if not _DIR: return
    mods = {'__main__': sys.modules.get('__main__')}
    for n, m in list(sys.modules.items()):
        fp = getattr(m, '__file__', '') or ''
        if fp.startswith('/work/') and fp.endswith('.py'): mods[n] = m
    G = {}
    for mn, m in mods.items():
        for k, v in list(vars(m).items()):
            if k.startswith('__') or callable(v) or type(v).__name__ == 'module': continue
            try: size = len(v)
            except Exception: size = None
            G[f'{mn}.{k}'] = [type(v).__name__, size, _h(v), _numeric(v)]
    os.makedirs(_DIR, exist_ok=True)
    with builtins._inst_open0(os.path.join(_DIR, _STEP + '.json'), 'w') as f:
        json.dump({'step': _STEP, 'reads': _reads, 'globals': G, 'calls': _calls}, f)
