import os, sys
from helpers import Set
from helpers import RegexStuff
import re
from org.w3c.dom import Document
import org.w3c.dom
from javax.xml.parsers import DocumentBuilderFactory
from javax.xml.parsers import DocumentBuilder
from org.xml.sax import SAXException
from org.xml.sax import SAXParseException
from java.io import File
from crypto import EncryptedPassword
from loggingutils import SimpleReporter

class PropertiesFile:
	""" utility class to handle property files. the provided WLST Properties class does't really do what we need
	"""
	def __init__(self, filename, log=None):
		""" initialise dictionary of valid properties and list of all file entries
		"""
		self.log = log
		try:
			pFile = open(filename, "r")
		except:
			self.report("error opening " + filename, "e")
			raise
		self.properties = {}
		self.allEntries = pFile.readlines()
		pFile.close()
		ep = EncryptedPassword()
		for entry in self.allEntries:
			if entry.strip().startswith("#"):
				# comment line
				pass
			elif entry.strip() == "":
				# blank line
				pass
			else:	
				pos = entry.find("=")
				if pos < 0:
					key = entry.strip()
					value = ""
				else:
					key = entry[:pos]
					if key.find("password") > 0:
						try:
							value = ep.decrypt(entry[pos + 1:].rstrip())
						except:
							value = entry[pos + 1:].rstrip()
					else:
						value = entry[pos + 1:].rstrip()
				self.properties[key] = value
		
	def get(self, propertyKey):
		""" simply get property by key
		"""
		try:
			value = self.properties[propertyKey]
		except KeyError:
			self.report(propertyKey + " does not exist", "w")
			return None
		return value

	def getPartialKey(self, match):
		""" match partial keys
		"""
		rs = RegexStuff()
		pattern = rs.regexFromWildcard(match)
		matches=[]
		for key in self.properties.keys():
			if re.match(pattern, key):
				if key.count(".") == match.count("."):
					matches.append((key, self.properties[key]))
		return matches
		
	def createTokenisedProperties(self, startToken, endToken, outputFile=None, ignoreKeys=["property.file.version"]):
		""" specifically for creating a replace map to be used in ant
		takes a properties file of token=value and turns it into ${start-token}token${end-token}=value
		takes a list of keys to ignore i.e not transform the key
		"""
		ignore = Set(ignoreKeys)
		tokenisedProperties = []
		for entry in self.allEntries:
			if entry.strip().startswith("#") or entry.strip() == "":
				tokenisedProperties.append(entry.rstrip())
			else:
				pos = entry.find("=")
				if pos < 0:
					key = entry.strip()
					value = ""
				else:
					key = entry[:pos].strip()
					value = entry[pos + 1:].strip()
				if ignore.contains(key):
					tokenisedProperties.append(key + "=" + value)
				else:
					tokenisedProperties.append(startToken + key + endToken + "=" + value.replace("\\", r"\\"))
		if outputFile:
			of = open(outputFile, "w")
			for property in tokenisedProperties:
				of.writelines(property + "\n")
			of.close()
			return outputFile
		else:
			return tokenisedProperties
	
	def validateVersionProperty(self, propertyKey="property.file.version", propertyValue=None):
		""" check for the presence of of a version property and, optionally, its value
		"""
		version = self.get(propertyKey)
		if not version:
			self.report("missing property " + propertyKey, "e")
			return 0
		else:
			if propertyValue:
				if version == propertyValue:
					return 1
				else:
					self.report("property file version " + version + " does not match " + propertyValue, "e")
					return 0
			else:
				return 1
	
	def report(self, errString, level="i"):
		levels = {"i" : "[INFO] ", "w" : "[WARN] ", "e" : "[ERROR] "}
		if self.log:
			log.log(level, errString)
		else:
			print levels[level] + errString

class NonEncryptedPropertiesFile:
	""" transform any non encrypted password properties int encrypted form
	return a PropertiesFile object of the new (rewritten) file
	"""
	
	def __init__(self, fileName):
		ep = EncryptedPassword()
		self.rep = SimpleReporter()
		self.fileName = fileName
		try:
			inf = open(fileName, "r")
		except:
			self.rep.report("problem opening %s" % (fileName), "e")
		self.origProps = inf.readlines()
		inf.close()
		newLines = []
		dirtyFile = 0
		for line in self.origProps:
			if line.strip().startswith("#"):
				newLines.append(line)
				continue
			lineBits = line.split("=")
			if len(lineBits) < 2:
				newLines.append(line)
				continue
			if not lineBits[0].find("password") > -1:
				newLines.append(line)
				continue
			key = lineBits[0]
			origVal = "=".join(lineBits[1:]).rstrip()
			try:
				ep.decrypt(origVal)
				newLines.append(line)
			except:
				newVal = ep.encrypt(origVal)
				newLines.append(key + "=" + newVal + "\n")
				dirtyFile = 1
		if dirtyFile:
			outf = open(fileName, "w")
			outf.writelines(newLines)
			outf.close()
	def getFile(self):
		pf = PropertiesFile(self.fileName)
		return pf
			
class XmlProperties:
	def __init__(self, inputFile):

		dbf = DocumentBuilderFactory.newInstance()
		db = dbf.newDocumentBuilder()
		myFile = File(inputFile)
		self.doc = db.parse (myFile)
		self.doc.getDocumentElement ().normalize ()
		self.reporter = Reporter()
		self.reporter.report("xml properties file " + inputFile)
		self.reporter.report("root element " + self.doc.getDocumentElement().getNodeName())
		
	def transformProperties(self, outputFile):

		properties = self.doc.getElementsByTagName("property")
		num = properties.getLength()
		self.reporter.report("transforming xml properties to " + outputFile)
		self.reporter.report("number of properties = %i" % (num))
		self.propertyList = []
		ofile = open(outputFile, "w")
		for i in range(num):
			el = properties.item(i)
			attMap = el.getAttributes()
			node = attMap.getNamedItem("name")
			name = node.getTextContent()
			node = attMap.getNamedItem("value")
			value = node.getTextContent()
			kv = name + "=" + value
			self.propertyList.append(kv)
			ofile.writelines(kv + "\n")
		ofile.close()
		self.pf = PropertiesFile(outputFile)

	def getAntProperties(self):
		""" redesign of transformProperties to return a PropertiesFile object
		that is the transformed ant properties
		"""
		self.transformProperties("tmp/ant-properties.properties")
		return self.pf		

class Reporter:
	def __init__(self, log=None):
		self.log = log

	def report(self, errString, level="i"):
		levels = {"i" : "[INFO] ", "w" : "[WARN] ", "e" : "[ERROR] "}
		if self.log:
			log.log(level, errString)
		else:
			print levels[level] + errString
