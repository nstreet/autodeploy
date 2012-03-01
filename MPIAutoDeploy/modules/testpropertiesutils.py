import sys, os
import unittest
from propertiesutils import PropertiesFile
from propertiesutils import NonEncryptedPropertiesFile

class TestPropertiesFile(unittest.TestCase):
	def setUp(self):
		self.simplePropertiesFileName = "testproperties.properties"
		pf = open(self.simplePropertiesFileName, "w")
		self.properties = ["property.file.version=ENV_VERSION",
		"key=value",
		"space.filled.value=valuebit nextbit",
		"# comment",
		" ",
		"contains-equals=123=4",
		"equals-no-value=",
		"partial.key.1=one",
		"partial.key.2=two",
		"partial.key.3=three",
		"special-characters=Or@c1e@pp@dm!n",
		"back.slash=back\\slash",
		"mymodule.name=mymodule",
		"module.1.name=module1",
		"module.2.name=module2",
		"my.password.test=2u2RyevzeMFbxViTzOh8Cw=="]
		print "properties are:"
		for property in self.properties:
			print "\t" + property
			pf.writelines(property + "\n")
		pf.close()
	def tearDown(self):
		#os.remove(self.simplePropertiesFileName)
		pass
	def testGet(self):
		print "testGet"
		pf = PropertiesFile(self.simplePropertiesFileName)
		val = pf.get("key")
		self.assertEqual(val, "value")
		val = pf.get("rubbish")
		self.assertEqual(val, None)
		val = pf.get("space.filled.value")
		self.assertEqual(val, "valuebit nextbit")
		val = pf.get("special-characters")
		self.assertEqual(val, r"Or@c1e@pp@dm!n")
		val = pf.get("back.slash")
		self.assertEqual(val, r"back\slash")
	def testGetWithEqualsSign(self):
		print "testGetWithEqualsSign"
		pf = PropertiesFile(self.simplePropertiesFileName)
		val = pf.get("contains-equals")
		self.assertEqual(val, "123=4")
	def testGetPasswordProperty(self):
		print "TestPropertiesFile : testGetPasswordProperty"
		pf = PropertiesFile(self.simplePropertiesFileName)
		val = pf.get("my.password.test")
		self.assertEqual(val, "mypassword")
	def testCreateTokenisedProperties(self):
		print "testCreateTokenisedProperties"
		pf = PropertiesFile(self.simplePropertiesFileName)
		tokenisedFileName = pf.createTokenisedProperties("@@_", "_@@", "testtokenisedproperties.properties")
		tokenisedFile = PropertiesFile(tokenisedFileName)
		for tpk in tokenisedFile.properties.keys():
			print tpk + "=" + tokenisedFile.get(tpk)
			if not tpk == "property.file.version":
				self.assertEqual(tokenisedFile.get(tpk), pf.get(tpk[3:][:-3]).replace("\\", r"\\"))
				self.assertEqual(tpk[:3], "@@_")
				self.assertEqual(tpk[-3:], "_@@")
		for i in range(len(self.properties)):
				if self.properties[i].strip().startswith("#") or self.properties[i].strip() == "" or self.properties[i].strip().startswith("property.file.version"):
					self.assertEqual(pf.allEntries[i].strip(), tokenisedFile.allEntries[i].strip())
		
		os.remove(tokenisedFileName)

	def testGetPartialKey(self):
		print "testGetPartialKey"
		pf = PropertiesFile(self.simplePropertiesFileName)
		propertyList = pf.getPartialKey("partial.key.*")
		self.assertEqual(len(propertyList), 3)
		for key, value in propertyList:
			self.assertEqual(value, pf.get(key))
		propertyList = pf.getPartialKey("*.key.*")
		self.assertEqual(len(propertyList), 3)
		for key, value in propertyList:
			self.assertEqual(value, pf.get(key))
		propertyList = pf.getPartialKey("rubbish.*")
		self.assertEqual(len(propertyList), 0)
		propertyList = pf.getPartialKey("*.rubbish.*")
		self.assertEqual(len(propertyList), 0)
		propertyList = pf.getPartialKey("module.*.name")
		self.assertEqual(len(propertyList), 2)
		propertyList = pf.getPartialKey("*.name")
		self.assertEqual(len(propertyList), 1)

	def testValidateVersionProperty(self):
		print "testValidateVersionProperty"
		pf = PropertiesFile(self.simplePropertiesFileName)
		# default key property.file.version
		version = pf.validateVersionProperty()
		self.assertEqual(version, 1)
		# default key wrong value
		version = pf.validateVersionProperty(propertyValue="false-version")
		self.assertEqual(version, 0)
		# non-existent key
		version = pf.validateVersionProperty(propertyKey="non.key")
		self.assertEqual(version, 0)
		# default key correct version
		version = pf.validateVersionProperty(propertyValue="ENV_VERSION")
		self.assertEqual(version, 1)
		# non-existent key value exists
		version = pf.validateVersionProperty(propertyKey="non.key", propertyValue="ENV_VERSION")
		self.assertEqual(version, 0)
		# specified key value correct
		version = pf.validateVersionProperty(propertyKey="property.file.version", propertyValue="ENV_VERSION")
		self.assertEqual(version, 1)

class TestNonEncryptedPropertiesFile(unittest.TestCase):
	def setUp(self):
		self.properties = [
		"my.password.1=Password123!MP\n",
		"my.non.pwd=secretPassword\n",
		"#comment password=plainText\n",
		"my.encrypted.password=fyNcN+k8xoHjwLo/DV2nRQ==\n"
		]
		self.testFileName = "tmp/non-encrypted.properties"
		tf = open(self.testFileName , "w")
		tf.writelines(self.properties)
		tf.close()
	
	def testNonEncryptedPropertiesFile(self):
		print "TestNonEncryptedPropertiesFile : testNonEncryptedPropertiesFile"
		pf = NonEncryptedPropertiesFile(self.testFileName).getFile()
		print "[INFO] original contents of file:"
		for property in self.properties:
			print property.rstrip()
		print "[INFO] new contents of file"
		inf = open(self.testFileName, "r")
		for line in inf.readlines():
			print line.rstrip()
			if line.strip().startswith("#"):
				self.assertEqual(line, self.properties[2])
			if line.split("=")[0] == "my.password.1":
				self.assertEqual("=".join(line.split("=")[1:]).rstrip(), "fyNcN+k8xoE4Vq9qsAuurQ==")
			if line.split("=")[0] == "my.encrypted.password":
				self.assertEqual(line, self.properties[3])
		print "[INFO] returned value of my.password.1 : %s" % (pf.get("my.password.1"))
		self.assertEqual(pf.get("my.password.1"), "Password123!MP")
		print "[INFO] returned value of my.encrypted.password : %s" % (pf.get("my.encrypted.password"))
		self.assertEqual(pf.get("my.encrypted.password"), "Password123")
		
def suite():
	suite = unittest.TestSuite()
	suite.addTest(TestPropertiesFile("testGet"))
	suite.addTest(TestPropertiesFile("testGetWithEqualsSign"))
	suite.addTest(TestPropertiesFile("testGetPasswordProperty"))
	suite.addTest(TestPropertiesFile("testCreateTokenisedProperties"))
	suite.addTest(TestPropertiesFile("testGetPartialKey"))
	suite.addTest(TestPropertiesFile("testValidateVersionProperty"))
	suite.addTest(TestNonEncryptedPropertiesFile("testNonEncryptedPropertiesFile"))
	return suite