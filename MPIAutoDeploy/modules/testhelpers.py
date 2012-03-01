import os, sys
import unittest
from helpers import Set
from helpers import RegexStuff

class TestSet(unittest.TestCase):
	def setUp(self):
		self.myset = Set(["thing1", "thing2", "thing3", "thing1"])
		print "setList ="
		for item in self.myset.setList:
			print "\t" + item
	def testContains(self):
		contains = self.myset.contains("thing1")
		self.assertNotEqual(contains, 0)
		contains = self.myset.contains("foo")
		self.assertEqual(contains, 0)
		if self.myset.contains("thing1"):
			print "self.myset.contains('thing1') is true (whatever that is)"
		else:
			print "self.myset.contains('thing1') is false (whatever that is)"
		if self.myset.contains("foo"):
			print "self.myset.contains('foo') is true (whatever that is)"
		else:
			print "self.myset.contains('foo') is false (whatever that is)"
	def testGetCount(self):
		print "TestSet : testGetCount"
		self.assertEqual(self.myset.getCount(), 3)

class TestRegexStuff(unittest.TestCase):
	def testRegexFromWildcard(self):
		rs = RegexStuff()
		regex = rs.regexFromWildcard("*.a.b")
		self.assertEqual(regex, ".*\.a\.b")
		regex = rs.regexFromWildcard("a.*.b")
		self.assertEqual(regex, "a\..*\.b")
	
def suite():
	suite = unittest.TestSuite()
	suite.addTest(TestSet("testContains"))
	suite.addTest(TestSet("testGetCount"))
	suite.addTest(TestRegexStuff("testRegexFromWildcard"))
	return suite