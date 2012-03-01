import os, sys
from propertiesutils import XmlProperties
from propertiesutils import PropertiesFile
xmlProps = XmlProperties("tmp/ant-properties.xml")
antPropertiesFile = "tmp/ant-properties.properties"
xmlProps.transformProperties(antPropertiesFile)
apf = PropertiesFile(antPropertiesFile)
# add some validation of existence of config file
configFilePath = apf.get("config.file.path")
if os.path.isfile(configFilePath):
	epf = PropertiesFile(configFilePath)
else:
	print "[ERROR] configuration properties file " + configFilePath + " does not exist"
	sys.exit("missing environment configuration file")
# add some validation of version
envVersion = apf.get("config.file.version")
if epf.validateVersionProperty(propertyValue=envVersion):
	version = epf.get("property.file.version")
	config_file_name = apf.get("config.file.name")
	tpf = epf.createTokenisedProperties("{@", "@}", "configmaps/" + config_file_name + version + ".properties")
else:
	print "[ERROR] invalid configuration file version"
	sys.exit("invalid configuration file")