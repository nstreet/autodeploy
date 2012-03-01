## This script will create resources in the BPM domain 
## Author : Surendar Patchimalla
##  Version : 1.1
## amended by Neil Street to make use of home-grown utility classes
## amended by Neil Street to refactor input properties, loop here instead of loopin in ant, enable specification of jndi names

import os
import commands
import shutil
from weblogic.descriptor import BeanAlreadyExistsException
from java.lang.reflect import UndeclaredThrowableException
from java.lang import System
import javax
from javax import management
from javax.management import MBeanException
from javax.management import RuntimeMBeanException
import javax.management.MBeanException
from java.lang import UnsupportedOperationException
from propertiesutils import XmlProperties
from propertiesutils import PropertiesFile
from wlstutils import DatasourceConfig


def connectToAdminServer(username, password, url):
  try:
     connect(username,password,url)
  except WLSTException:
     print 'No server is running at '+URL+', the script will start a new server'


def startTransaction():
  edit()
  startEdit()

def endTransaction():
  startEdit()
  save()
  activate(block="true")

from javax.management import InstanceAlreadyExistsException
from java.lang import Exception
from jarray import array

def create_Property(path, beanName):
  cd(path)
  try:
    print "creating mbean of type Property ... "
    theBean = cmo.lookupProperty(beanName)
    if theBean == None:
      cmo.createProperty(beanName)
  except java.lang.UnsupportedOperationException, usoe:
    pass
  except weblogic.descriptor.BeanAlreadyExistsException,bae:
    pass
  except java.lang.reflect.UndeclaredThrowableException,udt:
    pass
  except TypeError:
    prop = cmo.createProperty()
    prop.setName(beanName)
	
def create_JDBCSystemResource(path, beanName):
  print('\n Creating the required datasources \n')
  cd(path)
  try:
    print "creating mbean of type JDBCSystemResource ... "
    
    theBean = cmo.lookupJDBCSystemResource(beanName)
    if theBean == None:
      cmo.createJDBCSystemResource(beanName)
  except java.lang.UnsupportedOperationException, usoe:
    pass
  except weblogic.descriptor.BeanAlreadyExistsException,bae:
    pass
  except java.lang.reflect.UndeclaredThrowableException,udt:
    pass


def setAttributesFor_JDBCStore(datastore,db_user,db_port,sid,db_host,db_pass,url,driver):
  
  cd("/JDBCSystemResources/" + datastore + "/JDBCResource/" + datastore + "/JDBCDriverParams/" + datastore + "/Properties/" + datastore + "/Properties/user")
  print "datasource " + datastore
  print "setting attributes for mbean type JDBCStore"
  set("Value", db_user)
  set("Name", "user")
  cd("/JDBCSystemResources/" + datastore + "/JDBCResource/" + datastore + "/JDBCDriverParams/" + datastore + "/Properties/" + datastore + "/Properties/portNumber")
  set("Value", db_port)
  set("Name", "portNumber")
  cd("/JDBCSystemResources/" + datastore + "/JDBCResource/" + datastore + "/JDBCDriverParams/" + datastore + "/Properties/" + datastore + "/Properties/databaseName")
  set("Value", sid)
  set("Name", "databaseName")
  cd("/JDBCSystemResources/" + datastore + "/JDBCResource/" + datastore + "/JDBCDriverParams/" + datastore + "/Properties/" + datastore + "/Properties/serverName")
  set("Value", db_host)
  set("Name", "serverName")
  cd("/JDBCSystemResources/" + datastore + "/JDBCResource/" + datastore + "/JDBCDriverParams/" + datastore )
  print "setting attributes for mbean type JDBCDriverParams"
  set("Password", db_pass )
  set("DriverName", driver)
  set("UseXaDataSourceInterface", "true")
  set("Url", url)


def setAttributesForJDBCDataSource(datasource,clusterList):
	cd("/JDBCSystemResources/" + datasource)
	print "setting attributes for mbean type JDBCSystemResource"
	refBeans = []
	print "[INFO] configuring targets"
	for clustername in clusterList:
		print "[INFO] configuring cluster " + clustername
		refBeans.append(getMBean("/Clusters/" + clustername ))
	theValue = jarray.array(refBeans, Class.forName("weblogic.management.configuration.TargetMBean"))
	cmo.setTargets(theValue)

def setAttributesJDBCDataSourceParams(dsConfig):
	datasourcename = dsConfig["name"]
	cd("/JDBCSystemResources/" + datasourcename + "/JDBCResource/" + datasourcename + "/JDBCDataSourceParams/" + datasourcename )
	print "setting attributes for mbean type JDBCDataSourceParams"
	set("GlobalTransactionsProtocol", "TwoPhaseCommit")
	jndiNames = dsConfig["jndi"]
	jndiNameString = ":".join(dsConfig["jndi"])
	print "[INFO] setting JNDINames " + jndiNameString
	set("JNDINames", jarray.array(jndiNames, String))


def setAttributes_JDBCDataSource(datasource):
  cd("/JDBCSystemResources/"+ datasource + "/JDBCResource/" + datasource)
  print "setting attributes for mbean type JDBCDataSource"
  set("Name", datasource)


def setAttributes_JDBCXAParams(datasource):
  cd("/JDBCSystemResources/" + datasource + "/JDBCResource/" + datasource + "/JDBCXAParams/" + datasource)
  print "setting attributes for mbean type JDBCXAParams"
  set("RecoverOnlyOnce", "false")
  set("KeepLogicalConnOpenOnRelease", "false")
  set("ResourceHealthMonitoring", "true")
  set("XaRetryDurationSeconds", "0")
  set("XaEndOnlyOnce", "false")
  set("RollbackLocalTxUponConnClose", "false")
  set("KeepXaConnTillTxComplete", "true")
  set("XaTransactionTimeout", "3600")
  set("XaRetryIntervalSeconds", "60")
  set("XaSetTransactionTimeout", "true")
  set("NeedTxCtxOnClose", "false")


def setAttributes_JDBCConnectionPoolParams(datasourcename):
  cd("/JDBCSystemResources/" + datasourcename + "/JDBCResource/" + datasourcename + "/JDBCConnectionPoolParams/" + datasourcename)
  print "setting attributes for mbean type JDBCConnectionPoolParams"
  set("ProfileType", "255")
  set("StatementCacheSize", "10")
  set("TestConnectionsOnReserve", "true")
  set("RemoveInfectedConnections", "true")
  set("InactiveConnectionTimeoutSeconds", "0")
  set("TestTableName", " SQL SELECT getdate()")
  set("LoginDelaySeconds", "0")
  set("PinnedToThread", "false")
  set("IgnoreInUseConnectionsEnabled", "true")
  set("SecondsToTrustAnIdlePoolConnection", "10")
  set("ConnectionReserveTimeoutSeconds", "10")
  set("JDBCXADebugLevel", "10")
  set("TestFrequencySeconds", "120")
  set("ShrinkFrequencySeconds", "900")
  set("StatementTimeout", "-1")
  set("MaxCapacity", "300")
  set("HighestNumWaiters", "2147483647")
  set("InitialCapacity", "50")
  set("StatementCacheType", "LRU")
  set("ConnectionCreationRetryFrequencySeconds", "0")
  set("CapacityIncrement", "10")
  set("ProfileHarvestFrequencySeconds", "300")

def setAttributesForDS(clusterList, datasourcename):
	print "[INFO] setting attributes for datasource"
	cd("/JDBCSystemResources/"+ datasourcename)
	refBeans = []
	print "[INFO] configuring clusters"
	for clustername in clusterList:
		print "[INFO] configuring cluster " + clustername
		refBeans.append(getMBean("/Clusters/" + clustername))
	theValue = jarray.array(refBeans, Class.forName("weblogic.management.configuration.TargetMBean"))
	cmo.setTargets(theValue)


# Create the JDBC resources 
def create_datasource(dsConfig):
	try:
		datasourcename = dsConfig["name"]
		create_JDBCSystemResource("/", datasourcename)
		create_Property("/JDBCSystemResources/" + datasourcename + "/JDBCResource/" + datasourcename + "/JDBCDriverParams/" + datasourcename + "/Properties/" + datasourcename, "user")
		create_Property("/JDBCSystemResources/" + datasourcename + "/JDBCResource/" + datasourcename + "/JDBCDriverParams/" + datasourcename + "/Properties/" + datasourcename, "portNumber")
		create_Property("/JDBCSystemResources/" + datasourcename + "/JDBCResource/" + datasourcename + "/JDBCDriverParams/" + datasourcename + "/Properties/" + datasourcename, "databaseName")
		create_Property("/JDBCSystemResources/" + datasourcename + "/JDBCResource/" + datasourcename + "/JDBCDriverParams/" + datasourcename + "/Properties/" + datasourcename, "serverName")
		setAttributes_JDBCDataSource(datasourcename)
		setAttributesFor_JDBCStore(datasourcename,
									dsConfig["user"],
									dsConfig["port"],
									dsConfig["dbName"],
									dsConfig["host"],
									dsConfig["password"],
									dsConfig["url"],
									dsConfig["driver"])
		setAttributesForDS(dsConfig["target"],datasourcename)
		setAttributesForJDBCDataSource(datasourcename,dsConfig["target"])
		setAttributesJDBCDataSourceParams(dsConfig)
		setAttributes_JDBCConnectionPoolParams(datasourcename)
		setAttributes_JDBCXAParams(datasourcename)


		
  	except java.lang.UnsupportedOperationException, usoe:
    		print "Could not create JDBC resource "
    		pass
  	except weblogic.descriptor.BeanAlreadyExistsException,bae:
    		print "Could not create JDBC resource"
    		pass
  	except java.lang.reflect.UndeclaredThrowableException,udt:
    		print "Could not create JDBC resource"
    		pass
			
# IMPORT script init
try:
	xmlp = XmlProperties("tmp/ant-properties.xml")
	pf = xmlp.getAntProperties()

	# get a list of datasource unique ids
	dsNameProps = pf.getPartialKey("*.db.host")
	dsIds = []
	for key, value in dsNameProps:
		dsIds.append(key.split(".")[0])

	for id in dsIds:

		dsConfig = DatasourceConfig(id, pf).getConfig()
		dsname=dsConfig["name"]
		print "[INFO] creating datasource " + dsname


		targetList = dsConfig["target"]
		# if there are multiple targets we are assuming that they are on the same admin server
		target = targetList[0]
		connected = false
		print "[INFO] resolving admin server for target " + target
		# find the admin server for the target
		for k, v in pf.getPartialKey("*.target.name"):
			if v == target:
				adminPrefix = pf.get(k.split(".")[0] + ".admin.server")
				print "Getting Details for " + target
				username=pf.get(adminPrefix + ".admin_user")
				password=pf.get(adminPrefix + ".admin_password")
				url=pf.get(adminPrefix + ".admin_url")
				connectToAdminServer(username,password,url)
				connected = true
		
		if connected:
			startTransaction()
			create_datasource(dsConfig)
			endTransaction()
		else:
			print "[ERROR] Unable to resolve target " + target

except:
    print "Unexpected error: ", sys.exc_info()[0]
    dumpStack()
    raise
	