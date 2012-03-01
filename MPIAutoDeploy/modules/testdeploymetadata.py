import os, sys
import unittest
from deploymetadata import ConfigRegistry
from deploymetadata import DeploymentMetadata
from deploymetadata import AntCopyProject
from deploymetadata import PSCDetailsFile

class TestConfigRegistry(unittest.TestCase):

	def testGetDeployables(self):
		print "TestConfigRegistry : testGetDeployables"
		cr = ConfigRegistry("sample_properties/ConfigRegComponents.xls")
		deployables = cr.getDeployables()
		self.assertEqual(deployables[0]["name"], "AdaptOffRampService")
		self.assertEqual(deployables[0]["version"], "02_01_00")
		self.assertEqual(deployables[0]["packaging"], "JAR")
		self.assertEqual(deployables[0]["technology"], "OSB")
		self.assertEqual(deployables[0]["artefact"], "GAT-AdaptOffRampService-build.5.jar")
		self.assertEqual(deployables[0]["repo-path"], "AdvertManagement/AdaptOffRampService/02_01_00")
		self.assertEqual(deployables[0]["deploy-target"], "")
		self.assertEqual(deployables[4]["deploy-target"], "GWIMP")
		self.assertEqual(deployables[0]["security-model"], "")
		self.assertEqual(deployables[8]["security-model"], "DDOnly")

class TestDeploymentMetadata(unittest.TestCase):
	def setUp(self):
		self.crPscs = [("ENTERPRISECONTRACTSANDSCHEMAS", "03_08_04_00"),
					("REFERENCEDATALOOKUPSERVICEIMPL", "02_04_00_00")
					]
		self.ciPscs = [("TempBookingApplication", "SNAPSHOT")]
	def testGetMetadataForPSC(self):
		print "TestDeploymentMetadata : testGetMetadataForPSC"
		md = DeploymentMetadata("cr", "sample_properties/ConfigRegComponents.xls")
		self.assertNotEqual(md.CONFIG_REGISTRY, None)
		self.assertEqual(md.CI_METADATA, None)
		self.assertNotEqual(len(md.deployables), 0)
		for i in range(len(self.crPscs)):
			deployable = md.getMetadataForPSC(self.crPscs[i])
			self.assertNotEqual(deployable, None)
			if self.crPscs[i][0] == "ENTERPRISECONTRACTSANDSCHEMAS":
				self.assertEqual(deployable["name"], "EnterpriseContractsAndSchemas")
				self.assertEqual(deployable["version"], "03_08_04")
				self.assertEqual(deployable["technology"], "OSB")
				self.assertEqual(deployable["packaging"], "JAR")
				self.assertEqual(deployable["artefact"], "EnterpriseContractsAndSchemas-trunk-build.73.jar")
				self.assertEqual(deployable["repo-path"], "EnterpriseContractsAndSchemas/03_08_04")
			if self.crPscs[i][0] == "REFERENCEDATALOOKUPSERVICEIMPL":
				self.assertEqual(deployable["name"], "ReferenceDataLookupServiceImpl")
				self.assertEqual(deployable["version"], "02_04_00")
				self.assertEqual(deployable["technology"], "Webapp")
				self.assertEqual(deployable["packaging"], "Exploded")
				self.assertEqual(deployable["artefact"], "ReferenceDataLookupServiceImpl")
				self.assertEqual(deployable["repo-path"], "ReferenceDataManagement/ReferenceDataLookupServiceImpl/02_04_00")
				self.assertEqual(deployable["deploy-target"], "GWIMP")
		md = DeploymentMetadata("ci", "sample_properties/CIDeploys.xls")
		for i in range(len(self.ciPscs)):
			deployable = md.getMetadataForPSC(self.ciPscs[i])
			if self.ciPscs[i][0] == "TempBookingApplication":
				self.assertEqual(deployable["name"], "TempBookingApplication")
				self.assertEqual(deployable["version"], "SNAPSHOT")
				self.assertEqual(deployable["technology"], "Webapp")
				self.assertEqual(deployable["packaging"], "EAR")
				self.assertEqual(deployable["artefact"], "TempBookingApplicationEar-tempbookingbuild-3.0.0-SNAPSHOT-build.*.ear")
				self.assertEqual(deployable["repo-path"], "TempBookingParentPOM/trunk")
				self.assertEqual(deployable["deploy-target"], "GWAPP")
	def testCreatePathFromMetadata(self):
		""" test that we can derive path from metadata
		problems encountered when using repo-path and os.path.join()
		"""
		print "TestDeploymentMetadata : testCreatePathFromMetadata"
		md = DeploymentMetadata("cr", "sample_properties/ConfigRegComponents.xls")
		for deployable in md.deployables:
			path = os.path.join("repoPath", deployable["repo-path"])
			print path
			path = os.path.join("tmp", "releaseId", deployable["name"])
			print path
		
class TestAntCopyProject(unittest.TestCase):
	def setUp(self):
		self.deployables=[{	"name" : "EnterpriseContractsAndSchemas",
							"version" : "03_08_04",
							"technology" : "OSB",
							"packaging" : "JAR",
							"artefact" : "EnterpriseContractsAndSchemas-trunk-build.73.jar",
							"repo-path" : "EnterpriseContractsAndSchemas/03_08_04"}, 
							{"name" : "ReferenceDataLookupServiceImpl",
							"version" : "02_04_00",
							"technology" : "Webapp",
							"packaging" : "Exploded",
							"artefact" : "ReferenceDataLookupServiceImpl",
							"repo-path" : "ReferenceDataManagement/ReferenceDataLookupServiceImpl/02_04_00/", 
							"deploy-target" : "GWIMP"}
							]
							
	def testOpenProject(self):
		print "TestAntCopyProject : testOpenProject"
		project = AntCopyProject("sample_properties/testCopyProject.xml", "file")
		self.assertEqual(project.project[0], """<?xml version="1.0" encoding="UTF-8"?>""")
		project.setName("test-ant-copy")
		self.assertEqual(project.project[1], """<project name="test-ant-copy" default="build">""")
		
	def testDisplayProject(self):
		""" kinda difficult to do strict unit testing here - just displat the results for now
		"""
		print "TestAntCopyProject : displayProject"
		project = AntCopyProject("sample_properties/testCopyProject.xml", "file")
		project.setName("display-project")
		self.assertEqual(len(self.deployables), 2)
		processed = 0
		for deployable in self.deployables:
			processed += 1
			project.copyDir("d:/repo/" + deployable["repo-path"], "/**/*.*",
							"temp/deployment-root/" + deployable["name"] + "_" + deployable["version"])
		self.assertEqual(processed, 2)
		project.copyDir(".", "psc_details.properties", "tmp/package.home")
		project.property(name="package.home", value="tmp/package-home")
		print "--- project xml ---"
		for line in project.project:
			print line
			
	def testWriteBuildfile(self):
		print "TestAntCopyProject : writeBuildfile"
		project = AntCopyProject("sample_properties/testAntCopyProject.xml", "file")
		project.setName("written-project")
		self.assertEqual(len(self.deployables), 2)
		processed = 0
		project.deleteDir("tmp/package-home")
		for deployable in self.deployables:
			processed += 1
			project.copyDir("d:/repo/" + deployable["repo-path"], "/**/*.*",
							"temp/deployment-root/" + deployable["name"] + "_" + deployable["version"])
		self.assertEqual(processed, 2)
		project.property(name="package.home", value="tmp/package-home")
		project.updateConfigProps("config.properties", "package.home", "tmp/package-home")
		project.createSetEnvFile("PACKAGE_HOME", "/tmp/package-home")
		project.writeBuildfile()

	def testWriteBuildfileFTP(self):
		print "TestAntCopyProject : testWriteBuildfileFTP"
		project = AntCopyProject("sample_properties/testAntFTPProject.xml", "ftp")
		project.setName("ftp-project")
		project.copyFile("ftp://build.gateway.michaelpage.local/TempBookingParentPOM/trunk"
						, "TempBookingApplicationEar-tempbookingbuild-3.0.0-SNAPSHOT-build.279.ear"
						, "tmp/package-root/TempBookingApplication")
		project.writeBuildfile()
	
class TestPSCDetailsFile(unittest.TestCase):

	def setUp(self):
		self.deployables=[{	"name" : "EnterpriseContractsAndSchemas",
							"version" : "03_08_04",
							"technology" : "OSB",
							"packaging" : "JAR",
							"artefact" : "EnterpriseContractsAndSchemas-trunk-build.73.jar",
							"repo-path" : "EnterpriseContractsAndSchemas/03_08_04"}, 
							{"name" : "ReferenceDataLookupServiceImpl",
							"version" : "02_04_00",
							"technology" : "Webapp",
							"packaging" : "Exploded",
							"artefact" : "ReferenceDataLookupServiceImpl",
							"repo-path" : "ReferenceDataManagement/ReferenceDataLookupServiceImpl/02_04_00/", 
							"deploy-target" : "GWIMP"}
							]
	def testCreateDetails(self):
		print "TestPSCDetailsFile : testCreateDetails"
		pscDetails = PSCDetailsFile(self.deployables)
		self.assertEqual(pscDetails.details[0], "EnterpriseContractsAndSchemas.pscname=EnterpriseContractsAndSchemas")
		self.assertEqual(pscDetails.details[1], "EnterpriseContractsAndSchemas.version.label=03_08_04")
		self.assertEqual(pscDetails.details[2], "EnterpriseContractsAndSchemas.technology=osb")
		self.assertEqual(pscDetails.details[3], "EnterpriseContractsAndSchemas.deployable=EnterpriseContractsAndSchemas_03_08_04/EnterpriseContractsAndSchemas-trunk-build.73.jar")
		self.assertEqual(pscDetails.details[4], "ReferenceDataLookupServiceImpl.pscname=ReferenceDataLookupServiceImpl")
		self.assertEqual(pscDetails.details[5], "ReferenceDataLookupServiceImpl.version.label=02_04_00")
		self.assertEqual(pscDetails.details[6], "ReferenceDataLookupServiceImpl.technology=webapp")
		self.assertEqual(pscDetails.details[7], "ReferenceDataLookupServiceImpl.target=gwimp")
		self.assertEqual(pscDetails.details[8], "ReferenceDataLookupServiceImpl.deployable=ReferenceDataLookupServiceImpl_02_04_00/ReferenceDataLookupServiceImpl")

	def testWriteFile(self):
		""" cheating again - just write the file and print it to eyeball the results
		"""
		print "TestPSCDetailsFile : testWriteFile"
		pscDetails = PSCDetailsFile(self.deployables, "testpscdetails.properties")
		pscDetails.writeFile("sample_properties")
		theFile = open("sample_properties/testpscdetails.properties", "r")
		print "--- testpscdetails.properties ---"
		for line in theFile.readlines():
			print line[:-1]

def suite():
	suite = unittest.TestSuite()
	suite.addTest(TestConfigRegistry("testGetDeployables"))
	suite.addTest(TestDeploymentMetadata("testGetMetadataForPSC"))
	suite.addTest(TestDeploymentMetadata("testCreatePathFromMetadata"))
	suite.addTest(TestAntCopyProject("testOpenProject"))
	suite.addTest(TestAntCopyProject("testDisplayProject"))
	suite.addTest(TestAntCopyProject("testWriteBuildfile"))
	suite.addTest(TestAntCopyProject("testWriteBuildfileFTP"))
	suite.addTest(TestPSCDetailsFile("testCreateDetails"))
	suite.addTest(TestPSCDetailsFile("testWriteFile"))
	return suite