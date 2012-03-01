# Shutsdown the weblogic cluster
# Author : Surendar Patchimalla

if __name__ == '__main__': 
    from wlstModule import *#@UnusedWildImport
_serverNames=[]

def connectToDomain( url, username,  password):

    print 'Using connection details ' + url + ', ' + username + ' , ' + password
    connect(username,password,url)

def shutdownCluster(clustername):
    try:
        serverConfig()
        print "Shuting Down" + clustername + "  Cluster" 
        shutdown(clustername,'Cluster','true', 10, 'true','true')


               
    except java.lang.Exception, usoe:
        print "shutdown module failed"
        dumpStack()
        pass
try:
   
    username = sys.argv[2]
    password = sys.argv[3]
    url = sys.argv[1]
    clustername = sys.argv[4]
    connectToDomain(url,username,password)
    shutdownCluster(clustername)

    print "script returns SUCCESS"   
except Exception, e:
    print e 
    dumpStack()
    raise 
    
