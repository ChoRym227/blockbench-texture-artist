#!/usr/bin/env python3
"""Check explicitly designated support contacts with affine box SAT. Candidate gap, not physical support proof."""
import argparse,json
from pathlib import Path
import numpy as np
from check_z_fighting import Scene
from check_interpenetration import world,frames

def gap(a,b):
 def edges(p):return [p[2]-p[3],p[0]-p[3],p[7]-p[3]]
 u,v=edges(a),edges(b);axes=[np.cross(x,y) for es in (u,v) for x,y in zip(es,es[1:]+es[:1])]+[np.cross(x,y) for x in u for y in v];g=-float('inf')
 for ax in axes:
  length=np.linalg.norm(ax)
  if length<1e-10:continue
  ax=ax/length;p=a@ax;q=b@ax;g=max(g,float(q.min()-p.max()),float(p.min()-q.max()))
 return g

def audit(m,policy,hz=0,tol=.08):
 s=Scene(m);ix={e['name']:i for i,e in enumerate(s.e)};r={};samples=0
 for a,t in frames(s,hz):
  samples+=1;p=world(s,a,t)
  for n,parents in policy.items():
   if n not in ix or not parents or any(x not in ix for x in parents):raise ValueError(f'Invalid support policy: {n}: {parents}')
   g=min(gap(p[ix[n]],p[ix[x]]) for x in parents)
   if g>tol:
    row=r.setdefault(n,dict(cube=n,supports=parents,hits=0,max_axis_gap=0));row['hits']+=1
    if g>row['max_axis_gap']:row.update(max_axis_gap=g,clip=a['name'] if a else 'rest',time=t)
 return dict(samples=samples,attachments=len(policy),warnings=list(r.values()),unsupported=s.unsupported,limits='SAT separation axis gap, not Euclidean closest distance; explicit supports only, numeric sampled poses, no continuous or runtime proof.')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('model',type=Path);p.add_argument('--policy',type=Path,required=True);p.add_argument('--hz',type=float,default=0);p.add_argument('--output',type=Path);a=p.parse_args();r=audit(json.loads(a.model.read_text()),json.loads(a.policy.read_text()),a.hz);t=json.dumps(r,indent=2);a.output.write_text(t) if a.output else print(t);raise SystemExit(bool(r['warnings'] or r['unsupported']))
