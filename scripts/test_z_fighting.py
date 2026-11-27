"""Synthetic regression tests, no assets or external services required."""
import unittest
from check_z_fighting import Scene

def cube(n,lo,hi,rot=(0,0,0)):
 return dict(uuid=n,name=n,type='cube',**{'from':lo,'to':hi},origin=[0,0,0],rotation=list(rot),faces={f:{'texture':0} for f in ('north','south','east','west','up','down')})
def model(a,b,anim=None):
 return {'elements':[a,b],'outliner':[{'name':'root','uuid':'root','origin':[0,0,0],'children':['a',{'name':'moving','uuid':'moving','origin':[0,0,0],'children':['b']}]}],'animations':anim or []}
class Cases(unittest.TestCase):
 def test_exact_duplicate(self):
  a=cube('a',[0,0,0],[2,2,2]);b=cube('b',[0,0,0],[2,2,2]);self.assertEqual(Scene(model(a,b)).audit()['counts']['coplanar'],6)
 def test_no_area_edge(self):
  a=cube('a',[0,0,0],[2,2,2]);b=cube('b',[2,2,0],[4,4,2]);self.assertFalse(Scene(model(a,b)).audit()['counts'])
 def test_internal_contact(self):
  a=cube('a',[0,0,0],[2,2,2]);b=cube('b',[2,0,0],[4,2,2]);r=Scene(model(a,b)).audit()['counts'];self.assertEqual(r,{'opposing_contact':1})
 def test_rotated_exact(self):
  a=cube('a',[0,0,0],[2,2,2],(0,30,0));b=cube('b',[1,0,0],[3,2,2],(0,30,0));self.assertGreater(Scene(model(a,b)).audit()['counts'].get('coplanar',0),0)
 def test_near(self):
  a=cube('a',[0,0,0],[2,2,2]);b=cube('b',[.05,.05,.05],[2.05,2.05,2.05]);self.assertEqual(Scene(model(a,b)).audit()['counts']['near_parallel'],6)
 def test_animation(self):
  a=cube('a',[0,0,0],[2,2,2]);b=cube('b',[3,0,0],[5,2,2]);k=lambda t,x:{'channel':'position','time':t,'interpolation':'linear','data_points':[{'x':x,'y':0,'z':0}]};anim={'uuid':'a1','name':'move','length':1,'animators':{'moving':{'keyframes':[k(0,0),k(1,-3)]}}};r=Scene(model(a,b,[anim])).audit(20);self.assertGreater(r['counts'].get('coplanar',0),0)
if __name__=='__main__':unittest.main()
