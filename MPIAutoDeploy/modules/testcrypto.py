import unittest
from crypto import EncryptedPassword

class TestEmbeddedPassword(unittest.TestCase):
	def testEncrypt(self):
		print "TestEmbeddedPassword : testEncrypt"
		ep = EncryptedPassword()
		self.assertEqual("r5ISHXLXSgbYhhLqhtj+Mg==", ep.encrypt("password"))
	def testDecrypt(self):
		print "TestEmbeddedPassword : testDecrypt"
		ep = EncryptedPassword()
		self.assertEqual("password", ep.decrypt("r5ISHXLXSgbYhhLqhtj+Mg=="))
	def testRoundTrip(self):
		print "TestEmbeddedPassword : testRoundTrip"
		ep = EncryptedPassword()
		self.assertEqual(ep.decrypt(ep.encrypt("Password123")), "Password123")
		
def suite():
	suite = unittest.TestSuite()
	suite.addTest(TestEmbeddedPassword("testEncrypt"))
	suite.addTest(TestEmbeddedPassword("testDecrypt"))
	suite.addTest(TestEmbeddedPassword("testRoundTrip"))
	return suite
