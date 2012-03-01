## This script will publish PSC's with customisation in OSB Domain
## Author : Surendar Patchimalla


import wlstModule
import os
import shutil
from com.bea.wli.sb.management.configuration import SessionManagementMBean
from com.bea.wli.sb.management.configuration import ALSBConfigurationMBean
from com.bea.wli.config import Ref
from com.bea.wli.config.customization import Customization
from java.io import FileInputStream 
from java.util import HashMap
from java.util import ArrayList
from java.util import HashSet

import sys
global customFile
global file 

#=======================================================================================
# Entry function to deploy project configuration and resources
#        into a ALSB domain
#=======================================================================================

def importIntoDomain():
	try:
		# Declare Variables
		sessionMBean = None
		alsbConfigurationMBean = None
		packageHome = sys.argv[4]
		
		# Connect to Server
		print 'Connecting to server: ', sys.argv[3]
		connectToServer()

		


		# Create unique session name	
		print 'Creating unique session name'
		sessionName = createSessionName()
		print 'Created session name :', sessionName

		# Create and start session
		print 'Creating SessionMBean'
		sessionMBean = getSessionMBean(sessionName)
		print 'SessionMBean started new session'

		# obtain the ALSBConfigurationMBean instance that operates
		# on the session that has just been created. Notice that
		# the name of the mbean contains the session name.
		print 'Create ALSBConfiguration'
		alsbConfigurationMBean = findService(String(ALSBConfigurationMBean.NAME + ".").concat(sessionName), ALSBConfigurationMBean.TYPE)
		print "ALSBConfiguration MBean found", alsbConfigurationMBean

		# Perform updates or read operations in the session using alsbSession
		# sys.arg[4] is the root of the package
		print 'INFO package root is ' + packageHome
		psc_list=[]
		pscProps = loadPropertiesFromFile(packageHome + "/" + 'psc_details.properties')
		print 'INFO loaded properties from ' + packageHome + "/" + 'psc_details.properties'
		try:
			file = open(packageHome + "/" + "serviceslist.properties","rb")
		except:
			print 'ERROR failed to open serviceslist.properties'
			raise
		for line in file.readlines():
			print 'INFO processing serviceslist entry ' + line.rstrip()
			# sys.arg[4] is the root of the package
			pscName = line.rstrip()
			if len(pscName) != 0:
				service_file= packageHome + "/" + pscProps.getProperty(line.rstrip() + ".deployable")
				print 'INFO deployable resolved to ' , service_file
				psc_list.append(line.rstrip() + ":" + pscProps.getProperty(line.rstrip() + ".version.label"))

				print 'Starting import of:', service_file, "on to OSB Admin Server:", sys.argv[3]
				# Read import jar file
				print 'INFO Read import jar file'
				theBytes = readBinaryFile(service_file)
				print 'INFO Import file read successfully', service_file


				# Upload Jar File
				print 'INFO Uploading Jar file'
				alsbConfigurationMBean.uploadJarFile(theBytes)
				print 'INFO Jar Uploaded'

				print 'INFO ALSB Project will now get imported'
				alsbJarInfo = alsbConfigurationMBean.getImportJarInfo()

				alsbImportPlan = alsbJarInfo.getDefaultImportPlan()
				alsbImportPlan.setPassphrase(sys.argv[5])
				operationMap=HashMap()
				operationMap = alsbImportPlan.getOperations()
				print 'INFO Default importPlan'
				printOpMap(operationMap)
				alsbImportPlan.setPreserveExistingEnvValues(false)
				alsbImportPlan.setPreserveExistingOperationalValues(false)
				print 'INFO Modified importPlan'
				printOpMap(operationMap)
				importResult = alsbConfigurationMBean.importUploaded(alsbImportPlan)
				printDiagMap(importResult.getImportDiagnostics())

				if importResult.getFailed().isEmpty() == false:
					print 'ERROR One or more resources could not be imported properly'
					raise
				
				#customize if a customization file is specified
				#affects only the created resources
				customisationFile = service_file + ".xml"
				if(os.path.exists(customisationFile)):
					print 'INFO Loading customization File', customisationFile
					iStream = FileInputStream(customisationFile)
					customizationList = Customization.fromXML(iStream)
					alsbConfigurationMBean.customize(customizationList)


		print "INFO The MBean session has been configured for the following deployments:"		
		for psc in psc_list:
			print "\t" + psc

		try:
			sessionMBean.activateSession(sessionName, "Deployed PSC's " + "\t" + "\n\t".join(psc_list))
		except:
			print "ERROR problem encountered activating the session"
			print "INFO this can happen if one or more of the managed servers are not running"
			raise
			
		print "INFO Deployment of : \n\t" + "\n\t".join(psc_list) + "\nsuccessful"
	except:
		print "ERROR Unexpected error:", sys.exc_info()[0]
		if sessionMBean != None:
			sessionMBean.discardSession(sessionName)
			file.close()
			raise


#=======================================================================================
# Utility function to print the list of operations
#=======================================================================================
def printOpMap(map):
    set = map.entrySet()
    for entry in set:
        op = entry.getValue()
        print op.getOperation(),
        ref = entry.getKey()
        print ref
    print

#=======================================================================================
# Utility function to print the diagnostics
#=======================================================================================
def printDiagMap(map):
    set = map.entrySet()
    for entry in set:
        diag = entry.getValue().toString()
        print diag
    print

#=======================================================================================
# Connect to the Admin Server
#=======================================================================================

def connectToServer():
    connect(sys.argv[1],sys.argv[2],sys.argv[3])
    domainRuntime()

#=======================================================================================
# Utility function to read a binary file
#=======================================================================================
def readBinaryFile(fileName):
    file = open(fileName, 'rb')
    bytes = file.read()
    return bytes

#=======================================================================================
# Utility function to create an arbitrary session name
#=======================================================================================
def createSessionName():
    sessionName = String("MPageImportScript-"+Long(System.currentTimeMillis()).toString())
    return sessionName

#=======================================================================================
# Utility function to load a session MBeans
#=======================================================================================
def getSessionMBean(sessionName):
    # obtain session management mbean to create a session.
    # This mbean instance can be used more than once to
    # create/discard/commit many sessions
    sessionMBean = findService(SessionManagementMBean.NAME , SessionManagementMBean.TYPE)

    # create a session
    sessionMBean.createSession(sessionName)

    return sessionMBean


#=======================================================================================
# Utility function to load a property file
#=======================================================================================
def loadPropertiesFromFile(filename):
	properties = Properties()
	input = FileInputStream(filename)
	properties.load(input)
	input.close()
	return properties
	
# IMPORT script init
try:
    # import the service bus configuration
    importIntoDomain()

except:
    print "Unexpected error: ", sys.exc_info()[0]
    dumpStack()
    raise
