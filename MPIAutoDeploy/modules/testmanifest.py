import os, sys
import unittest
from manifest import CMDBManifest
from manifest import CIManifest

class TestCMDBManifest(unittest.TestCase):
	def setUp(self):
		xml = """
		<release-manifest>
			<psc>
				<id>GWA_00_03_00_09</id>
				<name>ENTERPRISECONTRACTSANDSCHEMAS</name>
				<!-- version with leading underscore - current at time of writing -->
				<version>_03_08_04_00</version>
			</psc>
			<psc>
				<id>GWA_00_03_00_09</id>
				<name>REFERENCEDATALOOKUPSERVICE</name>
				<!-- version without leading underscore -->
				<version>02_00_02_00</version>
			</psc>
			
		</release-manifest>
		"""
		self.testfile = "testmanifest.xml"
		outf = open(self.testfile, "w")
		outf.writelines(xml)
		outf.close()
	def testGetPSCs(self):
		print "TestCMDBManifest : testGetPSCs"
		man = CMDBManifest(self.testfile)
		pscs = man.getPSCs()
		self.assertEqual(len(pscs), 2)
		self.assertEqual(pscs[0][0], "ENTERPRISECONTRACTSANDSCHEMAS")
		self.assertEqual(pscs[0][1], "03_08_04_00")
		self.assertEqual(pscs[1][0], "REFERENCEDATALOOKUPSERVICE")
		self.assertEqual(pscs[1][1], "02_00_02_00")
		self.assertEqual(man.releaseId, "GWA_00_03_00_09")
		
	def testGetReleaseId(self):
		print "TestCMDBManifest : testGetReleaseId"
		man = CMDBManifest(self.testfile)
		id = man.getReleaseId()
		self.assertEqual(id, "GWA_00_03_00_09")

class TestCIManifest(unittest.TestCase):
	def testGetPSCs(self):
		print "TestCIManifest : testGetPSCs"
		man = CIManifest("sample_properties/CIDeploys.xls")
		pscs = man.getPSCs()
		# make sure we have more than one
		assert(len(pscs) > 1, "%i is not greater than 1" % len(pscs))
		# add stuff here
		self.assertEqual(pscs[0][0], "TempBookingApplication")
		self.assertEqual(pscs[0][1], "SNAPSHOT")
		self.assertEqual(pscs[1][0], "TempBookingNotificationService")
		self.assertEqual(pscs[1][1], "SNAPSHOT")
		self.assertEqual(man.releaseId, "CIDeploy")
		
	def testGetReleaseId(self):
		print "TestCIManifest : testGetReleaseId"
		man = CIManifest("sample_properties/CIDeploys.xls")
		id = man.getReleaseId()
		self.assertEqual(id, "CIDeploy")
		
		
def suite():
	suite = unittest.TestSuite()
	suite.addTest(TestCMDBManifest("testGetPSCs"))
	suite.addTest(TestCMDBManifest("testGetReleaseId"))
	suite.addTest(TestCIManifest("testGetPSCs"))
	suite.addTest(TestCIManifest("testGetReleaseId"))
	return suite