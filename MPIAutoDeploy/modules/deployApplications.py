"""
this script was written by Paul Nixon of Estafet
it originated at http://10.240.1.20/svn/gateway/Source/trunk/PSC/TemporaryBooking/TempBookingCommon/TempBookingParentPOM/deployApplications.py
and has been hacked to work with autodeploy 2.4.x (i.e. properties loaded by ant and passed at execution time)

**[1] we have experienced behaviour such that the WLST deploy command fails during its distribution phase
it seems that this happens only from a remote machine - that is a machine that is not in the virtual environment connecting via external ip
we  have seen occasions where a subsequent attempt to distribute sicceeds and sometimes, this has to be retried
this is why we have the rather inelegant code that will retry many times

**[2] we have found that WLST (like weblogic.Deployer) sometimes has trouble with the staged file system
we do not have a satisfactory workaround for this that does not involve manual intervention - so, if we detect this, 
or any other known issue, we bail out
"""
import re
from time import sleep

from propertiesutils import XmlProperties
from wlstutils import ApplicationDeploymentConfig

global debugging


def connectToAdminServer(username, password, url):
	try:
		connect(username,password,url)
		return true
	except WLSTException:
		print 'Unable to connect to admin server at ' + url 
		return false

def deployApplication (appConfig) :
	""" deploys the application described by the appConfig supplied
	if an error occurs in the deploy command, the specific error is not returned. the deploy command simply raises a WLSTException
	we have encountered behaviour where the deploy fails during the distribution to the managed servers and a subsequent distributApplication
	succeeds. Because we have no way of deciding if this is the cause of the failure, in the case of a failure of deploy,
	we try and distribute anyway.
	"""
	# First check if application already deployed - and undeploy it if so
	if isDeployed(appConfig): 
		# Found deployed application - undeploy it
		print "Undeploying application " + appConfig["name"] + " prior to deployment"
		if not undeployApplication(appConfig) :
			return false;
	print "Deploying application ", appConfig["name"], " from file ", appConfig["deployable"]
	options = {}
	options["timeout"] = 0
	if appConfig["deploy.with.version.identifier"]:
		options["versionIdentifier"] = appConfig["version"]
	options["upload"] = "true"
	options["stageMode"] = "stage"
	options["securityModel"] = appConfig["security.model"]
	try:
		redirect("tmp/wlst-command.out", "false")
		status = deploy(appName=appConfig["name"]
				, path=appConfig["deployable"]
				, targets=appConfig["target"]
				, **options
				)
		if status.getState() == "failed":
			return false
	except WLSTException, e:
		# the following works when we encounter the situation where the deploy fails at the distribute stage
		# this is essentially the same as installing the app by navigating to the upload on the admin server
		# the logic is inverted because we cannot get at the error when the deploy fails for this reason
		# so, if it is not one we know about, it is assumed to be the distribution thing
		stopRedirect()
		output = open("tmp/wlst-command.out", "r")
		outlines = output.readlines()
		output.close()
		# known error messages where we should bail out
		# this should add up over time
		knownBadNews = [
			("Check the directory and make sure no other application using this directory", "problem with staged files on managed servers"),
			("failed to preload on startup", "problem loading configuration at startup - maybe required PSCConfig is not on the classpath")
			]
		for line in outlines:
			# **[2]
			if line.startswith("Deployment Message"):
				for news, message in knownBadNews:
					if line.find(news) > 0:
						# detected one of the known error conditions
						print "[ERROR] %s - cannot deploy %s" % (message, appConfig["name"])
						return false
		# **[1]
		# not a known error so assumed to be the distribution thing - this is because we cannot get at the
		# error thrown during the deploy what that happens
		print "[WARN] exception encountered - attempting to distribute the application anyway"
		retry = appConfig["distribute.retry.count"]
		adornments = {
			1 : "st",
			2 : "nd",
			3 : "rd",
			}
		for i in range(retry):
			try:
				adornment = adornments[i + 1]
			except:
				adornment = "th"
			try:
				status = distributeApplication(
					"D:/Domains/" + appConfig["domain"] + "/servers/ORADM20_APP_ADM/upload/" + appConfig["name"] + "/" + appConfig["version"] + "/app/" + appConfig["name"]
					, targets=appConfig["target"]
					, **options)
				if status.getState() == "failed":
					raise
				else:
					break
			except:
				if i < retry - 1:
					print "[DEBUG] retrying for the %i%s time" % (i + 1, adornment)
					print "[DEBUG] waiting 15 seconds..."
					
					sleep(15)
				else:
					return false
	stopRedirect()
	print "Starting application ", appConfig["name"]
	options = {}
	options["timeout"] = 0
	if appConfig["deploy.with.version.identifier"]:
		options["versionIdentifier"] = appConfig["version"]
	
	try:
		status = startApplication(appConfig["name"], **options)
	except:
		return false
	return true

# Stop and undeploy and application with specified name.
# Returns true if application undeployed; else false
def undeployApplication (appConfig) :
	""" undeploy the application described in the supplied appConfig
	"""
	try:
		print "Stopping application ", appConfig["name"]
		status = stopApplication(appConfig["name"], timeout=0)
		if status.getState() == "failed":
			return false
		print "Undeploying application ", appConfig["name"]
		status = undeploy(appConfig["name"], timeout=0)
		if status.getState() == "failed":
			return false
	except:
		return false
	return true

def isDeployed(appConfig):
	""" check if application is deployed
	"""
	deployed = false
	if len( re.findall(appConfig["name"], ls('/AppDeployments')) ) > 0:
		deployed = true
	return deployed

try:
	# return a PropertiesFile object containing the ant namespace properties
	pf = XmlProperties("tmp/ant-properties.xml").getAntProperties()
	debug = pf.get("weblogic.script.debugging")
	if debug == "on":
		debugging = true
	else:
		debugging = false
	action = pf.get("deployApplications.action")
	if not (action == "deploy" or action == "undeploy"):
		print "Action must be 'deploy' or 'undeploy'"
		exit(exitcode=2)
	
	
	# Holder for name of domain to which we're currently connected:
	# use it to avoid re-connecting to domain already connected
	currentDomain = None
	pscs = pf.getPartialKey("*.pscname")
	applications = []
	for k, v in pscs:
		if pf.get(v + ".technology") == "webapp":
			applications.append(v)
	for artefact in applications:
		appConfig = ApplicationDeploymentConfig(artefact, pf).getConfig()
		print "Processing properties for psc %s" % (artefact)
		
		targetDomain = appConfig["domain"]
		if not (targetDomain == currentDomain) :
			# Change domain
			if not (currentDomain == None) :
				disconnect();
				currentDomain = None
			# Load target domain specification properties
			adminUserName = appConfig["admin.user"]
			adminPassword = appConfig["admin.password"]
			url = appConfig["admin.url"]
			if (debugging) :
				print "Connecting to " + url + " using admin username " + adminUserName
			if connectToAdminServer(adminUserName, adminPassword,  url):
				currentDomain = targetDomain
			else:
				print "Unable to connect to domain " + targetDomain + " admin server"
				print "Cancelling deployment and aborting"
				exit(exitcode=1)
		currentDomain = targetDomain
		# Ready to perform the deployment action
		try:
			if (action == "deploy"):
				target = appConfig["target"]
				applicationEar = appConfig["deployable"]
				print "Deploying application '" + artefact + "' from file '" + applicationEar + "' to target: " + target
				if not deployApplication (appConfig):
					print "[ERROR] failed to deploy application " + appConfig["name"]
					raise Exception("deployApplication failed")
			else: # undeploy
				print "Undeploying application named '", artefact, "'"
				undeployApplication(appConfig)
		except:
			print "Unexpected error: ", sys.exc_info()[0], sys.exc_info()[1]
			print "An exception has occurred; cancelling deployment action and aborting"
			disconnect(force="true")
			exit(exitcode=1)
	
	# We're done, so disconnect from any domain to whcih we're still connected
	if not (currentDomain == None) :
		disconnect();
except:
	print "Unexpected error: ", sys.exc_info()[0], sys.exc_info()[1]
	if (debugging) :
		dumpStack()
	exit(exitcode=1)


