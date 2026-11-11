"""Rank grade changes from control_end_impact.py output (/tmp/ce_old.json, /tmp/ce_new.json) plus the
extension rows of control_end_check.py (/tmp/ext_rows.txt), and club rank shifts. See docs/audit-nov11-c.md."""
import json, ast
from collections import defaultdict
o=json.load(open('/tmp/ce_old.json')); n=json.load(open('/tmp/ce_new.json'))
tb=json.load(open('/work/trade_book.json')); T=tb['trades']; NM=tb['names']
seat=defaultdict(float); who=defaultdict(list)
for a,b in zip(o['rows'],n['rows']):
    i,d,ab,giver,pid,v,old=a; new=b[6]; dl=new-old
    if abs(dl)<0.05: continue
    seat[(i,ab)]+=dl; who[(i,ab)].append((pid,dl))
    if giver: seat[(i,giver)]-=dl; who[(i,giver)].append((pid,-dl))
rows=[]
for (i,ab),dl in seat.items():
    d,seats=T[i]; net=next(s[1] for s in seats if s[0]==ab)
    ps=', '.join(f"{NM.get(p,p)} {x:+.1f}" for p,x in who[(i,ab)])
    other='/'.join(s[0] for s in seats if s[0]!=ab)
    rows.append(('trade',ab,d,f"trade with {other} ({ps})",net,round(net+dl,1),dl))
for l in open('/tmp/ext_rows.txt'):
    r=ast.literal_eval(l.strip())
    rows.append(('extension',r[1],r[2],f"{r[0]} {r[3]}y/${r[4]}M, control end {r[5]} to {r[6]}",r[9],r[10],r[10]-r[9]))
rows.sort(key=lambda r:-abs(r[6]))
print('trade seats moved >=0.05:',sum(1 for r in rows if r[0]=='trade'),' extensions moved:',sum(1 for r in rows if r[0]=='extension' and abs(r[6])>=0.05))
for k,r in enumerate(rows[:25],1): print(k, r[0], r[1], r[2], r[3], f"{r[4]:+.1f} -> {r[5]:+.1f} ({r[6]:+.1f})")
json.dump(rows,open('/tmp/movers.json','w'))
# club totals: every trade seat net + every extension net
EE=json.load(open('/work/ext_eval.json'))
tot=defaultdict(float)
for d,seats in T:
    for s in seats: tot[s[0]]+=s[1]
for e in EE:
    if e.get('ab') and e.get('net') is not None: tot[e['ab']]+=e['net']
new=dict(tot)
for r in rows: new[r[1]]+=r[6]
rk=lambda t:{c:i+1 for i,(c,_) in enumerate(sorted(t.items(),key=lambda x:-x[1]))}
a,b=rk(tot),rk(new)
print('\nclub rank changes (trades + extensions, all time):')
for c in sorted(a,key=lambda c:a[c]):
    if a[c]!=b[c]: print(c, a[c],'->',b[c], f"{tot[c]:+.1f} -> {new[c]:+.1f}")
print('clubs total delta:', {c:round(new[c]-tot[c],1) for c in sorted(tot, key=lambda c:-abs(new[c]-tot[c]))[:8]})
