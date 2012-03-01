## This script creates JMS resources required for PSC deployment
## this is the Estafet script as created by Paul Nixon hacked about to work with autodeploy 2.4.x
import os
from propertiesutils import XmlProperties
from wlstutils import JMSResourceConfig
from wlstutils import CommandOutputParser

# I don't like globals but I can't think of a better way to implement this without a lot of work
global debugging


def connectToAdminServer(username, password, url):
	try:
		connect(username,password,url)
		return true
	except WLSTException:
		print 'Unable to connect to admin server at ' + url 
		return false


def startTransaction():
	edit()
	startEdit()

def endTransaction(pf):
#	if debugging:
#		print "Debug mode enabled: cancelling changes"
#		cancelEdit('y')
#	else:
	save()
	if debugging:
		stdout = "true"
	else:
		stdout = "false"
#	redirect("tmp/wlst-managejmsresources.out", "false")
	try:
		activate(block="true")
	except:
#		dumpStack()
#		stopRedirect()
		antLog = os.path.join(pf.get("deploy.log.dir"), pf.get("deploy.log.filename"))
		if CommandOutputParser(antLog).contains("Same server added twice?"):
			print "[WARN] known weblogic error occurred during commit - check jms has been set up correctly"
		else:
			print "[ERROR] error occured during activation"
#			dumpStack()
			raise
#	stopRedirect()


	# Verify that a cluster and datasource exist in the domain and that:
	# no JMS module with name 'modulename' already exists;
	# no JMS Servers and JDBC Stores with names derived from 'modulename' exist;
	# Returns false if any conditions are not met; else returns true
def checkJMSConfig(modulename, cluster, datasourcename, strNumSuffix) :
	if debugging:
		print "Checking cluster exists"
	clusterBean = getMBean("/Clusters/" + cluster)
	if clusterBean == None :
		print 'Cluster ' + cluster + ' not found in domain'
		return false
	if debugging:
		print "Checking datasource exists"
	dataSource = getMBean("/JDBCSystemResources/" + datasourcename)
	if dataSource == None:
		print 'DataSource with name ' + datasourcename + ' not found in domain'
		return false
	result = true
	# Check that a JMS system module of same name does not already exist
	cd('/')
	mod = cmo.lookupJMSSystemResource(modulename)
	if mod == None:
		# Look for JMSStores and JMSServers
		servers = clusterBean.getServers()
		numSuffix = int(strNumSuffix)
		fillLen = len(strNumSuffix)
		for s in range(len(servers)):
			# Generate name suffix in series 01 02 03....
			suffix = str(numSuffix).zfill(fillLen)
			numSuffix += 1
			cd('/')
			serverName = modulename + '_JMSServer_' + suffix
			if debugging:
				print "Looking for JMSServer " + serverName
			jmsServer = cmo.lookupJMSServer(serverName)
			if jmsServer != None:
				jdbcStore = jmsServer.getPersistentStore()
				if jdbcStore == None:
					print 'A JMSServer with name ' + serverName + ' already exists in the domain'
				else :
					print 'A JMSServer with name ' + serverName + ' using JDBCStore ' + jdbcStore.getName() + ' already exists in the domain'
				result = false
				break
			storeName = modulename + '_JDBCStore_'  + suffix
			jdbcStore = cmo.lookupJDBCStore(storeName)
			if debugging:
				print "Looking for JDBCStore " + storeName
			if jdbcStore != None:
				print 'A JDBCStore with name ' + storeName + ' already exists in the domain'
				result = false
				break
	else:
		# Module already exists
		print 'A JMSSystemModule with name ' + modulename + ' already exists in the domain'
		result = false
	return result


	# Clean up in the event of a failure on resource creation
def cleanup(modulename, cluster, datasourcename, strNumSuffix) :
	if debugging:
		print "Cleaning up"
	clusterBean = getMBean("/Clusters/" + cluster)
	# Check for the JMS system module and destroy if it exists
	cd('/')
	mod = cmo.lookupJMSSystemResource(modulename)
	if mod != None:
		if debugging:
			print 'Destroying JMSSystemResource ' + modulename
		cmo.destroyJMSSystemResource(mod)
	# Look for and destroy JMSStores and JMSServers
	servers = clusterBean.getServers()
	numSuffix = int(strNumSuffix)
	fillLen = len(strNumSuffix)
	for s in range(len(servers)):
		# Generate name suffix in series 01 02 03....
		suffix = str(numSuffix).zfill(fillLen)
		numSuffix += 1
		cd('/')
		serverName = modulename + '_JMSServer_' + suffix
		if debugging:
			print "Looking for JMSServer " + serverName
		jmsServer = cmo.lookupJMSServer(serverName)
		if jmsServer != None:
			if debugging:
				print 'Destroying JMSServer ' + serverName
			cmo.destroyJMSServer(jmsServer)
		storeName = modulename + '_JDBCStore_'  + suffix
		jdbcStore = cmo.lookupJDBCStore(storeName)
		if debugging:
			print "Looking for JDBCStore " + storeName
		if jdbcStore != None:
			if debugging:
				print 'Destroying JDBCStore ' + storeName
			cmo.destroyJDBCStore (jdbcStore)


	# Create JMS Servers and JDBC Stores with names derived from 'modulename'
	# targetted at the migratable targets for the servers in 'cluster'. JDBCStores
	# will use 'datasource' for persistence
	# Returns an array containing the MBeans of the JMS servers created
def createJMSServers(modulename, cluster, datasourcename, strNumSuffix) :
	jmsServers = []
	clusterBean = getMBean("/Clusters/" + cluster)
	servers = clusterBean.getServers()
	numSuffix = int(strNumSuffix)
	fillLen = len(strNumSuffix)
	for s in range(len(servers)):
		serverName = servers[s].getName()
		# Set migratable target
		target = getMBean("/MigratableTargets/" + serverName + " (migratable)")
		targets = jarray.array([target], Class.forName("weblogic.management.configuration.TargetMBean"))
		# Create name suffix in series 01 02 03....
		suffix = str(numSuffix).zfill(fillLen)
		numSuffix += 1
		cd('/')
		storeName = modulename + '_JDBCStore_'  + suffix
		print "Creating JDBCStore with name " + storeName
		jdbcStore = cmo.createJDBCStore(storeName)
		jdbcStore.setPrefixName( modulename + suffix )
		jdbcStore.setTargets(targets)
		dataSource = getMBean("/JDBCSystemResources/" + datasourcename)
		jdbcStore.setDataSource(dataSource)
		jmsName = modulename + '_JMSServer_' + suffix
		cd('/')
		print "Creating JMSServer with name " + jmsName
		jmsServer = cmo.createJMSServer(jmsName)
		jmsServer.setPersistentStore(jdbcStore)
		jmsServer.setTargets(targets)
		jmsServers.append(jmsServer)
	if debugging:
		for i in range(len(jmsServers)):
			print "[DEBUG] jmsServer %i : %s" % (i, jmsServers[i].getName())
	return jmsServers


# Set special attributes of an error destination (queue or topic)
def configureErrorDestination (destination) :
	if (debugging):
		print "Configuring error destination " + destination.getName()
	ov = destination.getDeliveryParamsOverrides()
	if (debugging):
		print "Setting delivery overrides"
	ov.setDeliveryMode("Persistent")
	ov.setRedeliveryDelay(60000)
	# ov.setTimeToDeliver("-1")
	# ov.setTimeToLive(-1)
	logging = destination.getMessageLoggingParams()
	if (debugging):
		print "Setting logging params"
	logging.setMessageLoggingEnabled(true)
	# Log all message headers and properties
	logging.setMessageLoggingFormat("%header%,%properties%")
	df = destination.getDeliveryFailureParams()
	if (debugging):
		print "Setting delivery failure params"
	df.setRedeliveryLimit(5)
	df.setExpirationPolicy("Log")
	# Log all expired message headers and properties plus delivery time and redelivery limit
	df.setExpirationLoggingPolicy("%header%,%properties%,JMSDeliveryTime,JMSRedeliveryLimit") 


# Create and retutn Error Queue for queue named 'qName' in 'module' targetted at 'subdeployment'
def createErrorQueue (qName, module, subdeployment, jndiPrefix) :
	if (debugging):
		print "Creating error distributed queue name " + qName + "_Error_UDQ"
	errorQ = module.getJMSResource().createUniformDistributedQueue(qName + "_Error_UDQ")
	errorQ.setSubDeploymentName(subdeployment.getName())
	if jndiPrefix != "none":
		errorQ.setJNDIName(jndiPrefix + "." + errorQ.getName())
	else:
		errorQ.setJNDIName(errorQ.getName())
	errorQ.setForwardDelay(1)
	configureErrorDestination(errorQ)
	return errorQ


# Create and return Error Topic for topic named 'tName' in 'module' targetted at 'subdeployment'
def createErrorTopic (tName, module, subdeployment, jndiPrefix) :
	if (debugging):
		print "Creating error distributed topic name " + tName + "_Error_UDT"
	errorT = module.getJMSResource().createUniformDistributedTopic(tName + "_Error_UDT")
	errorT.setSubDeploymentName(subdeployment.getName())
	if jndiPrefix != "none":
		errorT.setJNDIName(jndiPrefix + "." + errorT.getName())
	else:
		errorT.setJNDIName(errorT.getName())
	
	configureErrorDestination(errorT)
	return errorT


# Create SystemModule 'modulename' containing JMS Servers, Destinations and related JMS resources. 
# Target destinations at a SubDeployment referring JMS Servers created on all servers in cluster.
# JMS Stores will use 'datasource' for persistence
def createJmsResources(jmsConfig):
	modulename = jmsConfig["base.name"]
	cluster = jmsConfig["target.domain"]
	if not jmsConfig["jndi.names.prefix"] == "none":
		jndiNamesPrefix = jmsConfig["jndi.names.prefix"] + "."
	else:
		jndiNamesPrefix = ""
	print "Configuring JMS resource " + modulename + " targetted at " + cluster
	if (not checkJMSConfig(modulename, cluster, jmsConfig["datasource"], jmsConfig["jms.module.numeric.suffix"])) :
		# Already exists, or cluster not found: can't proceed
		return false
	clusterBean = getMBean("/Clusters/" + cluster)
	# Create JMS servers on each managed server in cluster and target at corresponding migratable targets
	theJMSServers = createJMSServers(modulename, cluster, jmsConfig["datasource"], jmsConfig["jms.module.numeric.suffix"])
	# Create JMS System Module and target at cluster
	print "Creating JMSSystemModule"
	cd('/')
	module = cmo.createJMSSystemResource(jmsConfig["module.name"])
	clusterTarget = jarray.array([clusterBean], Class.forName("weblogic.management.configuration.TargetMBean"))
	module.setTargets(clusterTarget)
	# Create SubDeployment for destinations and target at the JMS Servers created above
	if (debugging) :
		print "Creating SubDeployment"
	subDeploy = module.createSubDeployment(modulename + "_SubDeployment")
	subDeploy.setTargets(theJMSServers)
	
	topics = pf.getPartialKey(modulename + ".jms.topic.*.name")
	if len(jmsConfig["queues"]) == 0 and len(jmsConfig["topics"]) == 0:
		print "No destinations defined for module ", modulename
		print "Module has been created without destinations"
		return true
	if (debugging) :
		print "Creating destinations and related resources"
	# Create (uniform distributed) queues and target at the subdeployment
	for qName, overrides in jmsConfig["queues"]:
		if (debugging):
			print "Creating resources for queue " + qName
		# Create XA connection factory for queue
		if overrides["create.xa.cf"]:
			xacfQueueName = qName + "_" + overrides["xa.cf.suffix"]
			if (debugging):
				print "Creating connection factory with name " + xacfQueueName
			cf = module.getJMSResource().createConnectionFactory(xacfQueueName);
			cf.setJNDIName(jndiNamesPrefix + cf.getName())
			# Default targetting targets conn factory at cluster target of parent module
			cf.setDefaultTargetingEnabled(overrides["default.targeting"])
			if (debugging):
				print "Setting load balancing params"
			cf.getLoadBalancingParams().setServerAffinityEnabled(overrides["server.affinity"])
			if (debugging):
				print "Setting transaction params"
			cf.getTransactionParams().setXAConnectionFactoryEnabled(true)
		if overrides["create.nonxa.cf"]:
			nonxacfQueueName = qName + "_" + overrides["nonxa.cf.suffix"]
			# Create non-XA connection factory for queue
			if (debugging):
				print "Creating connection factory with name " + nonxacfQueueName
			cf = module.getJMSResource().createConnectionFactory(nonxacfQueueName);
			cf.setJNDIName(jndiNamesPrefix + cf.getName())
			# Default targetting targets conn factory at cluster target of parent module
			cf.setDefaultTargetingEnabled(overrides["default.targeting"])
			if (debugging):
				print "Setting load balancing params"
			cf.getLoadBalancingParams().setServerAffinityEnabled(overrides["server.affinity"])
			# Create error queue for the distributed queue
		errorQ = createErrorQueue(qName, module, subDeploy, jmsConfig["jndi.names.prefix"])
		# Create the distributed queue
		if (debugging):
			print "Creating distributed queue with name " + qName + "_UDQ"
		queue = module.getJMSResource().createUniformDistributedQueue(qName + "_UDQ")
		queue.setSubDeploymentName(subDeploy.getName())
		queue.setJNDIName(overrides["jndi.name"])
		# Forward delay: check for user provided value; else set default
		queue.setForwardDelay(overrides["forward.delay"])
		ov = queue.getDeliveryParamsOverrides()
		if (debugging):
			print "Setting delivery overrides"
		if not overrides["delivery.mode"] == "No-Delivery":
			ov.setDeliveryMode(overrides["delivery.mode"])
		ov.setTimeToLive(overrides["time.to.live"])
		ov.setRedeliveryDelay(overrides["redelivery.delay"])
		df = queue.getDeliveryFailureParams()
		if (debugging):
			print "Setting delivery params"
		if (debugging):
			print "RedeliveryLimit"
		df.setRedeliveryLimit(overrides["redelivery.limit"])
		if (debugging):
			print "ExpirationPolicy"
		df.setExpirationPolicy(overrides["expiration.policy"])
		if (debugging):
			print "ErrorDestination"
		df.setErrorDestination(errorQ)
	for tName, overrides in jmsConfig["topics"]:
		if (debugging):
			print "Creating resources for topic " + tName
		# Create XA connection factory for topic
		if (debugging):
			print "Creating connection factory with name " + tName + "_XA_CF"
		cf = module.getJMSResource().createConnectionFactory(tName + "_XA_CF");
		cf.setJNDIName(jndiNamesPrefix + cf.getName())
		# Default targetting targets conn factory at cluster target of parent module
		cf.setDefaultTargetingEnabled(true)
		if (debugging):
			print "Setting load balancing params"
		cf.getLoadBalancingParams().setServerAffinityEnabled(false)
		if (debugging):
			print "Setting transaction params"
		cf.getTransactionParams().setXAConnectionFactoryEnabled(true)
		# Create non-XA connection factory for topic
		if (debugging):
			print "Creating connection factory with name " + tName + "_NonXA_CF"
		cf = module.getJMSResource().createConnectionFactory(tName + "_NonXA_CF");
		cf.setJNDIName(jndiNamesPrefix + cf.getName())
		# Default targetting targets conn factory at cluster target of parent module
		cf.setDefaultTargetingEnabled(true)
		if (debugging):
			print "Setting load balancing params"
		cf.getLoadBalancingParams().setServerAffinityEnabled(false)
		# Create error topic for the distributed topic
		errorT = createErrorTopic(tName, module, subDeploy, jmsConfig["jndi.names.prefix"])
		# Create the distributed topic
		if (debugging):
			print "Creating distributed topic with name " + tName + "_UDT"
		topic = module.getJMSResource().createUniformDistributedTopic(tName + "_UDT")
		topic.setSubDeploymentName(subDeploy.getName())
		topic.setJNDIName(overrides["jndi.name"])
		ov = topic.getDeliveryParamsOverrides()
		if (debugging):
			print "Setting delivery overrides"
		ov.setDeliveryMode(overrides["delivery.mode"])
		ov.setTimeToLive(overrides["time.to.live"])
		ov.setRedeliveryDelay(overrides["redelivery.delay"])
		df = topic.getDeliveryFailureParams()
		if (debugging):
			print "Setting delivery params"
		if (debugging):
			print "RedeliveryLimit"
		df.setRedeliveryLimit(overrides["redelivery.limit"])
		if (debugging):
			print "ExpirationPolicy"
		df.setExpirationPolicy(overrides["expiration.policy"])
		if (debugging):
			print "ErrorDestination"
		df.setErrorDestination(errorT)
	return true


# Drop JMS module and related JMS Servers and JDBC Stores
def destroyJmsResources(jmsConfig) :
	datasource = jmsConfig["datasource"]
	modulename=jmsConfig["base.name"]
	systemModulename=jmsConfig["module.name"]
	cluster = jmsConfig["target.domain"]
	print "Dropping JMS resource " + modulename + " targetted at " + cluster
	# Check for the JMS system module and destroy if it exists
	cd('/')
	mod = cmo.lookupJMSSystemResource(systemModulename)
	if (mod != None) :
		if (debugging) :
			print 'Destroying JMSSystemResource ' + systemModulename
		cmo.destroyJMSSystemResource(mod)
	if (debugging) :
		print "Checking cluster exists"
	clusterBean = getMBean("/Clusters/" + cluster)
	if (clusterBean == None) :
		print 'Cluster ' + cluster + ' not found in domain: unable to delete JMSServers and JDBCStores'
	else :
		# Look for and destroy JMSStores and JMSServers
		servers = clusterBean.getServers()
		numSuffix = int(jmsConfig["jms.module.numeric.suffix"])
		fillLen = len(jmsConfig["jms.module.numeric.suffix"])
		for s in range(len(servers)):
			# Generate name suffix in series 01 02 03....
			suffix = str(numSuffix).zfill(fillLen)
			numSuffix += 1
			cd('/')
			serverName = modulename + '_JMSServer_' + suffix
			if (debugging) :
				print "Looking for JMSServer " + serverName
			jmsServer = cmo.lookupJMSServer(serverName)
			if (jmsServer != None) :
				if (debugging) :
					print 'Destroying JMSServer ' + serverName
				cmo.destroyJMSServer(jmsServer)
			storeName = modulename + '_JDBCStore_'  + suffix
			jdbcStore = cmo.lookupJDBCStore(storeName)
			if (debugging) :
				print "Looking for JDBCStore " + storeName
			if (jdbcStore != None) :
				if (debugging) :
					print 'Destroying JDBCStore ' + storeName
				cmo.destroyJDBCStore (jdbcStore)



# Create or delete resource depending on the action param on cmd line
# Return true if successful or false if any error
def performTransaction (action, jmsConfig) :
	modname = jmsConfig["base.name"]
	if (action == "create") :
		if (createJmsResources(jmsConfig)) :
			return true
		else :
			print "Unable to create " + modname + "; cancelling configuration of " + modname + " and aborting"
			return false
	elif (action == "drop") :
		destroyJmsResources(jmsConfig)
		return true
	else :
		print "Unrecognised action: '" + action + "'"
		return false


try:
	# return a PropertiesFile object containing the ant namespace properties
	pf = XmlProperties("tmp/ant-properties.xml").getAntProperties()
	debug = pf.get("weblogic.script.debugging")
	if debug == "on":
		debugging = true
	else:
		debugging = false
	action = pf.get("managejmsresources.action")
	modules = pf.getPartialKey("*.jms.system.module.name")
	if debugging:
		print "[DEBUG] len(modules): %i" % len(modules)
		print "[DEBUG] modules[0][1]: " + modules[0][1]
		print "[DEBUG] action: " + action
	for k, modname in modules:
		print "Processing properties for JMS resource ID: %s" % (modname)
		jmsConfig = JMSResourceConfig(modname, pf).getConfig()

		datasourcename = jmsConfig["datasource"]
		target = jmsConfig["target.domain"]
		for k, v in pf.getPartialKey("*.target.name"):
			if v == target:
				admPrefix = pf.get(k.split(".")[0] + ".admin.server")
		domainAdminUserName = pf.get(admPrefix + ".admin_user")
		adminPassword = pf.get(admPrefix + ".admin_password")
		adminAddress = pf.get(admPrefix + ".adminUrl")
		if (debugging) :
			print "Connecting to " + adminAddress + " username: " + domainAdminUserName + "; password: " + adminPassword
		if connectToAdminServer(domainAdminUserName, adminPassword,  adminAddress):
			try:
				startTransaction()
				if (performTransaction(action, jmsConfig)):
					endTransaction(pf)
					disconnect()
				else:
					print "Unable to create " + modname + "; cancelling configuration of " + modname + " and aborting"
					cancelEdit('y')
					disconnect()
					exit(exitcode=1)
			except:
				print "An exception has occurred: ", sys.exc_info()[0], sys.exc_info()[1]
				print "Cancelling configuration of " + modname + " and aborting"
				cleanup(modname, target, datasourcename, jmsConfig["jms.module.numeric.suffix"])
				cancelEdit('y')
				disconnect(force="true")
				exit(exitcode=1)
		else:
			print "Cannot create JMS resource " + modname + "; unable to connect to domain admin server - aborting"
			exit(exitcode=1)
except:
	print "Unexpected error: ", sys.exc_info()[0], sys.exc_info()[1]
	if (debugging) :
		dumpStack()
	exit(exitcode=1)


