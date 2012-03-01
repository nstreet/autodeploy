from org.w3c.dom import Document
import org.w3c.dom
from javax.xml.parsers import DocumentBuilderFactory
from javax.xml.parsers import DocumentBuilder
from org.xml.sax import SAXException
from org.xml.sax import SAXParseException
from java.io import File


class XMLDoc:
	""" a wrapper to try to make parsing xml files easier
	"""
	
	def __init__(self, docFile):
		dbf = DocumentBuilderFactory.newInstance()
		db = dbf.newDocumentBuilder()
		myFile = File(docFile)
		self.doc = db.parse (myFile)
		self.doc.getDocumentElement().normalize()
		
	def getDoc(self):
		""" retutn the document
		"""
		return self.doc
		
	def getNodeList(self, doc, nodeName):
		""" return a list of named tag
		"""
		return doc.getElementsByTagName(nodeName)
		
	def getNodeValue(self, nodeList, nodeName):
		""" get the value of a tag
		note - assumes you know where you are in the doc
		"""
		try:
			nodeNameList = nodeList.getElementsByTagName(nodeName)
			element = nodeNameList.item(0)
			nodeList = element.getChildNodes()
			return nodeList.item(0).getNodeValue()
		except:
			# TODO: fail gracefully - for now, up to caller to detect error - maybe not best
			return None
			