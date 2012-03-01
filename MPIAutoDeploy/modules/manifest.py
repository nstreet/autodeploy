from xmldocutils import XMLDoc
from helpers import SpreadSheet
class DeploymentManifest:

	def getPSCs(self):
		""" return a list of psc-name, version tuples
		"""
		return self.pscList
		
	def getReleaseId(self):
		""" return the release id
		included with every psc element so assuming thay are all the same
		this links to CMDB behaviour
		"""
		return self.releaseId

class CMDBManifest(DeploymentManifest):
	def __init__(self, fileName):
		self.xml = XMLDoc(fileName)
		self.xmlDoc = self.xml.getDoc()
		self.releaseId = None
		self.pscList = []
		# get the psc nodes (instance of com.sun.org.apache.xerces.internal.dom.DeepNodeListImpl)
		pscs = self.xml.getNodeList(self.xmlDoc, "psc")
		for i in range(pscs.getLength()):
			id = self.xml.getNodeValue(pscs.item(i), "id")
			pscName = self.xml.getNodeValue(pscs.item(i), "name")
			psc_Version = self.xml.getNodeValue(pscs.item(i), "version")
			# strip the leading underscore if there is one
			if psc_Version.startswith("_"):
				idx = 1
			else:
				idx = 0
			pscVersion = "_".join(psc_Version.split("_")[idx:])
			self.pscList.append((pscName, pscVersion))
		self.releaseId = id

class CIManifest(DeploymentManifest):
	def __init__(self, fileName):
		self.wb = SpreadSheet(fileName).getSpreadSheet()
		sheet = self.wb.getSheet("DeploymentId")
		row = sheet.getRow(0)
		cell = row.getCell(0)
		self.releaseId = cell.getStringCellValue()
		sheet = self.wb.getSheet("Deployables")
		rows = sheet.getPhysicalNumberOfRows()
		self.pscList = []
		for i in range(rows):
			if i > 0:
				row = sheet.getRow(i)
				if row:
					name = row.getCell(1).getStringCellValue()
					version = row.getCell(0).getStringCellValue()
					self.pscList.append((name, version))
		
