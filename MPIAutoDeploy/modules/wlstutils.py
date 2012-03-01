import os, sys
import commands
import wl
import wlstModule
from propertiesutils import PropertiesFile
from weblogic.management.scripting.utils import WLSTInterpreter
from java.util import HashMap
from java.io import FileInputStream 
from com.bea.wli.sb.management.configuration import SessionManagementMBean
from com.bea.wli.sb.management.configuration import ALSBConfigurationMBean
from com.bea.wli.config import Ref
from com.bea.wli.config.customization import Customization
from java.io import FileInputStream 

class ServerConnection:
	def __init__(self, url, username, password, passphrase=None):
		self.url = url
		self.username = username
		self.password = password
		self.passphrase = passphrase
		self.interpreter = WLSTInterpreter()

	def logOn(self):
		try:
			connectString = "connect('" + self.username + "', '" + self.password + "', '" + self.url + "')"
			self.execute(connectString)
		except Exception, e:
			print "[ERROR] error connecting to server"
			print e
			raise
	def listClusters(self):
		clusters =[]
		redirectf = "tmp/_listClusters.txt"
		self.execute("ls()", "cd('/Clusters')", redirectf)
		ofile = open(redirectf, "r")
		for line in ofile.readlines():
			lineBits = line.split("--")
			if len(lineBits) > 1:
				clusters.append(lineBits[1].strip())
		self.execute("cd('/')")
		ofile.close()
		self.removeRedirectFile(redirectf)
		return clusters

	def clusterIsUp(self, cluster):
		""" return true if all managed servers are up. otherwise, false
		"""
		redirectf = "tmp/_clusterStatus.txt"
		self.execute("state('" + cluster + "','Cluster')", redirFile=redirectf)
		ofile = open(redirectf, "r")
		running = 1
		for line in ofile.readlines():
			lineBits = line.split("---")
			if len(lineBits) > 1:
				if lineBits[1].strip() != "RUNNING":
					running = 0
		ofile.close()
		self.removeRedirectFile(redirectf)
		return running
		
	def removeRedirectFile(self, redirectFile):
		if os.stat(redirectFile):
			os.remove(redirectFile)

	def execute(self, command, navigate=None, redirFile=None):
		print "[DEBUG] comand = " + command
		try:
			if navigate:
				self.interpreter.exec(navigate)
			if redirFile:
				self.interpreter.exec("redirect('" + redirFile + "', 'false')")
			self.interpreter.exec(command)
			if redirFile:
				self.interpreter.exec("stopRedirect()")
			return 1
		except Exception, e:
			self.interpreter.exec("stopRedirect()")
			print e
			raise

	def returnValue(self, command):
		print "[DEBUG] command = " + command
		wlstThing = self.interpreter.exec(command)
		return wlstThing
		
class WlstFragments:
	def __init__(self, username, password, url):
		connect(username, password, url)

class DatasourceConfig:
	""" get a version-agnostic set of properties for a datasource. deal with changes to input property structure
	"""
	def __init__(self, dsTag, props):
		self.config = {}
		name = props.get(dsTag + ".datasource.name")
		self.config["jndi"]=[]
		if not name:
			self.config["name"] = dsTag
			self.config["jndi"].append(dsTag)
		else:
			self.config["name"] = name
			jndiList = props.get(dsTag + ".jndi.name")
			jndiBits = jndiList.split(",")
			for jndiBit in jndiBits:
				self.config["jndi"].append(jndiBit.strip())
		self.config["host"] = props.get(dsTag + ".db.host")
		self.config["port"] = props.get(dsTag + ".db.port")
		self.config["user"] = props.get(dsTag + ".db.user")
		self.config["password"] = props.get(dsTag + ".db.password")
		self.config["dbName"] = props.get(dsTag + ".db.name")
		self.config["url"] = props.get(dsTag + ".db.url")
		self.config["driver"] = props.get(dsTag + ".db.driver")
		self.config["target"] = []
		targetList = props.get(dsTag + ".target")
		targetBits = targetList.split(",")
		for targetBit in targetBits:
			self.config["target"].append(targetBit.strip())
	def getConfig(self):
		return self.config
		
class JMSResourceConfig:
	""" get a version-agnostic set of properties for jms resource in anticipation of refactoring properties
		takes a property tag and the ant environment properties  -  returns a dict of properties
	"""
	def __init__(self, jmsTag, props):
		self.config = {}
		suffix = props.get(jmsTag + ".jms.system.module.suffix")
		if suffix:
			moduleName = jmsTag + "_" + suffix
		else:
			moduleName = jmsTag
		numSuffix = props.get(jmsTag + ".jms.module.numeric.suffix")
		if not numSuffix:
			self.config["jms.module.numeric.suffix"] = "01"
		else:
			self.config["jms.module.numeric.suffix"] = numSuffix
		self.config["module.name"] = moduleName
		self.config["base.name"] = jmsTag
		if props.get(jmsTag + ".target.suffix"):
			self.config["target.domain"] = props.get(jmsTag + ".target.domain") + "_" + props.get(jmsTag + ".target.suffix")
		else:
			self.config["target.domain"] = props.get(jmsTag + ".target.domain")
		self.config["datasource"] = props.get(jmsTag + ".datasource")
		if props.get(jmsTag + ".jndi.names.prefix"):
			self.config["jndi.names.prefix"] = props.get(jmsTag + ".jndi.names.prefix")
			jndiNamesPrefix = props.get(jmsTag + ".jndi.names.prefix") + "."
		else:
			self.config["jndi.names.prefix"] = "none"
			jndiNamesPrefix = ""
		queues = []
		queueProps = props.getPartialKey(jmsTag + ".queue.*.name")
		for k, v in queueProps:
			# create a dict of overrides for each queue
			overrides = {}
			# queue jndi name - defaults to "jms.queuename"
			# jndi name is not used as at 2.4.2
			# enforced default is ${jndi.names.prefix}[.]queuename_connection factory name
			jndiName = props.get(jmsTag + ".queue." + v + ".jndi.name")
			if jndiName:
				overrides["jndi.name"] = jndiName
			else:
				overrides["jndi.name"] = jndiNamesPrefix + v
			#xa connection factory suffix - used to create xa connection factory - if not present, no cf
			xacfSuffix = props.get(jmsTag + ".queue." + v + ".xa.cf.suffix")
			if xacfSuffix:
				overrides["create.xa.cf"] = 1
				overrides["xa.cf.suffix"] = xacfSuffix
			else:
				overrides["create.xa.cf"] = 0
			#nonxa connection factory suffix - used to create nonxa connection factory - if not present, no cf
			nonxacfSuffix = props.get(jmsTag + ".queue." + v + ".nonxa.cf.suffix")
			if nonxacfSuffix:
				overrides["create.nonxa.cf"] = 1
				overrides["nonxa.cf.suffix"] = nonxacfSuffix
			else:
				overrides["create.nonxa.cf"] = 0
			# default targeting (default true)
			defaultTargeting = props.get(jmsTag + ".queue." + v + ".default.targeting")
			if defaultTargeting:
				if defaultTargeting.upper() != "ENABLED":
					overrides["default.targeting"] = 0
				else:
					overrides["default.targeting"] = 1
					
			else:
				overrides["default.targeting"] = 1
			# server affinity (default disabled)
			serverAffinity = props.get(jmsTag + ".queue." + v + ".server.affinity")
			if serverAffinity:
				if serverAffinity.upper() != "DISABLED":
					overrides["server.affinity"] = 1
				else:
					overrides["server.affinity"] = 0
			else:
				overrides["server.affinity"] = 0
			# xa connection factory (default enabled)
			xaConnectionFactory = props.get(jmsTag + ".queue." + v + ".xa.connection.factory")
			if xaConnectionFactory:
				if xaConnectionFactory.upper() != "ENABLED":
					overrides["xa.connection.factory"] = 0
				else:
					overrides["xa.connection.factory"] = 1
			else:
				overrides["xa.connection.factory"] = 1
			# forward delay (default 1)
			forwardDelay = props.get(jmsTag + ".queue." + v + ".forward.delay")
			if forwardDelay:
				overrides["forward.delay"] = int(forwardDelay)
			else:
				overrides["forward.delay"] = 1
			# delivery mode (default Persistent)
			deliveryMode = props.get(jmsTag + ".queue." + v + ".delivery.mode")
			if deliveryMode:
				overrides["delivery.mode"] = deliveryMode
			else:
				overrides["delivery.mode"] = "Persistent"
			# time to live  (default 3600000) - might be an extra zero here
			timeToLive = props.get(jmsTag + ".queue." + v + ".time.to.live")
			if timeToLive:
				overrides["time.to.live"] = int(timeToLive)
			else:
				overrides["time.to.live"] = 3600000
			# redelivery delay (default 30000)
			redeliveryDelay = props.get(jmsTag + ".queue." + v + ".redelivery.delay")
			if redeliveryDelay:
				overrides["redelivery.delay"] = int(redeliveryDelay)
			else:
				overrides["redelivery.delay"] = 30000
			# redelivery limit (default 5)
			redeliveryLimit = props.get(jmsTag + ".queue." + v + ".redelivery.limit")
			if redeliveryLimit:
				overrides["redelivery.limit"] = int(redeliveryLimit)
			else:
				overrides["redelivery.limit"] = 5
			# expiration.policy (default Redirect)
			expirationPolicy = props.get(jmsTag + ".queue." + v + ".expiration.policy")
			if expirationPolicy:
				overrides["expiration.policy"] = expirationPolicy
			else:
				overrides["expiration.policy"] = "Redirect"
			queueConfig = (v, overrides)
			queues.append(queueConfig)
		self.config["queues"] = queues
		topics = []
		topicProps = props.getPartialKey(jmsTag + ".topic.*.name")
		for k, v in topicProps:
			overrides = {}
			jndiName = props.get(jmsTag + ".topic." + v + ".jndi.name")
			if jndiName:
				overrides["jndi.name"] = jndiName
			else:
				overrides["jndi.name"] = "jms." + v
			deliveryMode = props.get(jmsTag + ".topic." + v + ".delivery.mode")
			if deliveryModel:
				overrides["delivery.mode"] = deliveryMode
			else:
				overrides["delivery.mode"] = "Persistent"
			# time to live  (default 3600000) - might be an extra zero here
			timeToLive = props.get(jmsTag + ".topic." + v + ".time.to.live")
			if timeToLive:
				overrides["time.to.live"] = int(timeToLive)
			else:
				overrides["time.to.live"] = 3600000
			# redelivery delay (default 30000)
			redeliveryDelay = props.get(jmsTag + ".topic." + v + ".redelivery.delay")
			if redeliveryDelay:
				overrides["redelivery.delay"] = int(redeliveryDelay)
			else:
				overrides["redelivery.delay"] = 30000
			# redelivery limit (default 5)
			redeliveryLimit = props.get(jmsTag + ".topic." + v + ".redelivery.limit")
			if redeliveryLimit:
				overrides["redelivery.limit"] = int(redeliveryLimit)
			else:
				overrides["redelivery.limit"] = 5
			# expiration.policy (default Redirect)
			expirationPolicy = props.get(jmsTag + ".topic." + v + ".expiration.policy")
			if expirationPolicy:
				overrides["expiration.policy"] = expirationPolicy
			else:
				overrides["expiration.policy"] = "Redirect"
			topicConfig = (v, overrides)
			topics.append(topicConfig)
		self.config["topics"] = topics
	def getConfig(self):
		return self.config

class DeploymentConfig:
	def __init__(self, app, pf):
		self.config = {}
		self.config["target"] = pf.get(pf.get(app + ".target") + ".target.name")
		adminServer = pf.get(pf.get(app + ".target") + ".admin.server")
		self.config["domain"] = pf.get(adminServer + ".domain_name")
		self.config["admin.user"] = pf.get(adminServer + ".admin_user")
		self.config["admin.password"] = pf.get(adminServer + ".admin_password")
		self.config["admin.url"] = pf.get(adminServer + ".admin_url")
		self.config["name"] = app
		packageHome = os.path.normpath(pf.get("package.home"))
		self.config["deployable"] = os.path.join(packageHome, pf.get(app + ".deployable"))
		self.config["version"] = pf.get(app + ".version.label")
	def getConfig(self):
		return self.config

class ApplicationDeploymentConfig(DeploymentConfig):
	""" return a dict of attributes for the deployment of a web app
	"""
	def __init__(self, app, pf):
		DeploymentConfig.__init__(self, app, pf)
		retries = pf.get("weblogic.script.deploy.distribute.count")
		if not retries:
			retries = "1"
		self.config["distribute.retry.count"] = int(retries)
		sm = pf.get(app + ".securitymodel")
		if sm:
			self.config["security.model"] = sm
		else:
			self.config["security.model"] = "CustomRoles"
		if pf.get("weblogic.application.deploy.without.version.identifier") == "true":
			self.config["deploy.with.version.identifier"] = 0
		else:
			self.config["deploy.with.version.identifier"] = 1
			
	def getConfig(self):
		return self.config
	

class OSBDeploymentConfig(DeploymentConfig):
	""" return a dict of attributes for the deployment of a osb jar
	"""
	def __init__(self, osb, pf):
		DeploymentConfig.__init__(self, osb, pf)
	def getConfig(self):
		return self.config
		
		
class CommandOutputParser:
	""" simple stuff around parsing the result of a redirect()
	"""
	def __init__(self, outFile):
		of = open(outFile, "r")
		self.outlines = of.readlines()
		of.close()
	def contains(self, content):
		hasContent = 0
		for line in self.outlines:
			if line.find(content) > 0:
				hasContent = 1
				break
		return hasContent