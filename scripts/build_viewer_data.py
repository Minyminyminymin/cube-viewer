"""Rebuild the trajectory viewer's embedded DATA from samples.csv.gz (all 558 trials, full-sample angle fit).
Points: every ceil(n/600)-th sample (x/y/z/d in mm, cube frame; t in 1/100 s). Edge stats and means use all samples."""
import json, math, sys, numpy as np, pandas as pd
S=pd.read_csv(sys.argv[1]).sort_values(['pid','type','session','trial','t'])
def trial(g):
    n=len(g); q=g.iloc[::math.ceil(n/600)]; dm=g.dist*1000; E=[]
    for e in range(1,10):
        v=dm[g.seg==e]
        E.append(dict(e=e,n=int(len(v)),pct=round(len(v)/n*100,1),**({k:round(float(f(v)),1) for k,f in [('mean',np.mean),('med',np.median),('p95',lambda x:np.percentile(x,95))]} if len(v) else dict(mean=None,med=None,p95=None))))
    r=lambda c:(q[c]*1000).round().astype(int).tolist()
    return dict(i=int(g.trial.iloc[0]),x=r('hx'),y=r('hy'),z=r('hz'),d=r('dist'),s=q.seg.astype(int).tolist(),t=(q.t*100).round().astype(int).tolist(),
                mean=round(float(dm.mean()),1),dur=round(float(g.t.max()),1),edges=E)
D={}
for (p,ty,s),g in S.groupby(['pid','type','session']):
    tr=[trial(x) for _,x in g.groupby('trial')]
    D.setdefault(p,{}).setdefault(ty,[]).append(dict(s=int(s),date=str(g.date.iloc[0]),file=g.file.iloc[0],trials=tr,mean=round(float(np.mean([t['mean'] for t in tr])),1)))
json.dump(D,open(sys.argv[2],'w'),separators=(',',':'))
