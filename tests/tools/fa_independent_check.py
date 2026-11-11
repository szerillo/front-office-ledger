# Independent recompute of every graded FA row (realized from lvm_cache by club name, expected from terms).
# Own code; shares inputs with the engine (lvm_cache.json, contract_book.json shares and owned seasons). Round 20 repost.
# Independent recompute of graded FA rows: realized from lvm_cache rows by club name (own code),
# expected from terms with the documented formula; compared to the live allx_fa values.
import json, collections
L={k:v for k,v in json.load(open('/work/lvm_cache.json')).items() if not k.startswith('__')}
CB=json.load(open('/work/contract_book.json'))
NAMES={'ARI':['Arizona Diamondbacks'],'ATL':['Atlanta Braves'],'BAL':['Baltimore Orioles'],'BOS':['Boston Red Sox'],
'CHC':['Chicago Cubs'],'CWS':['Chicago White Sox'],'CIN':['Cincinnati Reds'],'CLE':['Cleveland Indians','Cleveland Guardians'],
'COL':['Colorado Rockies'],'DET':['Detroit Tigers'],'HOU':['Houston Astros'],'KC':['Kansas City Royals'],
'LAA':['Anaheim Angels','Los Angeles Angels of Anaheim','Los Angeles Angels','California Angels'],'LAD':['Los Angeles Dodgers'],
'MIA':['Florida Marlins','Miami Marlins'],'MIL':['Milwaukee Brewers'],'MIN':['Minnesota Twins'],'NYM':['New York Mets'],
'NYY':['New York Yankees'],'ATH':['Oakland Athletics','Athletics','Sacramento Athletics'],'PHI':['Philadelphia Phillies'],
'PIT':['Pittsburgh Pirates'],'SD':['San Diego Padres'],'SF':['San Francisco Giants'],'SEA':['Seattle Mariners'],
'STL':['St. Louis Cardinals'],'TB':['Tampa Bay Devil Rays','Tampa Bay Rays'],'TEX':['Texas Rangers'],
'TOR':['Toronto Blue Jays'],'WSH':['Montreal Expos','Washington Nationals']}
allnames={r[1] for v in L.values() for r in v['rows']}
unk=allnames-{n for v in NAMES.values() for n in v}
print('LVM team names not mapped:',sorted(unk)[:20])
DPW={int(k):v for k,v in CB['dpw'].items()}; TYP={int(k):v for k,v in CB['typical_fa'].items()}
ERA=CB.get('era_adj_pre2006',1.0); LMIN=CB.get('league_min',0.75); BAND={int(k):v for k,v in CB.get('band_mult',{}).items()}
def typ(k,y,b): return TYP.get(min(k,5),CB['typical_fa_all'])*(ERA if y<2006 else 1)*BAND.get(b,1.0)
POSTING_FEE = {   # (player id, signing club) -> fee $M
    (493137, "BOS"): 51.11,  # Daisuke Matsuzaka, Dec 2006
    (506432, "NYY"): 26.0,   # Kei Igawa, Dec 2006
    (506433, "TEX"): 51.7,   # Yu Darvish, Jan 2012
    (547888, "NYY"): 20.0,   # Masahiro Tanaka, Jan 2014
    (547943, "LAD"): 25.7,   # Hyun Jin Ryu, Dec 2012
    (628317, "LAD"): 20.0,   # Kenta Maeda, Jan 2016
    (660271, "LAA"): 20.0,   # Shohei Ohtani, Dec 2017 (signing as an international pro: IFA channel)
    (579328, "SEA"): 10.275, # Yusei Kikuchi, Jan 2019
    (673548, "CHC"): 14.6,   # Seiya Suzuki, Mar 2022
    (807799, "BOS"): 15.4,   # Masataka Yoshida, Dec 2022
    (808967, "LAD"): 50.6,   # Yoshinobu Yamamoto, Dec 2023
    (684007, "CHC"): 9.825,  # Shota Imanaga, Jan 2024
    (808982, "SF"): 18.825, # Jung Hoo Lee, Dec 2023
    (673490, "SD"): 5.3,    # Ha-Seong Kim, Jan 2021
    (628356, "PIT"): 5.0,    # Jung Ho Kang, Jan 2015
    (457292, "MIN"): 5.33,   # Tsuyoshi Nishioka, Dec 2010
}
W=json.load(open('/work/sweep_results.json'))+json.load(open('/work/hist_results.json'))
graded={}
for r in W:
    for x in (r.get('allx_fa') or []):
        if x[2] is not None and x[4] is not None: graded[(x[7],r['abbr'],x[0])]=x
BOOK=collections.defaultdict(list)
for c in CB['book']:
    if c['kind']=='fa': BOOK[(str(c['pid']),c['club'])].append(c)
res=collections.Counter(); diffs=[]
for (pid,ab,d),x in graded.items():
    cs=[c for c in BOOK[(pid,ab)] if c['yrs']==x[2] and abs(c['tot']-x[3])<0.06]
    if len(cs)>1:
        y,mo=int(d[:4]),int(d[5:7]); st=y+1 if mo>=10 else y
        cs=[c for c in cs if c['start']==st]
    if len(cs)!=1: res['contract not uniquely matched']+=1; continue
    c=cs[0]; held=[h for h in c.get('held',[]) if h[1]<=2026]
    # my realized: LVM rows on the club in contract seasons
    rows=L.get(pid,{}).get('rows',[])
    seasons=c.get('own') or list(range(c['start'],c['start']+c['yrs']))
    my_real=sum(v for y,t,v in rows if y in seasons and y<=2026 and t in NAMES[ab])
    shares={h[1]:h[3] for h in held}
    my_exp=sum(max(0,c['aav']-LMIN)/DPW.get(h[1],9.7)*h[3]*typ(h[0],h[1],c.get('band')) for h in held)
    fee=POSTING_FEE.get((int(pid),ab),0.0)
    if fee and held: my_exp+=fee/DPW.get(held[0][1],9.7)*typ(1,held[0][1],c.get('band'))
    live_real,live_exp,live_net=x[4],x[5],x[6]
    qo = round(live_exp-my_exp,1)
    ok_r=abs(round(my_real,1)-live_real)<=0.15
    ok_e=abs(my_exp-live_exp)<=0.06 or abs(my_exp+1.0-live_exp)<=0.06
    res['realized agrees' if ok_r else 'realized differs']+=1
    res['expected agrees (or +1 QO)' if ok_e else 'expected differs']+=1
    if not ok_r or not ok_e: diffs.append((ab,d,x[1],round(my_real,2),live_real,round(my_exp,2),live_exp))
print(len(graded),'graded FA rows'); print(dict(res))
diffs.sort(key=lambda t:-abs(t[3]-t[4]))
for t in diffs[:15]: print(t)
json.dump({'counts':dict(res),'diffs':diffs},open('indep3_results.json','w'),indent=1,ensure_ascii=False)
