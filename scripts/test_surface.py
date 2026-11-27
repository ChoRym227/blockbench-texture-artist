import unittest
import numpy as np
from check_interpenetration import coverage
from check_attachment import gap
from check_z_fighting import corners
class TestSurface(unittest.TestCase):
 def test_half(self):
  f=np.array([[-.5,.5,0],[.5,.5,0],[.5,.5,1],[-.5,.5,1]])
  self.assertAlmostEqual(coverage(f,np.zeros(3),np.eye(3)),.5,places=4)
 def test_coplanar_excluded(self):
  f=np.array([[0,0,0],[1,0,0],[1,0,1],[0,0,1]])
  self.assertEqual(coverage(f,np.zeros(3),np.eye(3)),0)
 def test_inside(self):
  f=np.array([[.1,.5,.1],[.8,.5,.1],[.8,.5,.8],[.1,.5,.8]])
  self.assertAlmostEqual(coverage(f,np.zeros(3),np.eye(3)),1)
 def test_rotated_scaled(self):
  f=np.array([[-.5,.5,0],[.5,.5,0],[.5,.5,1],[-.5,.5,1]]);A=np.array([[0,-2,0],[1,0,0],[0,0,.5]]);t=np.array([2,3,4]);self.assertAlmostEqual(coverage(f@A.T+t,t,np.linalg.inv(A)),.5,places=4)
 def test_sat(self):
  a=corners({'from':[0,0,0],'to':[1,1,1]});self.assertAlmostEqual(gap(a,a+[2,0,0]),1);self.assertLess(gap(a,a+[.5,0,0]),0);self.assertAlmostEqual(gap(a,a+[1,0,0]),0)
if __name__=='__main__':unittest.main()
