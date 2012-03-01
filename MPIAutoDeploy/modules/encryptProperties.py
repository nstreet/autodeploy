""" take a list of properties files and open them
"""
import sys, os
from propertiesutils import PropertiesFile
from propertiesutils import NonEncryptedPropertiesFile
from loggingutils import SimpleReporter
from propertiesutils import XmlProperties
logger = SimpleReporter()
xpf = XmlProperties("tmp/ant-properties.xml")
xpf.transformProperties("tmp/ant-properties.properties")
pf = PropertiesFile("tmp/ant-properties.properties")
fileList = pf.get("property.files").split(",")
for file in fileList:
	logger.report("Processing %s" % (file))
	enc = NonEncryptedPropertiesFile(file)