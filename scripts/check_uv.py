#!/usr/bin/env python3
"""Check integer per-face UV dimensions, bounds and partial overlaps."""
import argparse,json,math
from pathlib import Path

def audit(m,density=1):
    errors=[]; rects={}; occupied={}; count=0
    textures=m.get('textures',[])
    for e in m['elements']:
        if e.get('type','cube')!='cube': continue
        x,y,z=[abs(b-a)*density for a,b in zip(e['from'],e['to'])]
        for f,(w,h) in dict(north=(x,y),south=(x,y),east=(z,y),west=(z,y),up=(x,z),down=(x,z)).items():
            a=e.get('faces',{}).get(f,{}); tex=a.get('texture'); uv=a.get('uv'); name=e['name']+'/'+f
            if tex is None: continue
            count+=1
            if not isinstance(tex,int) or not 0<=tex<len(textures) or not uv or len(uv)!=4 or any(v!=round(v) for v in uv):errors.append([name,'invalid reference/UV']);continue
            u,v,U,V=map(int,uv); u,U=sorted((u,U));v,V=sorted((v,V))
            if a.get('rotation',0)%180==90:w,h=h,w
            t=textures[tex]; W=t.get('uv_width',m['resolution']['width']);H=t.get('uv_height',m['resolution']['height'])
            if not (0<=u<U<=W and 0<=v<V<=H and math.isclose(U-u,w) and math.isclose(V-v,h)):errors.append([name,'size/bounds']);continue
            r=(tex,u,v,U,V)
            if r not in rects:
                overlap=False
                for i in range(u,U):
                    for j in range(v,V):
                        k=(tex,i,j)
                        if k in occupied:overlap=True
                        occupied[k]=r
                if overlap:errors.append([name,'partial overlap'])
            rects[r]=rects.get(r,0)+1
    return dict(faces=count,unique_uv=len(rects),shared_faces=count-len(rects),errors=errors,limitations='Exact rectangle sharing allowed; artistic compatibility requires review.')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('model',type=Path);p.add_argument('--density',type=float,default=1);p.add_argument('--output',type=Path);a=p.parse_args();r=audit(json.loads(a.model.read_text()),a.density);s=json.dumps(r,indent=2);print(s) if not a.output else a.output.write_text(s);raise SystemExit(bool(r['errors']))
