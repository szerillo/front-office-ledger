import json, math, sys
sys.path.insert(0,'/work')
import asset_rules as AR
CB=json.load(open('/work/contract_book.json')); SV=json.load(open('/work/service.json'))
EE={(e['pid'],e['s']):e for e in json.load(open('/work/ext_eval.json'))}
RATE=json.load(open('/work/ext_class_rate.json'))['cls']
CB_DPW={int(k):v for k,v in CB['dpw'].items()}; LMIN=CB.get('league_min',0.75)
def wins_of(m,y): return max(0.0,m-LMIN)/CB_DPW.get(y,AR.dpw(y))
def true_end(pid):
    s=SV.get(str(pid))
    if not s: return None, None
    by={int(k):v for k,v in s['by'].items()}; tot=0
    # a season he played that service.json lacks (deGrom 2017) would push the end a year late: no answer
    _rec = AR._lvm().get(int(pid)); _pl = {r[0] for r in (_rec or {}).get('rows', [])}
    if by and any(min(by) < y < max(by) and y not in by for y in _pl): return None, None
    for y in sorted(by):
        tot+=by[y]
        if tot>=1032: return y, len(s.get('arb_winters',[]))==4
    left=1032-tot; last=max(by) if by else 2026
    return last+math.ceil(left/172), len(s.get('arb_winters',[]))==4
def grade(c, ce):
    held=[h for h in c.get('held',[]) if h[1]<=2026]
    pid=int(c['pid']); raw=0; cst={}; kof={}
    for k,y,w,sh in held:
        kof[y]=k; ext_c=wins_of(AR.ext_salary(c,y),y)*sh
        if ce is not None and y<=ce:
            arb=AR.arb_salary_ce(pid,y,ce) if hasattr(AR,'arb_salary_ce') else None
            if arb is None:
                # arb path with this control end: last three control seasons
                if ce-2<=y<=ce:
                    w_=AR.season_war(pid); basis=max(w_.get(y-1,0),0.5*(w_.get(y-1,0)+w_.get(y-2,0)),0)
                    arb=max(0.75,(0.6+basis)*{1:1.0,2:1.5,3:3.1}[y-ce+3]*AR.dpw(y)/9.7)
                else: arb=LMIN
            raw+=(wins_of(arb,y)-ext_c)*AR.money_unit(y)
        else:
            kk=y-ce if ce is not None else k
            raw+=w-ext_c*AR.typical_fa(kk,y,c.get('band'))
        cst[y]=cst.get(y,0)+ext_c
    return raw, cst
rows=[]; cov=0; s2=0
exts=[c for c in CB['book'] if c['kind']=='ext']
for c in exts:
    pid=c['pid']; te,sup=true_end(pid)
    if te is None: continue
    cov+=1; s2+=bool(sup)
    ee=AR.control_end(pid)
    held=[h[1] for h in c.get('held',[]) if h[1]<=2026]
    if ee is None or te==ee or not held: continue
    span=set(range(min(te,ee)+1, max(te,ee)+1))
    if not (span & set(held)): continue
    e=EE.get((str(pid),c['sign']))
    r_old,cst=grade(c,ee); r_new,_=grade(c,te)
    exp=sum(RATE.get(e['cls'] if e else 'veteran',0)*v for v in cst.values()) if e else 0
    rows.append((c['name'],c['club'],c['sign'],c['yrs'],c['tot'],ee,te,sup, e['net'] if e else None, round(r_old-exp,1), round(r_new-exp,1)))
print('extensions',len(exts),'covered by service data',cov,'Super Two among covered',s2,'grades changed',len(rows))
for r in sorted(rows,key=lambda r:-abs(r[10]-r[9])): print(r)

print('\n--- Olson by hand ---')
c=[c for c in CB['book'] if c['kind']=='ext' and c['name']=='Matt Olson'][0]
pid=c['pid']
for k,y,w,sh in [h for h in c['held'] if h[1]<=2026]:
    ext_m=AR.ext_salary(c,y); ext_c=wins_of(ext_m,y)*sh
    w_=AR.season_war(pid); basis=max(w_.get(y-1,0),0.5*(w_.get(y-1,0)+w_.get(y-2,0)),0)
    arb23=max(0.75,(0.6+basis)*{1:1.0,2:1.5,3:3.1}[y-2023+3]*AR.dpw(y)/9.7) if 2021<=y<=2023 else None
    print(y, 'LedgerWAR %.2f'%w, 'ext salary $%.1fM = %.2f wins'%(ext_m,ext_c), 'money_unit %.2f'%AR.money_unit(y),
          'typFA(old k=%d) %.2f'%(y-2022, AR.typical_fa(y-2022,y,c.get('band'))) if y>2022 else '',
          ('arb path $%.1fM = %.2f wins'%(arb23, wins_of(arb23,y))) if arb23 else '')
e=EE[(str(pid),c['sign'])]; print('class',e['cls'],'rate',RATE[e['cls']],'cost',e['cost'],'expected',round(RATE[e['cls']]*e['cost'],2),'net',e['net'])

def parts(c, ce):
    out=[]
    for k,y,w,sh in [h for h in c['held'] if h[1]<=2026]:
        ext_c=wins_of(AR.ext_salary(c,y),y)*sh
        if y<=ce:
            w_=AR.season_war(c['pid']); basis=max(w_.get(y-1,0),0.5*(w_.get(y-1,0)+w_.get(y-2,0)),0)
            arb=max(0.75,(0.6+basis)*{1:1.0,2:1.5,3:3.1}[y-ce+3]*AR.dpw(y)/9.7) if ce-2<=y<=ce else LMIN
            out.append((y,'controlled','arb $%.1fM'%arb, round((wins_of(arb,y)-ext_c)*AR.money_unit(y),2)))
        else:
            t=AR.typical_fa(y-ce,y,c.get('band')); out.append((y,'free agent','prod %.2f - %.2f x %.2f'%(w,ext_c,t), round(w-ext_c*t,2)))
    return out
for ce in (2022,2023):
    p=parts(c,ce); print('ce',ce, p, 'raw', round(sum(x[3] for x in p),2), 'net', round(sum(x[3] for x in p)-4.02,2))
