import unittest
from ftpsitenav import FTPSiteNav

class TestFTPSiteNav(unittest.TestCase):

	def testGetLatestFromPattern(self):
		print "TestFTPSiteNav : testGetLatestFromPattern"
		ftp = FTPSiteNav("build.gateway.michaelpage.local")
		dir = "TempBookingParentPOM/trunk"
		pattern = "TempBookingApplicationEar-tempbookingbuild-3.0.0-SNAPSHOT-build.*.ear"
		expected = ("TempBookingApplicationEar-tempbookingbuild-3.0.0-SNAPSHOT-build.279.ear", "279")
		latest = ftp.getLatestFromPattern(dir, pattern)
		self.assertNotEqual(len(ftp.lines), 0)
		print "--- output from ftp command ---"
		for line in ftp.lines:
			print line
		self.assertEqual(latest[0], expected[0])
		print "--- filename returned ---"
		print latest[0]
		self.assertEqual(latest[1], expected[1])
		print "--- pattern match returned ---"
		print latest[1]
		
	def test_CreateDate(self):
		print "testGetLatestFromPattern : test_CreateDate"
		ftp = FTPSiteNav("build.gateway.michaelpage.local")
		d = ftp._createDate("01-31-12", "05:49PM")
		self.assertEqual(d.getDate(), 31)
		self.assertEqual(d.getMonth(), 0)
		self.assertEqual(d.getYear(), 112)
		d = ftp._createDate("01-31-88", "05:49PM")
		self.assertEqual(d.getDate(), 31)
		self.assertEqual(d.getMonth(), 0)
		self.assertEqual(d.getYear(), 88)
		
def suite():
	suite = unittest.TestSuite()
	suite.addTest(TestFTPSiteNav("test_CreateDate"))
	suite.addTest(TestFTPSiteNav("testGetLatestFromPattern"))
	return suite