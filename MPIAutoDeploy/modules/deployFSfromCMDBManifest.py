import os, sys
from deploymetadata import DeploymentMetadata
from deploymetadata import AntCopyProject
from deploymetadata import PSCDetailsFile
from manifest import CMDBManifest
from manifest import CIManifest
from ftpsitenav import FTPSiteNav
from propertiesutils import XmlProperties


""" create the deploy file system in tmp/<release-id> from a manifest file from CMDB
"""
def processCMDBManifest(pf):
	""" create the autodeploy file system from a released repository
	supposes a structure as in svn BuildDeliverables
	"""
	repoPath = pf.get("manifest.repository.root")
	manifest = CMDBManifest(pf.get("manifest.file"))
	releaseId = manifest.getReleaseId()
	pscs = manifest.getPSCs()
	deployables = []
	# cater for different transport protocols - right now only file
	antFile = AntCopyProject("antBuildtmpFS.xml", pf.get("manifest.repository.protocol"))
	antFile.setName("createtmpfs")
	antFile.deleteDir("tmp/" + releaseId)
	# cater for getting metadata in different ways - right now only config registry
	metadata = DeploymentMetadata(pf.get("manifest.metadata.source"), pf.get("manifest.metadata.file"))
	for psc in pscs:
		deployable = metadata.getMetadataForPSC(psc)
		if deployable:
			deployables.append(deployable)
			source = repoPath + "/" + deployable["repo-path"]
			pattern = "**/**"
			target = "tmp/" + releaseId + "/" + deployable["name"] + "_" + deployable["version"]
			antFile.copyDir(source, pattern, target)
			# generic name for config folder DC-SR-ORAPP-XX_ROOT hard-coded
			antFile.copyDir(target + "/config", "**", "tmp/" + releaseId + "/DC-SR-ORAPP-XX_ROOT/PSCConfig")
	createAutodeployProperties(antFile, releaseId, deployables)
			
def processCIManifest(pf):
	""" create a file system for autodeploy from some file system - probably build-system output
	the CIManifest allows the inclusion of a pattern match so that we can get the latest build
	of a particular artefact
	"""
	manifest = CIManifest(pf.get("manifest.file"))
	releaseId = manifest.getReleaseId()
	deployPackageHome = "tmp/" + releaseId
	pscs = manifest.getPSCs()
	deployables = []
	# cater for different repository types - file/ftp
	# TODO implement file for CI
	antFile = AntCopyProject("antBuildtmpFS.xml", pf.get("manifest.repository.protocol"))
	antFile.setName("createtmpfs")
	antFile.deleteDir(deployPackageHome)
	metadata = DeploymentMetadata(pf.get("manifest.metadata.source"), pf.get("manifest.metadata.file"))
	for psc in pscs:
		deployable = metadata.getMetadataForPSC(psc)
		if deployable:
			deployables.append(deployable)
			if pf.get("manifest.repository.protocol").lower() == "ftp":
				repoHome = "ftp://" + pf.get("manifest.repository.root")
			elif pf.get("manifest.repository.protocol").lower() == "file":
				repoHome = pf.get("manifest.repository.root")
			if deployable["artefact"].find("*") > 0 and pf.get("manifest.repository.protocol").lower() == "ftp":
				ftpSite = FTPSiteNav(pf.get("manifest.repository.root"))
				latest = ftpSite.getLatestFromPattern(deployable["repo-path"], deployable["artefact"])[0]
				deployable["artefact"] = latest
			artefact = deployable["artefact"]
			sourceDir = repoHome + "/" + deployable["repo-path"]
			target = deployPackageHome + "/" + deployable["name"]
			antFile.copyFile(sourceDir, artefact, target)
	createAutodeployProperties(antFile, releaseId, deployables)
			
				
def createAutodeployProperties(antFile, packageHome, deployables):
	""" do the bits that are common to all ant files like create the properties file and set package.home
	"""
	# force protocol to file for local file copy
	antFile.copyDir(".", "psc_details.properties", "tmp/" + packageHome, protocol="file")
	antFile.property(name="package.home", value="tmp/" + packageHome)
	antFile.updateConfigProps("environment-config.properties", "package.home", "tmp/" + packageHome)
	antFile.createSetEnvFile("PACKAGE_HOME", "tmp/" + packageHome)
	antFile.writeBuildfile()
	detailsFile = PSCDetailsFile(deployables).writeFile(".")
			
	
pf = XmlProperties("tmp/ant-properties.xml").getAntProperties()
manifestSource = pf.get("manifest.source")
# cater for different kinds of manifest - right now only cmdb and ci
if manifestSource == "cmdb":
	processCMDBManifest(pf)
elif manifestSource == "ci":
	processCIManifest(pf)
else:
	raise
	
	