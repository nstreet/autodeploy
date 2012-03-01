""" get all of the properties files in the current directory and open them
"""
import os
from propertiesutils import NonEncryptedPropertiesFile
from loggingutils import SimpleReporter
logger = SimpleReporter()
listDir = os.listdir(".")
for entry in listDir:
	if os.path.isfile(entry):
		if entry.endswith(".properties"):
			logger.report("Processing %s" % (entry))
			pf = NonEncryptedPropertiesFile(entry)