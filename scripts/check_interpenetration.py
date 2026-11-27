#!/usr/bin/env python3
"""Surface/solid intersection for rotated cubes, including affine animated transforms.
Reports geometric candidates, NOT visibility or aesthetic proof. Explicit per-face
protection policies distinguish intentional attachments from unwanted penetration.
"""
import argparse,json,math
from pathlib import Path
import numpy as np
from check_z_fighting import Scene,FACES

def polyarea(p):
 if len(p)<3:return 0.
 return float(np.linalg.norm(np.cross(p,np.roll(p,-1,axis=0)).sum(0))/2)

def clip(poly,normal,limit):
 if not len(poly):return poly
 out=[];prev=poly[-1];pd=limit-prev@normal
 for cur in poly:
  cd=limit-cur@normal
  if (pd>=0)!=(cd>=0):out.append(prev+(cur-prev)*pd/(pd-cd))
  if cd>=0:out.append(cur)
  prev=cur;pd=cd
 return np.asarray(out)

def coverage(face,origin,inv,eps=1e-5):
 # World face clipped against open local unit box; affine transform handles nonuniform bone scale.
 q=(face-origin)@inv.T
 for axis in range(3):
  n=np.eye(3)[axis];q=clip(q,n,1-eps);q=clip(q,-n,-eps)
  if len(q)<3:return 0.
 # affine map preserves area ratio on a single plane
 return min(1.,polyarea(q)/max(polyarea((face-origin)@inv.T),1e-12))

def world(scene,a=None,t=0):
 mats=scene.matrices(a,t);A=np.array([mats[u][0] for u in scene.owners]);b=np.array([mats[u][1] for u in scene.owners]);return scene.local@A.transpose(0,2,1)+b[:,None,:]

def frames(scene,hz):
 yield None,0.
 if hz:
  for a in scene.m.get('animations',[]):
   ts=set(np.linspace(0,a['length'],math.ceil(a['length']*hz)+1));ts.update(k['time'] for tr in a.get('animators',{}).values() for k in tr.get('keyframes',[]) if 0<=k['time']<=a['length'])
   for t in sorted(ts):yield a,float(t)

def candidates(scene,p,policy=None,all_faces=True):
 policy=policy or {};lo=p.min(1);hi=p.max(1);orig=p[:,3];B=np.stack([p[:,2]-orig,p[:,0]-orig,p[:,7]-orig],axis=2);valid=abs(np.linalg.det(B))>1e-10;inv=np.zeros_like(B);inv[valid]=np.linalg.inv(B[valid]);out=[]
 for i,e in enumerate(scene.e):
  name=e['name'];spec=policy.get(name,{});protected=spec.get('protected_faces',[]);allowed=spec.get('allow',{});faces=list(FACES) if all_faces else protected
  if not faces:continue
  js=np.where(np.all((hi[i]>lo+1e-6)&(hi>lo[i]+1e-6),axis=1)&valid)[0]
  for f in faces:
   if e.get('faces',{}).get(f,{}).get('texture') is None:continue
   face=p[i,FACES[f]];fmin=face.min(0);fmax=face.max(0)
   for j in js:
    if i==j or not np.all((fmax>=lo[j])&(hi[j]>=fmin)):continue
    frac=coverage(face,orig[j],inv[j]);other=scene.e[j]['name']
    if frac<=1e-5:continue
    protected_hit=f in protected and other not in allowed.get(f,[])
    if all_faces or protected_hit:out.append(dict(cube=name,face=f,other=other,fraction=round(frac,6),kind='protected' if protected_hit else 'fully_covered' if frac>.999 else 'partial_coverage'))
 return out

def audit(m,policy=None,hz=0):
 s=Scene(m);records={};counts={};sample=0
 for a,t in frames(s,hz):
  sample+=1
  for r in candidates(s,world(s,a,t),policy,all_faces=a is None):
   key=(r['cube'],r['face'],r['other'],r['kind']);rec=records.setdefault(key,dict(r,clip=a['name'] if a else 'rest',time=t,hits=0));rec['hits']+=1;counts[r['kind']]=counts.get(r['kind'],0)+1
   if r['fraction']>rec['fraction']:rec.update(fraction=r['fraction'],clip=a['name'] if a else 'rest',time=t)
 return dict(samples=sample,counts=counts,issues=list(records.values()),unsupported=s.unsupported,limits='All textured faces at rest; only configured protected faces during numeric linear sampled animation. Pairwise coverage, not union or visibility; no continuous-time or alpha-mask proof. Full coverage can be intentional. Missing policy is not a pass.')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('model',type=Path);p.add_argument('--policy',type=Path);p.add_argument('--hz',type=float,default=0);p.add_argument('--output',type=Path);a=p.parse_args();r=audit(json.loads(a.model.read_text()),json.loads(a.policy.read_text()) if a.policy else {},a.hz);v=json.dumps(r,indent=2);a.output.write_text(v) if a.output else print(v);raise SystemExit(bool(r['counts'].get('protected') or r['unsupported']))
