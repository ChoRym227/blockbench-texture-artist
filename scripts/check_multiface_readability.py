#!/usr/bin/env python3
"""Flag low-information UV faces on selected focal objects. Not an aesthetic or visibility classifier."""
import argparse,json,base64,io
from pathlib import Path
import numpy as np
from PIL import Image

def audit(m,folder,policy=None):
 tex=[];issues=[];stats=[];policy=policy or {}
 for t in m['textures']:
  src=t.get('source','');im=Image.open(io.BytesIO(base64.b64decode(src.split(',',1)[1]))) if src.startswith('data:') else Image.open(folder/t['name']);tex.append(np.array(im.convert('RGBA')))
 for e in m['elements']:
  if e.get('type','cube')!='cube':continue
  spec=policy.get(e['name'],{});faces=spec.get('detail_faces',[])
  for f,d in e['faces'].items():
   if d.get('texture') is None:continue
   u,v,U,V=map(int,d['uv']);u,U=sorted((u,U));v,V=sorted((v,V));p=tex[d['texture']][v:V,u:U];a=p[p[:,:,3]>0,:3];n=len(a)
   if not n:continue
   colors,cnt=np.unique(a,axis=0,return_counts=True);contrast=float(np.ptp(a@np.array([.2126,.7152,.0722])));dominance=float(max(cnt)/n);eligible=n>=4 and (U-u>=2 or V-v>=2);flat=len(colors)<2 or contrast<8 or dominance>.95
   if f in faces:
    rec=dict(cube=e['name'],face=f,size=[U-u,V-v],colors=len(colors),dominance=round(dominance,3),luma_range=round(contrast,2),eligible=eligible);stats.append(rec)
    if eligible and flat:issues.append(rec)
 return dict(selected_faces=len(stats),warnings=issues,faces=stats,limits='Heuristic: selected visible-intent faces only, tiny faces exempt; variation does not prove material quality or seam continuity. Inspect actual multi-angle renders.')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('model',type=Path);p.add_argument('--policy',type=Path);p.add_argument('--output',type=Path);a=p.parse_args();r=audit(json.loads(a.model.read_text()),a.model.parent,json.loads(a.policy.read_text()) if a.policy else {});s=json.dumps(r,indent=2);a.output.write_text(s) if a.output else print(s)
