
#Conditionally import wlstModule only when script is executed with jython
if __name__ == '__main__': 
    from wlstModule import *#@UnusedWildImport
_serverNames=[]

def connectToDomain( url, username,  password):
    connect(username,password,url)

def FindApp(name, appversion):
    try:
        serverConfig()
        print "Finding Application " + name + "#" + appversion 
        theBean = cmo.lookupAppDeployment(name + "#" + appversion)
        #print 'Checking ... ' + name + "#" + appversion
        if theBean != None:
            print " A version of PSC " + name + "has been found running on the server(s)"
            fileName = name + '.lok'
            fl=open(fileName,'a')
            fl.write( '\n' )
            fl.close()
               
    except java.lang.Exception, usoe:
        print "FindApp module failed"
        dumpStack()
        pass
try:
   
    username = sys.argv[2]
    password = sys.argv[3]
    url = sys.argv[1]
    appname = sys.argv[4]
    appversion = sys.argv[5]
    connectToDomain(url,username,password)
    FindApp(appname, appversion)

    print "script returns SUCCESS"   
except Exception, e:
    print e 
    print "Error while trying to save and/or activate!!!"
    dumpStack()
    raise 
    
