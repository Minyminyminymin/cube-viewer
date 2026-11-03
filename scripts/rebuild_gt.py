"""Rebuild the summer ground-truth cube for the 8 named participants, fit each rotating trial's start angle,
validate against the logged DistanceToCurve, and save every sample with its nearest edge point.
Geometry (summer README + CubeCalibrator.cs): center (0,1,0.65), edge 0.3*0.8 = 0.24 m, traced polyline
0-1-2-3-0-4-5-6-7-4 (front face z=-h, back face z=+h), rotation about world z at 30 deg/s."""
import sys, re, glob, os, numpy as np, pandas as pd
DATA=sys.argv[1]; OUT=sys.argv[2]
C=np.array([0,1,0.65]); h=0.12
V=np.array([[-h,-h,-h],[h,-h,-h],[h,h,-h],[-h,h,-h],[-h,-h,h],[h,-h,h],[h,h,h],[-h,h,h]])
ORDER=[0,1,2,3,0,4,5,6,7,4]; A=V[ORDER[:-1]]; B=V[ORDER[1:]]   # 9 segments, local frame
PIDS='AA|AZ|EC|EM|IL|JP|MM|ZZ'
def nearest_local(Q):
    """Q: (n,3) points in the cube's local frame -> distance, nearest point, segment index (0..8)."""
    d=B-A; L2=(d**2).sum(1)
    t=np.clip(((Q[:,None,:]-A[None])*d[None]).sum(2)/L2,0,1)
    P=A[None]+t[...,None]*d[None]; D=np.linalg.norm(Q[:,None,:]-P,axis=2)
    k=D.argmin(1); i=np.arange(len(Q))
    return D[i,k],P[i,k],k
def to_local(W,ang):
    X=W-C; c,s=np.cos(-ang),np.sin(-ang)   # undo rotation about z
    return np.c_[c*X[:,0]-s*X[:,1], s*X[:,0]+c*X[:,1], X[:,2]]
def fit_phase(W,T,logd,sign):
    sub=np.arange(len(W))
    def cost(ph): return np.median(np.abs(nearest_local(to_local(W[sub],np.radians(ph+sign*30*T[sub])))[0]-logd[sub]))
    grid=np.arange(0,360,2.0); c=[cost(p) for p in grid]; p0=grid[int(np.argmin(c))]
    fine=np.arange(p0-2,p0+2,0.05); c2=[cost(p) for p in fine]; return fine[int(np.argmin(c2))],min(c2)
rows=[]; files=sorted(f for f in glob.glob(os.path.join(DATA,'RotatingTrace_Calib_*.csv')) if re.search(rf'Calib_+({PIDS})_2026(06|07|08)\d\d',os.path.basename(f)))
for f in files:
    b=os.path.basename(f); m=re.search(rf'Calib_+({PIDS})_(\d{{8}})_(?:S(\d+))?',b)
    d=pd.read_csv(f); d=d[d.TrialType.isin(['cube_static','cube_rotating'])].dropna(subset=['DistanceToCurve'])
    for (ty,ti),g in d.groupby(['TrialType','TrialIndex']):
        W=g[['WorldX','WorldY','WorldZ']].values; T=(g.TimeStamp-g.TimeStamp.iloc[0]).values; logd=g.DistanceToCurve.values
        if ty=='cube_rotating':
            best=min((fit_phase(W,T,logd,s)+(s,) for s in (1,)),key=lambda r:r[1]); ph,_,sg=best
            ang=np.radians(ph+sg*30*T)
        else: ph,sg,ang=0.0,0,np.zeros(len(T))
        Q=to_local(W,ang); dist,P,k=nearest_local(Q)
        rows.append(pd.DataFrame(dict(file=b,pid=m.group(1),date=m.group(2),snum=int(m.group(3) or 1),type=ty,trial=int(ti)+1,t=T,
            hx=Q[:,0],hy=Q[:,1],hz=Q[:,2],gx=P[:,0],gy=P[:,1],gz=P[:,2],seg=k+1,dist=dist,logged=logd,phase=ph,sign=sg)))
    print(b,flush=True)
S=pd.concat(rows,ignore_index=True)
ss=S[['pid','date','snum']].drop_duplicates().sort_values(['pid','date','snum']); ss['session']=ss.groupby('pid').cumcount()+1
S=S.merge(ss,on=['pid','date','snum'])
S['off']=(S.dist-S.logged).abs()>0.001
bad=S.groupby(['file','type','trial']).off.mean().pipe(lambda x:x[x>0.01])
print('median |diff| mm',(S.dist-S.logged).abs().median()*1000); print('excluded:',bad.round(3).to_string())
S=S[~S.set_index(['file','type','trial']).index.isin(bad.index)]
print('trials',S.groupby(['pid','type','session','trial']).ngroups, S.groupby('type').apply(lambda x:x.groupby(['pid','session','trial']).ngroups).to_dict())
S.drop(columns=['off']).to_parquet(OUT) if False else S.drop(columns=['off']).to_csv(OUT,index=False,compression='gzip')
