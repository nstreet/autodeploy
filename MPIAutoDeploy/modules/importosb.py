## This script will publish PSC's with customisation in OSB Domain
## Author : Surendar Patchimalla
## amended by Neil Street to use home-grown utility classes


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
from propertiesutils import PropertiesFile
from wlstutils import ServerConnection
from helpers import BinaryFile
from propertiesutils import XmlProperties
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
		xpf = XmlProperties("tmp/ant-properties.xml")
		xpf.transformProperties("tmp/ant-properties.properties")
		pf = PropertiesFile("tmp/ant-properties.properties")
		packageHome = pf.get("package.home")
		
		# Connect to Server
		print 'Connecting to server: ', pf.get("osbadm.adminUrl")
	#		connectToServer()
		connect(pf.get("osbadm.admin_user"), pf.get("osbadm.admin_password"), pf.get("osbadm.adminUrl"))
		domainRuntime()


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
		pscProps = PropertiesFile(packageHome + "/" + 'psc_details.properties')
		print 'INFO loaded properties from ' + packageHome + "/" + 'psc_details.properties'
		pscNames = pscProps.getPartialKey("*.pscname")
		serviceProps = []
		for k, v in pscNames:
			if pscProps.get(v + ".technology") == "osb":
				serviceProps.append((k, v))
		
		for k, pscName in serviceProps:
			print 'INFO processing serviceslist entry ' + pscName
			# sys.arg[4] is the root of the package
			if len(pscName) != 0:
				service_file= packageHome + "/" + pscProps.get(pscName + ".deployable")
				print 'INFO deployable resolved to ' , service_file
				psc_list.append(pscName + ":" + pscProps.get(pscName + ".version.label"))

				print 'Starting import of:', service_file, "on to OSB Admin Server:", pf.get("osbimp.adminUrl")

				# Read import jar file
				print 'INFO Read import jar file'
				theBytes = BinaryFile(service_file).getBytes()
				print 'INFO Import file read successfully', service_file


				# Upload Jar File
				print 'INFO Uploading Jar file'
				alsbConfigurationMBean.uploadJarFile(theBytes)
				print 'INFO Jar Uploaded'

				print 'INFO ALSB Project will now get imported'
				alsbJarInfo = alsbConfigurationMBean.getImportJarInfo()

				alsbImportPlan = alsbJarInfo.getDefaultImportPlan()
				# we are currently running all WLST with the same keystore
				# if this changes we will have to get more clever here
				alsbImportPlan.setPassphrase(pf.get("oradm.keystore.passphrase"))
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
		deployMessage = "Deployed PSC's " + "\t" + "\n\t".join(psc_list)
		try:
			sessionMBean.activateSession(sessionName, deployMessage)
		except:
			print "ERROR problem encountered activating the session"
			print "INFO this can happen if one or more of the managed servers are not running"
			raise
			
		print "INFO Deployment of : \n\t" + "\n\t".join(psc_list) + "\nsuccessful"
	except Exception, e:
		print "ERROR Unexpected error:", sys.exc_info()[0]
		print e
		if sessionMBean:
			sessionMBean.discardSession(sessionName)
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

	
# IMPORT script init
try:
    # import the service bus configuration
    importIntoDomain()

except:
    print "Unexpected error: ", sys.exc_info()[0]
    dumpStack()
    raise
