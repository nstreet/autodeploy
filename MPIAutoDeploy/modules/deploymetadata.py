from helpers import Set
from helpers import SpreadSheet

class ConfigRegistry:
	""" convenience wrapper to enable the interim use of the existing config registry spreadsheet 
	to acquire metadata for deployment
	"""
	def __init__(self, wbFile):
		self.wb = SpreadSheet(wbFile).getSpreadSheet()
		
	def getDeployables(self):
		""" return a list of dicts
		name : pscname
		version : version
		technology : technology
		packaging : packaging
		repo-path : path in repo
		artefact : artefact name
		target : deploy target
		security-model : security model
		"""
		sheet = self.wb.getSheet("Deployables")
		rows = sheet.getPhysicalNumberOfRows()
		deployables = []
		for i in range(rows):
			if not i == 0:
				row = sheet.getRow(i)
				deployable = {}
				if row:
					pscVersion = row.getCell(1)
					tech = row.getCell(2)
					repoPath = row.getCell(5)
					if pscVersion and tech and repoPath:
						pscBits = pscVersion.getStringCellValue().split("_")
						deployable["name"] = pscBits[0]
						deployable["version"] = "_".join(pscBits[1:])
						tech = row.getCell(2)
						deployable["technology"] = tech.getStringCellValue().strip()
						package = row.getCell(3)
						if package:
							deployable["packaging"] = package.getStringCellValue().strip()
						artefact = row.getCell(4)
						if artefact:
							deployable["artefact"] = artefact.getStringCellValue().strip()
						repoPath = row.getCell(5)
						repoPathValue = repoPath.getStringCellValue().strip()
						if repoPathValue.endswith("/"):
							deployable["repo-path"] = repoPathValue[:-1]
						else:
							deployable["repo-path"] = repoPathValue
						target = row.getCell(6)
						if target:
							deployable["deploy-target"] = target.getStringCellValue().strip()
						secModel = row.getCell(7)
						if secModel:
							deployable["security-model"] = secModel.getStringCellValue().strip()
						deployables.append(deployable)
		return deployables

class CIMetadata:
	""" convenience wrapper to use a simple spreadsheet 
	to acquire metadata for deployment
	TODO: refactor this
	"""
	def __init__(self, wbFile):
		self.wb = SpreadSheet(wbFile).getSpreadSheet()
		
	def getDeployables(self):
		""" return a list of dicts
		name : pscname
		version : version
		technology : technology
		packaging : packaging
		repo-path : path in repo
		artefact : artefact name
		target : deploy target
		security-model : security model
		"""
		sheet = self.wb.getSheet("Deployables")
		rows = sheet.getPhysicalNumberOfRows()
		deployables = []
		for i in range(rows):
			if not i == 0:
				row = sheet.getRow(i)
				deployable = {}
				if row:
					name = row.getCell(1)
					version = row.getCell(0)
					if name and version:
						deployable["name"] = row.getCell(1).getStringCellValue().strip()
						deployable["version"] = row.getCell(0).getStringCellValue().strip()
						deployable["technology"] = row.getCell(2).getStringCellValue().strip()
						deployable["packaging"] = row.getCell(3).getStringCellValue().strip()
						deployable["repo-path"] = row.getCell(5).getStringCellValue().strip()
						deployable["artefact"] = row.getCell(4).getStringCellValue().strip()
						target = row.getCell(6)
						if target:
							deployable["deploy-target"] = target.getStringCellValue().strip()
						secModel = row.getCell(7)
						if secModel:
							deployable["security-model"] = secModel.getStringCellValue().strip()
						
						deployables.append(deployable)
		return deployables

class DeploymentMetadata:
	def __init__(self, metadataSource, file=None):
		""" interface class to provide a dict object of metadata for a given psc-name, psc-version pair
		if the source of the metadata is the config registry, we get all of the metadata in the config registry
		at init time (just parse the spreadsheet the once)
		"""
		self.CI_METADATA = None
		self.CONFIG_REGISTRY = None
		self.source = metadataSource.lower()
		if self.source == "cr":
			self.CONFIG_REGISTRY = 1
		if self.source == "ci":
			self.CI_METADATA = 1
		self.file = file
		if self.CONFIG_REGISTRY:
			self.deployables = ConfigRegistry(self.file).getDeployables()
		if self.CI_METADATA:
			self.deployables = CIMetadata(self.file).getDeployables()
	
	def getMetadataForPSC(self, psc):
		if self.CONFIG_REGISTRY:
			deployable = self._getMetadataFromConfigRegistry(psc)
		if self.CI_METADATA:
			deployable = self._getDeployableFromMyDeployables(psc)
		return deployable
		
	def _getMetadataFromConfigRegistry(self, psc):
		""" return the deployable dict from config registry
		manifest versions from cmdb have 4 levels - config registry has 3
		"""
		manifestName = psc[0]
		manifestVersion = psc[1]
		# strip off the last version level
		crVersion = "_".join(manifestVersion.split("_")[:-1])
		myPsc = (manifestName, crVersion)
		deployable = self._getDeployableFromMyDeployables(myPsc)
		return deployable
			
	def _getDeployableFromMyDeployables(self, psc):
		matched = 0
		for deployable in self.deployables:
			if deployable["name"].lower() == psc[0].lower() and deployable["version"] == psc[1]:
				matched = 1
				break
		if matched:
			return deployable
		else:
			return None
		
class AntCopyProject:
	def __init__(self, projectFile, protocol):
		""" create an ant project that will be used to populate the deploy file system
		"""
		self.PROTOCOL_FILE = None
		self.PROTOCOL_FTP = None
		if protocol.lower() == "file":
			self.PROTOCOL_FILE = 1
		if protocol.lower() == "ftp":
			self.PROTOCOL_FTP = 1
		self.projectFile = projectFile
		self.project = []
		self.project.append('<?xml version="1.0" encoding="UTF-8"?>')

	def setName(self, name):
		self.project.append('<project name="' + name + '" default="build">')
		self.project.append('<target name="build">')

	def copyDir(self, sourceDir, sourcePattern, target, protocol=None):
		if self.PROTOCOL_FILE or protocol == "file":
			self._copyDirFile(sourceDir, sourcePattern, target)
	
	def _copyDirFile(self, sourceDir, sourcePattern, target):
		self.project.append('<mkdir dir="' + target + '"/>')
		self.project.append('<copy todir="' + target + '" failonerror="false">')
		self.project.append('<fileset dir="' + sourceDir + '" includes="' + sourcePattern + '"/>')
		self.project.append('</copy>')

	def copyFile(self, sourceDir, sourceFile, target):
		if self.PROTOCOL_FTP:
			self._copyFileFTP(sourceDir, sourceFile, target)
	
	def _copyFileFTP(self, sourceDir, sourceFile, target):
		self.project.append('<mkdir dir="' + target + '"/>')
		self.project.append('<get src="' + sourceDir + '/' + sourceFile + '" dest="' + target + '/' + sourceFile + '"/>')

	def updateConfigProps(self, file, property, value):
		self.project.append('<echo message="[INFO] updating ' + file + '"/>')
		self.project.append('<echo message="[INFO] with ' + property + '=' + value + '"/>')
		self.project.append('<propertyfile file="' + file + '" comment="THIS FILE HAS BEEN EDITED TO ADD ' + property + '=' + value + '">')
		self.project.append('<entry key="' + property + '" value="' + value + '"/>')
		self.project.append('</propertyfile>')

	def createSetEnvFile(self, envVariable, value):
		self.project.append('<echo message="[INFO] creating cmd file set' + envVariable + '.cmd to set ' + envVariable + '=' + value + '"/>')
		self.project.append('<echo file="set' + envVariable + '.cmd">')
		self.project.append('@echo off')
		self.project.append('echo setting environment variable ' + envVariable + '=' + value)
		self.project.append('set ' + envVariable + '=' + value)
		self.project.append('</echo>')
		
	def deleteDir(self, dir):
		self.project.append('<delete dir="' + dir + '"/>')
		
	def property(self, name, value):
		self.project.append('<property name="' + name + '" value="' + value + '"/>')
		
	def writeBuildfile(self):
		buildFile = open(self.projectFile, "w")
		for line in self.project:
			buildFile.writelines(line + "\n")
		buildFile.writelines("</target>\n</project>")
		buildFile.close()
		
class PSCDetailsFile:
	def __init__(self, deployables, detailsFile=None):
		""" turn a set of deployables dicts into a standard psc_details file
		"""
		if detailsFile:
			self.detailsFile = detailsFile
		else:
			self.detailsFile = "psc_details.properties"
		self.deployables = deployables
		self.details = []
		# filter the technologies that we create psc_details entries for
		pscDetailsTechnologies = Set(["webapp", "osb"])
		for deployable in self.deployables:
			if pscDetailsTechnologies.contains(deployable["technology"].lower()):
				self.details.append(deployable["name"] + ".pscname=" + deployable["name"])
				self.details.append(deployable["name"] + ".version.label=" + deployable["version"])
				self.details.append(deployable["name"] + ".technology=" + deployable["technology"].lower())
				# use the presence of the target member to drive the creation of the property
				# just in case we have targets with other technologies (currently only webapp)
				target = None
				try:
					target = deployable["deploy-target"].lower()
				except:
					pass
				if target:
					self.details.append(deployable["name"] + ".target=" + target)
				self.details.append(deployable["name"] + ".deployable=" + deployable["name"] + "_" + deployable["version"] + "/" + deployable["artefact"])
			
	def writeFile(self, packageRoot):
		detailsFile = open(packageRoot + "/" + self.detailsFile, "w")
		detailsFile.writelines("\n".join(self.details))
		detailsFile.close()
		