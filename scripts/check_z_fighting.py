#!/usr/bin/env python3
"""Detect overlapping, nearly parallel transformed cube faces. Numeric linear tracks only.
Same-facing overlaps are risk candidates, not proof of visible flicker. Opposing
faces are counted separately as potential internal contacts; no occlusion proof.
"""
import argparse,json,math
from pathlib import Path
import numpy as np
from scipy.spatial.transform import Rotation as R
FACES={'north':[0,1,2,3],'south':[5,4,7,6],'east':[1,5,6,2],'west':[4,0,3,7],'up':[4,5,1,0],'down':[3,2,6,7]}
NAMES=list(FACES)
def corners(e):
 x,y,z=e['from'];X,Y,Z=e['to'];return np.array([[x,Y,z],[X,Y,z],[X,y,z],[x,y,z],[x,Y,Z],[X,Y,Z],[X,y,Z],[x,y,Z]],float)
def area(p):
 if len(p)<3:return 0.
 p=np.asarray(p);return abs(np.sum(p[:,0]*np.roll(p[:,1],-1)-p[:,1]*np.roll(p[:,0],-1)))/2
def signed(p):return np.sum(p[:,0]*np.roll(p[:,1],-1)-p[:,1]*np.roll(p[:,0],-1))
def cross(a,b):return a[0]*b[1]-a[1]*b[0]
def overlap(a,b,n):
 u=a[1]-a[0];u/=np.linalg.norm(u);v=np.cross(n,u);v/=np.linalg.norm(v);basis=np.stack([u,v],axis=1)
 a=a@basis;b=b@basis # caller supplies vertices relative to a common origin
 if signed(b)<0:b=b[::-1]
 p=list(a)
 for x,y in zip(b,np.roll(b,-1,axis=0)):
  if not p:break
  q=[];d=y-x;prev=p[-1];pv=cross(d,prev-x)
  for cur in p:
   cv=cross(d,cur-x)
   if (pv>=-1e-9)!=(cv>=-1e-9):q.append(prev+(cur-prev)*(pv/(pv-cv)))
   if cv>=-1e-9:q.append(cur)
   prev=cur;pv=cv
  p=q
 return area(p)
class Scene:
 def __init__(self,m):
  self.m=m;self.e=[e for e in m['elements'] if e.get('type','cube')=='cube'];self.g={};self.parent={};self.owner={};self.unsupported=[e.get('name','unnamed')+': non-cube geometry unsupported' for e in m['elements'] if e.get('type','cube')!='cube']
  def walk(g,p=None):
   if isinstance(g,str):
    if g in self.owner:self.unsupported.append('Duplicate outliner reference: '+g)
    self.owner[g]=p;return
   u=g['uuid'];self.g[u]=g;self.parent[u]=p
   for c in g.get('children',[]):walk(c,u)
  for g in m['outliner']:walk(g)
  self.owners=[self.owner.get(e['uuid']) for e in self.e];self.local=[];self.track={}
  for e in self.e:
   if e['uuid'] not in self.owner:self.unsupported.append(e['name']+': missing outliner reference')
  for e in self.e:
   o=np.asarray(e.get('origin',[0,0,0]));p=corners(e);self.local.append(R.from_euler('xyz',e.get('rotation',[0,0,0]),degrees=True).apply(p-o)+o)
   if e.get('inflate',0) or e.get('rescale',False):self.unsupported.append(e['name']+': inflate/rescale unsupported')
  self.local=np.array(self.local);self.ci=[];self.fi=[]
  for i,e in enumerate(self.e):
   for j,f in enumerate(NAMES):
    if e.get('faces',{}).get(f,{}).get('texture') is not None:self.ci.append(i);self.fi.append(j)
  self.ci=np.array(self.ci);self.fi=np.array(self.fi);self.idx=np.array(list(FACES.values()))[self.fi];self.ii,self.jj=np.triu_indices(len(self.ci),1);sel=self.ci[self.ii]!=self.ci[self.jj];self.ii=self.ii[sel];self.jj=self.jj[sel]
  for a in m.get('animations',[]):
   for u,tr in a.get('animators',{}).items():
    if u not in self.g:continue
    for c in ['position','rotation','scale']:
     ks=sorted([k for k in tr.get('keyframes',[]) if k['channel']==c],key=lambda k:k['time'])
     if not ks:continue
     try:
      if any(k.get('interpolation','linear')!='linear' or len(k['data_points'])!=1 for k in ks):raise ValueError('nonlinear')
      self.track[(a['uuid'],u,c)]=(np.array([k['time'] for k in ks]),np.array([[float(k['data_points'][0][ax]) for ax in 'xyz'] for k in ks]))
     except (ValueError,KeyError,TypeError):self.unsupported.append(f"{a['name']}/{tr.get('name',u)}/{c}: unsupported track")
 def matrices(self,a=None,t=0):
  mats={None:(np.eye(3),np.zeros(3))}
  def value(u,c,default):
   tr=self.track.get((a['uuid'],u,c)) if a else None
   return np.array([np.interp(t,tr[0],tr[1][:,i]) for i in range(3)]) if tr else np.asarray(default,float)
  for u,g in self.g.items():
   o=np.asarray(g['origin']);r=R.from_euler('xyz',np.asarray(g.get('rotation',[0,0,0]))+value(u,'rotation',[0,0,0]),degrees=True).as_matrix();s=value(u,'scale',[1,1,1]);A=r@np.diag(s);b=o-A@o+value(u,'position',[0,0,0]);P,q=mats[self.parent[u]];mats[u]=(P@A,P@b+q)
  return mats
 def frame(self,a=None,t=0):
  mats=self.matrices(a,t);A=np.array([mats[u][0] for u in self.owners]);b=np.array([mats[u][1] for u in self.owners]);p=self.local@A.transpose(0,2,1)+b[:,None,:];v=p[self.ci[:,None],self.idx];n=np.cross(v[:,1]-v[:,0],v[:,2]-v[:,0]);n/=np.maximum(1e-12,np.linalg.norm(n,axis=1))[:,None];n*=np.where(np.sum(n*(v.mean(1)-p.mean(1)[self.ci]),axis=1)<0,-1,1)[:,None];return v,n,A
 def candidates(self,a=None,t=0,near=.1,exact=1e-4):
  v,n,A=self.frame(a,t);i,j=self.ii,self.jj;lo=v.min(1);hi=v.max(1);keep=np.all((hi[i]+near>=lo[j])&(hi[j]+near>=lo[i]),axis=1);i,j=i[keep],j[keep];dot=np.sum(n[i]*n[j],axis=1);keep=abs(dot)>=math.cos(math.radians(.1));i,j,dot=i[keep],j[keep],dot[keep];ds=np.einsum('ijk,ik->ij',v[j]-v[i,0,None,:],n[i]);keep=np.max(abs(ds),axis=1)<=near+1e-8;i,j,ds,dot=i[keep],j[keep],ds[keep],dot[keep];out=[]
  for k,l,d,sgn in zip(i,j,ds,dot):
   org=v[k,0];ar=overlap(v[k]-org,v[l]-org,n[k]);
   if ar<=1e-5:continue
   ci,cj=int(self.ci[k]),int(self.ci[l]);dist=float(np.mean(d));out.append(dict(cube_a=self.e[ci]['name'],face_a=NAMES[self.fi[k]],cube_b=self.e[cj]['name'],face_b=NAMES[self.fi[l]],plane_distance=dist,max_plane_distance=float(np.max(abs(d))),overlap_area=ar,kind=('opposing_contact' if sgn<0 else 'coplanar' if max(abs(d))<=exact else 'near_parallel'),i=ci,j=cj,normal=n[k].tolist(),local_normal_a=(A[ci].T@n[k]).tolist(),local_normal_b=(A[cj].T@n[k]).tolist()))
  return out
 def audit(self,hz=0,near=.1):
  records={};counts={};samples=0
  frames=[(None,0.)]
  if hz:
   for a in self.m.get('animations',[]):
    ts=set(np.linspace(0,a['length'],math.ceil(a['length']*hz)+1));ts.update(k['time'] for tr in a.get('animators',{}).values() for k in tr.get('keyframes',[]) if 0<=k['time']<=a['length']);frames.extend((a,t) for t in sorted(ts))
  for a,t in frames:
   clip=a['name'] if a else 'rest';samples+=1
   for r in self.candidates(a,t,near):
    key=(clip,r['i'],r['face_a'],r['j'],r['face_b'],r['kind']);counts[r['kind']]=counts.get(r['kind'],0)+1
    if key not in records:records[key]=dict(r,clip=clip,time=float(t),hits=1)
    else:records[key]['hits']+=1
  return dict(samples=samples,counts=counts,unique_by_kind={k:sum(r['kind']==k for r in records.values()) for k in counts},issues=list(records.values()),unsupported=self.unsupported,limits='Numeric linear XYZ Euler approximation; normals within 0.1 degrees of parallel or antiparallel, exact distance <= 0.0001, near distance <= configured threshold; no occlusion, alpha-mask, runtime or continuous-time guarantee. Opposing contact requires separate review.')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('model',type=Path);p.add_argument('--hz',type=float,default=0);p.add_argument('--near',type=float,default=.1);p.add_argument('--output',type=Path);p.add_argument('--strict-near',action='store_true');a=p.parse_args();r=Scene(json.loads(a.model.read_text())).audit(a.hz,a.near);s=json.dumps(r,indent=2);a.output.write_text(s) if a.output else print(s);raise SystemExit(bool(r['counts'].get('coplanar') or r['unsupported'] or (a.strict_near and r['counts'].get('near_parallel'))))
