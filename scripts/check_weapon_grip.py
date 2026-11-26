#!/usr/bin/env python3
"""Sample numeric linear bbmodel bone animation; approximate XYZ Euler OBB review, not runtime."""
import argparse,json,math
from pathlib import Path
import numpy as np
from scipy.spatial.transform import Rotation

def audit(m,c,hz=20):
    if hz<20: raise ValueError('minimum 20 Hz')
    groups={}; parent={}; owners={}; names={}
    def walk(b,p=None):
        if isinstance(b,str): owners[b]=p;return
        u=b['uuid'];groups[u]=b;parent[u]=p;names[b['name']]=u
        for a in b['children']:walk(a,u)
    for b in m['outliner']:walk(b)
    hand=names[c['hand_bone']]; weapon=names[c['weapon_bone']]; grip=np.array(c['grip'],float);anchor=np.array(c.get('hand_anchor',c['grip']),float);axis=np.array(c.get('weapon_axis',[0,1,0]),float);axis/=np.linalg.norm(axis)
    def descendant(u,root):
        while u:
            if u==root:return True
            u=parent[u]
        return False
    allowed={names[n] for n in c.get('allowed_contact_bones',[c['hand_bone']])}
    items=[]
    for e in m['elements']:
        if e.get('type','cube')!='cube':raise ValueError('only cubes supported')
        if e.get('inflate',0) or e.get('rescale',False):raise ValueError('inflate/rescale unsupported')
        owner=owners[e['uuid']];lo=np.array(e['from']);hi=np.array(e['to']);o=np.array(e['origin']);r=Rotation.from_euler('xyz',e.get('rotation',[0]*3),degrees=True).as_matrix();center=r@((lo+hi)/2-o)+o
        items.append((e['name'],owner,center,(hi-lo)/2,r))
    wi=[i for i,e in enumerate(items) if descendant(e[1],weapon)];bi=[i for i,e in enumerate(items) if i not in wi and e[1] not in allowed]
    def sat(A,ea,B,eb,d):
        # OBB separating axes, exclude touching surfaces by small tolerance.
        C=A.T@B;t=A.T@d; a=np.abs(C)+1e-9; tol=.08
        if np.any(np.abs(t)>=ea+a@eb-tol) or np.any(np.abs(C.T@t)>=eb+a.T@ea-tol):return False
        for i in range(3):
            for j in range(3):
                if abs(C[i,j])>.999999:continue
                p,q=(i+1)%3,(i+2)%3;v,w=(j+1)%3,(j+2)%3
                if abs(t[q]*C[p,j]-t[p]*C[q,j])>=ea[p]*a[q,j]+ea[q]*a[p,j]+eb[v]*a[i,w]+eb[w]*a[i,v]-tol*math.sqrt(max(0,1-C[i,j]**2)):return False
        return True
    reports=[]
    for clip in m['animations']:
        tracks={}; keytimes=set();L=clip['length']
        for u,anim in clip['animators'].items():
            if u not in groups:raise ValueError('unknown animator '+u)
            for k in anim['keyframes']:
                ch=k['channel'];keytimes.add(k['time'])
                if ch not in ('position','rotation') or k.get('interpolation','linear')!='linear' or len(k['data_points'])!=1:raise ValueError('unsupported keyframe')
                tracks.setdefault((u,ch),[]).append((k['time'],[float(k['data_points'][0][v]) for v in 'xyz']))
        tracks={k:(np.array([p[0] for p in sorted(v)]),np.array([p[1] for p in sorted(v)])) for k,v in tracks.items()}
        ts=sorted(set(round(float(t),7) for t in list(np.linspace(0,L,math.ceil(L*hz)+1))+list(keytimes)))
        def sample(u,ch,t):
            if (u,ch) not in tracks:return np.zeros(3)
            x,y=tracks[u,ch];return np.array([np.interp(t,x,y[:,i]) for i in range(3)])
        err=0; wrist=0;ground=math.inf;ground_frames=0;coll={}; collision_frames=0;prev=None;speed=0;direction=[]
        for t in ts:
            transforms={}
            for u,b in groups.items():
                o=np.array(b['origin']);r=Rotation.from_euler('xyz',np.array(b.get('rotation',[0]*3))+sample(u,'rotation',t),degrees=True).as_matrix();trans=o-r@o+sample(u,'position',t)
                if parent[u]:pr,pt=transforms[parent[u]];r,trans=pr@r,pr@trans+pt
                transforms[u]=(r,trans)
            hr,ht=transforms[hand];wr,wt=transforms[weapon];err=max(err,float(np.linalg.norm(hr@anchor+ht-wr@grip-wt)));wrist=max(wrist,float(np.linalg.norm(Rotation.from_euler('xyz',sample(hand,'rotation',t),degrees=True).as_rotvec())*180/math.pi))
            d=wr@axis;direction.append(d.tolist())
            if prev and t>prev[0]:speed=max(speed,math.degrees(math.acos(np.clip(prev[1]@d,-1,1)))/(t-prev[0]))
            prev=(t,d)
            centers=[];ext=[];rots=[];aabbs=[]
            for _,u,cc,ee,rr in items:
                r,p=transforms.get(u,(np.eye(3),np.zeros(3)));rr=r@rr;centers.append(r@cc+p);ext.append(ee);rots.append(rr);aabbs.append(np.abs(rr)@ee)
            centers=np.array(centers);aabbs=np.array(aabbs);low=min(centers[i,1]-aabbs[i,1] for i in wi);ground=min(ground,low);ground_frames+=low<c.get('ground_y',0)-c.get('ground_tolerance',1)
            hit=False
            for i in wi:
                delta=centers[bi]-centers[i];mask=np.all(np.abs(delta)<aabbs[bi]+aabbs[i]-.08,axis=1)
                for j in np.array(bi)[mask]:
                    if sat(rots[i],ext[i],rots[j],ext[j],centers[j]-centers[i]):
                        pair=items[i][0]+' / '+items[j][0];coll[pair]=coll.get(pair,0)+1;hit=True
            collision_frames+=hit
        reports.append(dict(clip=clip['name'],samples=len(ts),max_grip_error=round(err,6),max_wrist_rotation_deg=round(wrist,2),min_weapon_y=round(ground,3),ground_candidate_frames=int(ground_frames),intentional_ground_clip=clip['name'] in c.get('intentional_ground_clips',[]),collision_frames=int(collision_frames),collision_pairs=dict(sorted(coll.items(),key=lambda x:-x[1])),max_axis_speed_deg_s=round(speed,2)))
    return dict(hz=hz,clips=reports,limitations='Numeric linear keys, XYZ Euler approximation, cube OBB candidates with 0.08 unit tolerance; excludes declared hand contact bones. No actual engine evaluation; inspect collision candidates visually.')
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('model',type=Path);p.add_argument('--config',type=Path,required=True);p.add_argument('--output',type=Path);p.add_argument('--hz',type=int,default=20);a=p.parse_args();r=audit(json.loads(a.model.read_text()),json.loads(a.config.read_text()),a.hz);s=json.dumps(r,indent=2);print(s) if not a.output else a.output.write_text(s)
