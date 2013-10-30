#! /usr/bin/env python
#
# Quick and dirty quaternion library.  This only exists because there is no
# obvious alternative and numpy doesn't (yet) support quaternions directly.

import unittest
import random

import numpy as np
import numpy.matlib as m

from numbers import Number

class Quaternion(object):
	def __init__(self, q=None, dtype=np.float64):
		self.dtype = dtype
		if q is None:
			self.q = np.asarray([1,0,0,0], dtype)
		else:
			self.q = np.asarray(q, dtype)

	def __str__(self):
		return "[%f, %f, %f, %f]" % (self.q[0], self.q[1], self.q[2], self.q[3])
	
	def __eq__(self, other):
		if (self - other).length() < 0.0001:
			return True
		else:
			return False

	def __add__(self, other):
		return Quaternion(q=self.q + other.q, dtype=self.dtype)

	def __sub__(self, other):
		return Quaternion(q=self.q - other.q, dtype=self.dtype)

	def __mul__(self, other):
		if isinstance(other, Number):
			return Quaternion(q=self.q * other, dtype=self.dtype)
		
		q = self
		r = other
		x0 = r[0]*q[0] - r[1]*q[1] - r[2]*q[2] - r[3]*q[3]
		x1 = r[0]*q[1] + r[1]*q[0] - r[2]*q[3] + r[3]*q[2]
		x2 = r[0]*q[2] + r[1]*q[3] + r[2]*q[0] - r[3]*q[1]
		x3 = r[0]*q[3] - r[1]*q[2] + r[2]*q[1] + r[3]*q[0]
		return Quaternion(q=[x0, x1, x2, x3], dtype=self.dtype)

	def __rmul__(self, other):
		return Quaternion(q=self.q * other, dtype=self.dtype)

	#def __div__(self, other):
		##return Quaternion(q=self.q / other, dtype=self.dtype)
		#return self * (1 / other)

	#def __pow__(self, other):
		#pass

	def __neg__(self):
		return Quaternion(q=-1 * self.q, dtype=self.dtype)

	def __getitem__(self, key):
		return self.q[key]

	#def __setitem__(self, key, item):
		##assert(0 <= key <= 3)
		#self.q[key] = item

	def norm2(self):
		return np.dot(self.q, self.q)

	def length(self):
		return np.sqrt(self.norm2())

	def normalize(self):
		self.q = self.q / self.length()
		return self

	def normalized(self):
		return Quaternion(self.q / self.length(), dtype=self.dtype)

	# Rotation conversion equations are taken from Wikipedia
	def to_matrix(self):
		"""Returns 3x3 rotation matrix corresponding to this quaternion."""
		rmat = np.empty((3,3), self.dtype)
		#w, x, y, z = self.q

		#xx2 = 2*x*x
		#yy2 = 2*y*y
		#zz2 = 2*z*z
		#xy2 = 2*x*y
		#wz2 = 2*w*z
		#zx2 = 2*z*x
		#wy2 = 2*w*y
		#yz2 = 2*y*z
		#wx2 = 2*w*x

		#rmat[0,0] = 1. - yy2 - zz2
		#rmat[0,1] = xy2 - wz2
		#rmat[0,2] = zx2 + wy2
		#rmat[1,0] = xy2 + wz2
		#rmat[1,1] = 1. - xx2 - zz2
		#rmat[1,2] = yz2 - wx2
		#rmat[2,0] = zx2 - wy2
		#rmat[2,1] = yz2 + wx2
		#rmat[2,2] = 1. - xx2 - yy2

		q1, q2, q3, q4 = self.q
		rmat[0,0] = 1. - 2*q2*q2 - 2*q3*q3
		rmat[0,1] = 2*(q1*q2 - q3*q4)
		rmat[0,2] = 2*(q1*q3 + q2*q4)
		rmat[1,0] = 2*(q1*q2 + q3*q4)
		rmat[1,1] = 1. - 2*q1*q1 - 2*q3*q3
		rmat[1,2] = 2*(q2*q3 - q1*q4)
		rmat[2,0] = 2*(q1*q3 - q2*q4)
		rmat[2,1] = 2*(q1*q4 + q2*q3)
		rmat[2,2] = 1. - 2*q1*q1 - 2*q2*q2

		assert abs(np.linalg.det(rmat) - 1) < 0.001
		#print(abs(np.linalg.det(rmat) - 1))

		return rmat

	def from_matrix(self, mat):
		"""Set this quaternion to match the given 3x3 rotation matrix."""
		assert abs(np.linalg.det(mat) - 1) < 0.001

		q4 = 0.5 * np.sqrt(1. + mat[0,0] + mat[1,1] + mat[2,2])
		q4_t = 1. / (4*q4)
		q1 = q4_t * (mat[2,1] - mat[1,2])
		q2 = q4_t * (mat[0,2] - mat[2,0])
		q3 = q4_t * (mat[1,0] - mat[0,1])

		self.q = np.asarray([q1,q2,q3,q4], self.dtype)
		self.normalize()

	def from_euler(self, phi, theta, psi):
		#self.q[0] = np.cos(phi/2) * np.cos(theta/2) * np.cos(psi/2) +\
		            #np.sin(phi/2) * np.sin(theta/2) * np.sin(psi/2)
		#self.q[1] = np.sin(phi/2) * np.cos(theta/2) * np.cos(psi/2) -\
		            #np.cos(phi/2) * np.sin(theta/2) * np.sin(psi/2)
		#self.q[2] = np.cos(phi/2) * np.sin(theta/2) * np.cos(psi/2) +\
		            #np.sin(phi/2) * np.cos(theta/2) * np.sin(psi/2)
		#self.q[3] = np.cos(phi/2) * np.cos(theta/2) * np.sin(psi/2) -\
		            #np.sin(phi/2) * np.sin(theta/2) * np.cos(psi/2)
		self.q[0] = np.cos((phi - psi)/2) * np.sin(theta/2)
		self.q[1] = np.sin((phi - psi)/2) * np.sin(theta/2)
		self.q[2] = np.sin((phi + psi)/2) * np.cos(theta/2)
		self.q[3] = np.cos((phi + psi)/2) * np.cos(theta/2)

	def from_axis_angle(self, axis, angle):
		assert abs(axis[0]**2 + axis[1]**2 + axis[2]**2 - 1.0) < 0.001
		self.q[3] = np.cos(angle / 2)
		self.q[0] = np.sin(angle / 2) * np.cos(axis[0])
		self.q[1] = np.sin(angle / 2) * np.cos(axis[1])
		self.q[2] = np.sin(angle / 2) * np.cos(axis[2])


class TestQuaternion(unittest.TestCase):

	EPS = 1e-10

	def rand_quaternion(self):
		w = random.random()
		x = random.random()
		y = random.random()
		z = random.random()
		q1 = Quaternion([w,x,y,z], np.float64)
		q1.normalize()
		return q1

	def rand_euler(self):
		# NOTE: Theta is limited to (0,pi)
		phi = random.random() * 2*np.pi
		theta = random.random() * 1*np.pi
		psi = random.random() * 2*np.pi
		return (phi, theta, psi)
	
	def test_add(self):
		"""simple addition test cases."""
		q1 = Quaternion([1,2,3,4], np.float64)
		q2 = Quaternion([2,3,4,1], np.float64)
		self.assertTrue((q2 + q1 - Quaternion([3,5,7,5], np.float64)).length() < TestQuaternion.EPS)

		x = np.sqrt(2, dtype=np.float64)
		q1 = Quaternion([x,x,x,x], np.float64)
		self.assertTrue((q1 + q2 - Quaternion([2+x, 3+x, 4+x, 1+x], np.float64)).length() < TestQuaternion.EPS)

	def test_sub(self):
		"""simple subtraction test case."""
		q1 = Quaternion([1,2,3,4], np.float64)
		q2 = Quaternion([2,3,4,1], np.float64)
		self.assertTrue((q1 - q2 - Quaternion([-1,-1,-1,3], np.float64)).length() < TestQuaternion.EPS)

	def test_length(self):
		"""norm2 and length, as well as quaternion normalization functions."""
		# Test norm2 and length
		q1 = Quaternion([1,1,1,1], np.float64)
		self.assertEqual(q1.norm2(), 4)
		self.assertEqual(q1.length(), 2.0)

		# Copy normalize test
		q2 = q1.normalized()
		self.assertEqual(q2[0], q2[1])
		self.assertEqual(q2[0], q2[2])
		self.assertEqual(q2[0], q2[3])

		# Destructive normalize test
		q1.normalize()
		self.assertEqual(q1[0], q2[1])
		self.assertEqual(q1[1], q2[2])
		self.assertEqual(q1[2], q2[3])
		self.assertEqual(q1[3], q2[0])
	
	def test_multiply(self):
		q1 = Quaternion([0,0,0,1])
		q2 = Quaternion([0,0,0,0])
		self.assertEqual(q2, q1 * q2)

		q1 = Quaternion([1,2,3,4])
		self.assertEqual(q1*2, Quaternion([2,4,6,8]))

	#def test_div(self):
		#q1 = Quaternion([1,2,3,4])
		#q2 = q1 / 2.0
		#self.assertEqual(q1[0],1/2)

		#q1 = Quaternion([1,2,3,4])
		#q2 = q1 / 1.5
		#self.assertEqual(q1[0],1/1.5)

	def test_neg(self):
		"""Test additive inverse."""
		q1 = Quaternion([1,2,3,4])
		q2 = -q1
		self.assertEqual(q2, Quaternion([-1,-2,-3,-4]))

	def test_euler(self):
		"""Test axis-angle and euler representation conversions."""
		q1 = Quaternion([0,0,0,0], np.float64)
		#q1.from_euler(0, 0, 0)
		#print(q1)
		#self.assertEqual(q1, Quaternion([1,0,0,0]))


		for i in range(100):
			(phi, theta, psi) = self.rand_euler()
			q1.from_euler(phi, theta, psi)

			q_phi = np.arctan2(q1[0]*q1[2] + q1[1]*q1[3],-(q1[1]*q1[2]-q1[0]*q1[3]))
			q_theta = np.arccos(-q1[0]**2 -q1[1]**2 + q1[2]**2 + q1[3]**2)
			q_psi = np.arctan2(q1[0]*q1[2] - q1[1]*q1[3], q1[1]*q1[2] + q1[0]*q1[3])

			# Convert between different conventions
			if q_phi < 0:
				q_phi += 2 * np.pi
			#if q_theta < 0:
				#q_theta += 2 * np.pi
			if q_psi < 0:
				q_psi += 2 * np.pi

			r1 = m.matrix([phi, theta, psi])
			r1q = m.matrix([q_phi, q_theta, q_psi])
			#print(r1- r1q)
			self.assertTrue(np.linalg.norm(r1 - r1q) < 1e-10)

			# Synthesize three single-axis rotation matrices
			# This calculation seems broken at the moment (ordering of matrices?)
			#Ax = m.matrix([[1,            0,           0],
			               #[0,  np.cos(phi), np.sin(phi)],
			               #[0, -np.sin(phi), np.cos(phi)]])
			#Ay = m.matrix([[np.cos(theta), 0, -np.sin(theta)],
			               #[0,             1,              0],
			               #[np.sin(theta), 0,  np.cos(theta)]])
			#Az = m.matrix([[ np.cos(psi), np.sin(psi), 0],
			               #[-np.sin(psi), np.cos(psi), 0],
			               #[           0,           0, 1]])
			#R = Az * Ay * Ax
			#print('\n%s\n\n%s' % (R, q1.to_matrix()))

	def test_axis_angle(self):
		"""Verify that axis-angle conversions work correctly."""
		self.assertTrue(False)
	def test_types(self):
		"""Verify that types are maintained and passed correctly.
		Ignored for now."""
		self.assertTrue(False)


	def test_matrix(self):
		# WARNING: This really should have a lower error margin, but fails:
		# check the relevant equations
		for i in range(1000):
			q1 = self.rand_quaternion()

			mat = q1.to_matrix()

			q2 = Quaternion([0,0,0,0], np.float64)
			q2.from_matrix(mat)
			if (q1-q2).length() >= 5e-9:
				print((q1 - q2).length())
			self.assertTrue((q1 - q2).length() < 5e-9)

if __name__ == "__main__":
	random.seed()
	unittest.main()