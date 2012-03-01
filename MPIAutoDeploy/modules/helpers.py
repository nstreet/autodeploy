import os, sys
from org.apache.poi.hssf.usermodel import *
from java.io import FileInputStream

class Set:
	""" convenience class for deriving a unique list from a given list
	could be extended to do stuff like intersection and union if required
	"""
	def __init__(self, list):
		self.setList = []
		for item in list:
			already = 0
			for got in self.setList:
				if got == item:
					already = 1
					break
			if not already:
				self.setList.append(item)
	def contains(self, yourItem):
		for item in self.setList:
			if item == yourItem:
				return 1
		return 0
	def getCount(self):
		return len(self.setList)

class RegexStuff:
	def regexFromWildcard(self, wildcardString):
		regex = ""
		for i in range(len(wildcardString)):
			if wildcardString[i] == "*":
				regex += ".*"
			elif wildcardString[i] == ".":
				regex += "\."
			else:
				regex += wildcardString[i]
		return regex

class BinaryFile:
	def __init__(self, fileName):
		self.fileName = fileName
		ifile = open(fileName, "rb")
		self.contents = ifile.read()
		ifile.close()
	def getBytes(self):
		return self.contents
		
class SpreadSheet:
	""" wrapper for a spreadsheet
	TODO do we want to extend this?
	"""
	def __init__(self, wbFile):
		fis = FileInputStream(wbFile)
		self.wb = HSSFWorkbook(fis)
	
	def getSpreadSheet(self):
		return self.wb

