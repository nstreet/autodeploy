## This script will create resources in the BPM domain 
## Author : Surendar Patchimalla
##  Version : 0.1

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
from java.io import FileInputStream
from propertiesutils import XmlProperties
from wlstutils import JMSResourceConfig

_serverNames=[]
global q_target

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

def create_JMSSystemResource(path, beanName):
  cd(path)
  try:
    print "creating mbean of type JMSSystemResource ... "
    theBean = cmo.lookupJMSSystemResource(beanName)
    if theBean == None:
      cmo.createJMSSystemResource(beanName)
  except java.lang.UnsupportedOperationException, usoe:
    pass
  except weblogic.descriptor.BeanAlreadyExistsException,bae:
    pass
  except java.lang.reflect.UndeclaredThrowableException,udt:
    pass
	
def create_SubDeployment(path, beanName):
  cd(path)
  try:
    print "creating mbean of type SubDeployment ... "
    theBean = cmo.lookupSubDeployment(beanName)
    if theBean == None:
      cmo.createSubDeployment(beanName)
  except java.lang.UnsupportedOperationException, usoe:
    pass
  except weblogic.descriptor.BeanAlreadyExistsException,bae:
    pass
  except java.lang.reflect.UndeclaredThrowableException,udt:
    pass

	
def create_ConnectionFactory(path, beanName):
  cd(path)
  try:
    print "creating mbean of type ConnectionFactory ... "
    theBean = cmo.lookupConnectionFactory(beanName)
    if theBean == None:
      cmo.createConnectionFactory(beanName)
  except java.lang.UnsupportedOperationException, usoe:
    pass
  except weblogic.descriptor.BeanAlreadyExistsException,bae:
    pass
  except java.lang.reflect.UndeclaredThrowableException,udt:
    pass

def create_UniformDistributedQueue(path, beanName):
  cd(path)
  try:
    print "creating mbean of type UniformDistributedQueue ... "
    theBean = cmo.lookupUniformDistributedQueue(beanName)
    if theBean == None:
      cmo.createUniformDistributedQueue(beanName)
  except java.lang.UnsupportedOperationException, usoe:
    pass
  except weblogic.descriptor.BeanAlreadyExistsException,bae:
    pass
  except java.lang.reflect.UndeclaredThrowableException,udt:
    pass

def setAttributes_SecurityParams(factory,module):
  cd("/JMSSystemResources/"+ module + "/JMSResource/"+ module + "/ConnectionFactories/" + factory + "/SecurityParams/" + factory)
  print "setting attributes for mbean type SecurityParams"
  set("AttachJMSXUserId", "false")

def setAttributesFor_XAQueueConnectionFactory(module,jndiname):
  cd("/JMSSystemResources/"+ module + "/JMSResource/"+ module + "/ConnectionFactories/XAConnectionFactory")
  print "setting attributes for mbean type JMSConnectionFactory"
  set("DefaultTargetingEnabled", "true")
  set("Name", jndiname)
  set("JNDIName", jndiname)
  cd("/JMSSystemResources/"+ module + "/JMSResource/"+ module + "/ConnectionFactories/XAConnectionFactory/LoadBalancingParams/XAConnectionFactory")
  set("LoadBalancingEnabled", "true")
  set("ServerAffinityEnabled", "false")
  #cd("/JMSSystemResources/" + module + "/JMSResource/" + module + "/ConnectionFactories/" + jndiname + "/TransactionParams/" + jndiname )
  #set("XAConnectionFactoryEnabled", "true")
  

def setAttributesFor_Queue(module,resourcename,jndiname):
  cd("/JMSSystemResources/"+ module + "/JMSResource/"+ module + "/UniformDistributedQueues/" + resourcename)
  print "setting attributes for mbean type UniformDistributedQueue"
  set("LoadBalancingPolicy", "Round-Robin")
  set("Name", resourcename)
  set("SubDeploymentName", "servergroup")
  set("JNDIName", jndiname)
  
def create_UniformDistributedTopic(path, beanName):
  cd(path)
  try:
    print "creating mbean of type UniformDistributedTopic ... "
    theBean = cmo.lookupUniformDistributedTopic(beanName)
    if theBean == None:
      cmo.createUniformDistributedTopic(beanName)
  except java.lang.UnsupportedOperationException, usoe:
    pass
  except weblogic.descriptor.BeanAlreadyExistsException,bae:
    pass
  except java.lang.reflect.UndeclaredThrowableException,udt:
    pass

	
def setAttributesFor_XATopicConnectionFactory(module,jndiname):
  cd("/JMSSystemResources/" + module + "/JMSResource/" + module + "/ConnectionFactories/XATopicConnectionFactory")
  print "setting attributes for mbean type JMSConnectionFactory"
  set("DefaultTargetingEnabled", "true")
  set("Name", jndiname)
  set("JNDIName", jndiname)
  cd("/JMSSystemResources/" + module + "/JMSResource/" + module + "/ConnectionFactories/XATopicConnectionFactory/LoadBalancingParams/XATopicConnectionFactory")
  set("LoadBalancingEnabled", "true")
  set("ServerAffinityEnabled", "false")
  
def setAttributesFor_XATransactionParams(module,jndiname):
  print "setting attributes for mbean type TransactionParams"
  print "/JMSSystemResources/" + module + "/JMSResource/" + module + "/ConnectionFactories/NO_NAME_0 /TransactionParams/" + jndiname
  cd("/JMSSystemResources/" + module + "/JMSResource/" + module + "/ConnectionFactories/" + jndiname )
  create("DUMMY","TransactionParams")
  cd("TransactionParams/NO_NAME_0")
  set("XAConnectionFactoryEnabled", "true")

def setAttributesFor_Topic(module,resourcename,jndiname):
  cd("/JMSSystemResources/" + module + "/JMSResource/" + module + "/UniformDistributedTopics/"+ resourcename)
  print "setting attributes for mbean type UniformDistributedTopic"
  set("LoadBalancingPolicy", "Round-Robin")
  set("Name", resourcename)
  set("SubDeploymentName", "servergroup")
  set("JNDIName", jndiname)

def create_JDBCStore(path, beanName):
  cd(path)
  try:
    print "creating mbean of type JDBCStore ... "
    theBean = cmo.lookupJDBCStore(beanName)
    if theBean == None:
      cmo.createJDBCStore(beanName)
  except java.lang.UnsupportedOperationException, usoe:
    pass
  except weblogic.descriptor.BeanAlreadyExistsException,bae:
    pass
  except java.lang.reflect.UndeclaredThrowableException,udt:
    pass

def create_JMSServer(path, beanName):
  cd(path)
  try:
    print "creating mbean of type JMSServer ... "
    theBean = cmo.lookupJMSServer(beanName)
    if theBean == None:
      cmo.createJMSServer(beanName)
  except java.lang.UnsupportedOperationException, usoe:
    pass
  except weblogic.descriptor.BeanAlreadyExistsException,bae:
    pass
  except java.lang.reflect.UndeclaredThrowableException,udt:
    pass


def setAttributesForJMSServer(jms_server,server,jdbcstore):
  cd("/JMSServers/" + jms_server)
  print "setting attributes for mbean type JMSServer"
  refBean0 = getMBean("/Servers/" + server )
  theValue = jarray.array([refBean0], Class.forName("weblogic.management.configuration.TargetMBean"))
  cmo.setTargets(theValue)

  bean = getMBean("/JDBCStores/" + jdbcstore )
  cmo.setPersistentStore(bean)

ls()
def setAttributesFor_JDBCStore(store,servername,prefix,datastore):
  cd("/JDBCStores/" + store )
  print "setting attributes for mbean type JDBCStore"
  set("PrefixName", prefix)
  refBean0 = getMBean("/Servers/" + servername )
  theValue = jarray.array([refBean0], Class.forName("weblogic.management.configuration.TargetMBean"))
  cmo.setTargets(theValue)
  bean = getMBean("/JDBCSystemResources/" + datastore)
  cmo.setDataSource(bean)

def setAttributesFor_JMSModule(jmsModule,clustername):
  cd("/JMSSystemResources/" + jmsModule)
  print "setting attributes for mbean type JMSSystemResource"
  refBean0 = getMBean("/Clusters/" + clustername)
  theValue = jarray.array([refBean0], Class.forName("weblogic.management.configuration.TargetMBean"))
  cmo.setTargets(theValue)

def setAttributesFor_SubDeployment(module,submodule,servernames):
  cd("/JMSSystemResources/"+ module + "/SubDeployments/" + submodule)
  print "setting attributes for mbean type SubDeployment"
  theValue=[]
  for i in servernames:
	refBean0 = getMBean("/JMSServers/" + i )
	theValue.append(refBean0)
  cmo.setTargets(theValue)


#=======================================================================================
# Utility function to load a property file
#=======================================================================================
def loadPropertiesFromFile(filename):
	properties = Properties()
	input = FileInputStream(filename)
	properties.load(input)
	input.close()
	return properties
	

# Create the JDBC resources 
def create_jmsresource(modulename, pscProps):
	try:
		#propInputStream = FileInputStream("jmsdetails.properties")
		#pscProps = Properties()
		#pscProps.load(propInputStream)
		resource_name=pscProps["resource.name"]
		q_type=pscProps["resource.type"] 
		q_jndi_name=pscProps["resource.jndi.name"]
		q_target=pscProps["target"]
		q_datasource=pscProps["persistence.datastore"]
		f_modulename=modulename + "Module"
		
		print "[INFO] Shutting cluster " + q_target
		shutdown(q_target,'Cluster','block=true')
		print "[INFO] configuring resource " + resource_name

		create_JMSSystemResource("/",f_modulename)
		create_SubDeployment("/JMSSystemResources/" + f_modulename , "servergroup")
		if(q_type.upper()=="QUEUE"):
			create_ConnectionFactory("/JMSSystemResources/" + f_modulename + "/JMSResource/" + f_modulename , "XAConnectionFactory")
			create_UniformDistributedQueue("/JMSSystemResources/" + f_modulename + "/JMSResource/" + f_modulename, resource_name)
			setAttributes_SecurityParams("XAConnectionFactory", f_modulename)
			setAttributesFor_XAQueueConnectionFactory(f_modulename, modulename + "XAConnectionFactory")
			setAttributesFor_Queue(f_modulename,resource_name,q_jndi_name)
			#setAttributesFor_XATransactionParams(f_modulename, modulename + "XAConnectionFactory")
			
		else:
			create_UniformDistributedTopic("/JMSSystemResources/"+ f_modulename +"/JMSResource/" + f_modulename, "resource_name")
			create_ConnectionFactory("/JMSSystemResources/"+ f_modulename +"/JMSResource/" + f_modulename, "XATopicConnectionFactory")
			setAttributes_SecurityParams("XATopicConnectionFactory", f_modulename)
			setAttributesFor_XATopicConnectionFactory(f_modulename, modulename + "XATopicConnectionFactory" )
			setAttributesFor_XATransactionParams(f_modulename, modulename + "XATopicConnectionFactory" )
			#setAttributesFor_Topic(f_modulename,resource_name,q_jndi_name)
		
		cd('/')
		servers = cmo.getServers()
		print 'Servers in the domain are'
		count=1
		for x in servers:
			srv_name=x.getName()
			if(not srv_name.endswith("ADM")):
				create_JMSServer("/", modulename + 'JMSServer' + str(count))
				create_JDBCStore("/", modulename + 'jdbcStore'  + str(count))
				setAttributesFor_JDBCStore(modulename +"jdbcStore"  + str(count) , srv_name,modulename + str(count),q_datasource)
				setAttributesForJMSServer(modulename + 'JMSServer' + str(count),srv_name,modulename +"jdbcStore" +  str(count))
				_serverNames.append(modulename + 'JMSServer' + str(count))
				count=count+1
				
		
		setAttributesFor_SubDeployment(f_modulename,"servergroup", _serverNames)
		setAttributesFor_JMSModule(f_modulename,q_target)
		
		print "[INFO] Starting cluster " + q_target
		start(q_target,'Cluster','block=true')
		
		
  	except java.lang.UnsupportedOperationException, usoe:
    		print "Could not create  resource "
    		pass
  	except weblogic.descriptor.BeanAlreadyExistsException,bae:
    		print "Could not create  resource"
    		pass
  	except java.lang.reflect.UndeclaredThrowableException,udt:
    		print "Could not create  resource"
    		pass
			
# IMPORT script init
try:

	xmlp = XmlProperties("tmp/ant-properties.xml")
	pf = xmlp.getAntProperties()

	# get a list of datasource unique ids
	jmsNameProps = pf.getPartialKey("*.module.name")
	jmsIds = []
	for key, value in jmsNameProps:
		jmsIds.append(key.split(".")[0])

	for jmsId in jmsIds:
		jmsConfig = JMSResourceConfig(jmsId, pf).getConfig()
		target = jmsConfig["target"]

		print "[INFO} resolving admin server for " + target		connected = false
		print "[INFO] resolving admin server for target " + target
		connected = false
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
			create_jmsresource(jmsId, jmsConfig)
			endTransaction()
  

except:
    print "Unexpected error: ", sys.exc_info()[0]
    dumpStack()
    raise
	