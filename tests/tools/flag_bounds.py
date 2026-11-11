"""Round 16: bounds on trade-side moves if the flagged salary rows in the $0 population are wrong. Lower: each set to
$0 charge; upper: each set to the player's prior-season salary. Shadow only. Restores salary_overrides.csv."""
import runpy,io,contextlib,shutil,csv,json,sys
fx='tests/fixtures/salary_overrides.csv'; base=open(fx).read()
rows={}
for f in ['tests/fixtures/zero_br_2026-11-11.txt','tests/fixtures/zero_br_rand40_2026-11-11.txt','tests/fixtures/arb_br_2026-11-11.txt']:
  for l in open(f):
    p,r=l.strip().split('#')
    for a in r.split(','):
      if a: y,k=a.split(':')[:2]; rows.setdefault((int(p),int(y)),[]).append(int(k)/1000)
seas=[(430832,2018),(453281,2018),(453281,2020),(455119,2022),(455755,2018),(506702,2020),(592192,2025)]
def run(extra):
  open(fx,'w').write(base+''.join(f'{p},{y},{v},bound test,x\n' for (p,y),v in extra.items()))
  with contextlib.redirect_stdout(io.StringIO()): G=(sys.argv.__setitem__(slice(None),['x','/tmp/zbr_all.txt']), runpy.run_path('tests/tools/zero_salary_shadow.py'))[1]
  open(fx,'w').write(base); return G['delta'],G['nets']
d0,n=run({})
up={s:max(rows.get((s[0],s[1]-1),[0])+rows[s]) for s in seas}
lo={s:0.0 for s in seas}
for nm,ex in (('upper',up),('lower',lo)):
  d,_=run(ex); keys=set(d)|set(d0)
  mv=[(k,round(d.get(k,0)-d0.get(k,0),2)) for k in keys if abs(d.get(k,0)-d0.get(k,0))>=0.5]
  fl=[k for k in keys if (n[k]+d0.get(k,0)>0)!=(n[k]+d.get(k,0)>0)]
  print(nm,'sides moving 0.5+',len(mv),sorted(mv,key=lambda x:-abs(x[1]))[:8],'flips vs current',len(fl))
print('upper values',up)
