## Checks the servers status
## Author - Neil Street 
## intended to functionally replace checkAndStart.py
"""
parse the weblogic-domain.properties file
for each domain
	list the clusters
	check that the cluster's managed servers are up
	if not, bomb
	
this is pretty crude and may benefit from some cleverness
"""
import sys
from propertiesutils import PropertiesFile
from wlstutils import ServerConnection
from propertiesutils import XmlProperties
    
try:
	tp = XmlProperties("tmp/ant-properties.xml")
	tp.transformProperties("tmp/ant-properties.properties")
	pf = PropertiesFile("tmp/ant-properties.properties")
	adminServers = pf.getPartialKey("*.domain_name")
	for k, v in adminServers:
		prefix = k.split(".")[0]
		username = pf.get(prefix + ".admin_user")
		password = pf.get(prefix + ".admin_password")
		url = pf.get(prefix + ".admin_url")
		sc = ServerConnection(url, username, password)
		sc.logOn()
		clusters = sc.listClusters()
		for cluster in clusters:
			if not sc.clusterIsUp(cluster):
				print "[ERROR] One or more managed servers is not running"
				sys.exit(1)
	print "[INFO] all managed servers are running"
except Exception, e:
    print e 
    dumpStack()
    raise 
    
