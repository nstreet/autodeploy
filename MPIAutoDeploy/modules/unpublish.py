## This script will unpublish PSC's from OSB Domain
## Author : Surendar Patchimalla

if __name__ == '__main__': 
    from wlstModule import *#@UnusedWildImport
from java.util import Collections
from com.bea.wli.sb.management.configuration import SessionManagementMBean
from com.bea.wli.sb.management.configuration import ALSBConfigurationMBean
import com.bea.wli.config.Ref
from java.io import FileInputStream 
import sys
global file 

#=======================================================================================
# Entry function to deploy project configuration and resources
#        into a ALSB domain
#=======================================================================================

def unpublish():
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

		try:
			file = open(packageHome + "/" + "osbundeployables.properties","rb")
		except:
			print 'ERROR failed to open osbundeployables.properties'
			raise
		for line in file.readlines():
			print 'INFO removing ' + line.rstrip()
			pscName = line.rstrip()
			if len(pscName) != 0:
				psc_list.append(pscName)
				projectRef = com.bea.wli.config.Ref(com.bea.wli.config.Ref.PROJECT_REF, com.bea.wli.config.Ref.DOMAIN, pscName)
				if alsbConfigurationMBean.exists(projectRef):
					alsbConfigurationMBean.delete(Collections.singleton(projectRef))


		print "INFO This session has removed for the following projects:" 		
		for psc in psc_list:
			print "\t" + psc

		try:
			sessionMBean.activateSession(sessionName, "Deleted projects" + "\t" + "\n\t".join(psc_list))
		except:
			print "ERROR problem encountered activating the session"
			print "INFO this can happen if one or more of the managed servers are not running"
			raise
			

	except:
		print "ERROR Unexpected error:", sys.exc_info()[0]
		if sessionMBean != None:
			sessionMBean.discardSession(sessionName)
			file.close()
			raise



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
    sessionName = String("MPageUnpublishScript-"+Long(System.currentTimeMillis()).toString())
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
    unpublish()

except:
    print "Unexpected error: ", sys.exc_info()[0]
    dumpStack()
    raise
