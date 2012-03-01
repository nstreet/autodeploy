import os, sys
import unittest
from wlstutils import DatasourceConfig
from wlstutils import JMSResourceConfig
from wlstutils import ApplicationDeploymentConfig
from wlstutils import CommandOutputParser
from propertiesutils import PropertiesFile
from propertiesutils import XmlProperties
class TestDatasourceConfig(unittest.TestCase):
	def testGetConfig(self):
		print "TestDatasourceConfig : testGetConfig"
		pf = PropertiesFile("modules/testdsdetails.properties")
		dsList = pf.getPartialKey("*.db.host")
		testpost24 = 0
		testpre241 = 0
		for k, v in dsList:
			tag = k.split(".")[0]
			dsConfig = DatasourceConfig(tag, pf).getConfig()
			if pf.get(tag + ".datasource.name"):
				# post 2.4.0
				self.assertEqual(pf.get(tag + ".datasource.name"), dsConfig["name"])
				jndiList = []
				for jndiName in pf.get(tag + ".jndi.name").split(","):
					jndiList.append(jndiName.strip())
				self.assertEqual(jndiList, dsConfig["jndi"])
				testpost24 = 1
			else:
				# pre 2.4.1
				self.assertEqual(tag, dsConfig["name"])
				self.assertEqual(tag, dsConfig["jndi"][0])
				testpre241 = 1
			self.assertEqual(pf.get(tag + ".db.host"), dsConfig["host"])
			self.assertEqual(pf.get(tag + ".db.port"), dsConfig["port"])
			self.assertEqual(pf.get(tag + ".db.user"), dsConfig["user"])
			self.assertEqual(pf.get(tag + ".db.password"), dsConfig["password"])
			self.assertEqual(pf.get(tag + ".db.name"), dsConfig["dbName"])
			self.assertEqual(pf.get(tag + ".db.url"), dsConfig["url"])
			self.assertEqual(pf.get(tag + ".db.driver"), dsConfig["driver"])
			targets = []
			for target in pf.get(tag + ".target").split(","):
				targets.append(target.strip())
			self.assertEqual(targets, dsConfig["target"])
		self.assertEqual(testpost24, 1)
		self.assertEqual(testpre241, 1)

class TestJMSResourceConfig(unittest.TestCase):
	def testGetConfig(self):
		print "TestJMSResourceConfig : testGetConfig"
		pf = PropertiesFile("modules/testjmsdetails.properties")
		jmsList = pf.getPartialKey("*.jms.system.module.name")
		for k, v in jmsList:
			tag = k.split(".")[0]
			jmsConfig = JMSResourceConfig(tag, pf).getConfig()
			self.assertEqual(pf.get(tag + ".jms.system.module.name"), tag)
			if pf.get(tag + ".jms.system.module.suffix"):
				self.assertEqual(jmsConfig["module.name"], tag + "_" + pf.get(tag + ".jms.system.module.suffix"))
			else:
				self.assertEqual(jmsConfig["module.name"], tag)
			self.assertEqual(jmsConfig["base.name"], tag)
			if pf.get(tag + ".target.suffix"):
				self.assertEqual(jmsConfig["target.domain"], pf.get(tag + ".target.domain") + "_" + pf.get(tag + ".target.suffix"))
			else:
				self.assertEqual(jmsConfig["target.domain"], pf.get(tag + ".target.domain"))
			self.assertEqual(jmsConfig["datasource"], pf.get(tag + ".datasource"))
			# simply test that the number of queues is the same
			self.assertEqual(len(jmsConfig["queues"]), len(pf.getPartialKey(tag + ".queue.*.name")))
			# simply test that the number of topics is the same
			self.assertEqual(len(jmsConfig["topics"]), len(pf.getPartialKey(tag + ".topic.*.name")))

class TestApplicationDeploymentConfig(unittest.TestCase):
	def testGetConfig(self):
		print "TestApplicationDeploymentConfig : testGetConfig"
		pf = XmlProperties("tmp/ant-properties.xml").getAntProperties()
		for k, psc in pf.getPartialKey("*.pscname"):
			if pf.get(psc + ".technology") == "webapp":
				appConfig = ApplicationDeploymentConfig(psc, pf).getConfig()
				self.assertEqual(appConfig["domain"], "GWA_Applications")
				self.assertEqual(appConfig["deployable"], os.path.join(pf.get("package.home"), pf.get(psc + ".deployable")))
				self.assertEqual(appConfig["admin.user"], "GWAApplicationsAdmin")
				self.assertEqual(appConfig["target"], pf.get(pf.get(psc + ".target") + ".target.name"))
				self.assertEqual(appConfig["name"], psc)
				if pf.get(psc + ".securitymodel"):
					self.assertEqual(appConfig["security.model"], pf.get(psc + ".securitymodel"))
				else:
					self.assertEqual(appConfig["security.model"], "CustomRoles")

class TestCommandOutputParser(unittest.TestCase):
	def setUp(self):
		outlines = [
			"line1\n",
			"line2\n",
			"this is the error plus some more text\n",
			"some text preceding another error in the middle of some text\n",
			"and an error at the end of file"
			]
		commandOut = open("tmp/test-command-output.out", "w")
		commandOut.writelines(outlines)
		commandOut.close()
	def tearDown(self):
		try:
			os.remove("tmp/test-command-output.out")
		except:
			print "[ERROR] error while attempting to delete tmp/test-command-output.out"
	def testContains(self):
		print "TestCommandOutputParser : testContains"
		cOut = CommandOutputParser("tmp/test-command-output.out")
		self.assertEqual(cOut.contains("the error"), 1)
		self.assertEqual(cOut.contains("another error"), 1)
		self.assertEqual(cOut.contains("end of file"), 1)
		self.assertEqual(cOut.contains("not an error"),0)
		
def suite():
	suite = unittest.TestSuite()
	suite.addTest(TestDatasourceConfig("testGetConfig"))
	suite.addTest(TestJMSResourceConfig("testGetConfig"))
	suite.addTest(TestApplicationDeploymentConfig("testGetConfig"))
	suite.addTest(TestCommandOutputParser("testContains"))
	return suite