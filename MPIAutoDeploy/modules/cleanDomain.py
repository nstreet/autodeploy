# Cleans the apps deployed and the datasources
# Author : Surendar Patchimalla
if __name__ == '__main__': 
    from wlstModule import *#@UnusedWildImport
_serverNames=[]
import re
import os


def connectToDomain( url, username,  password):
    connect(username,password,url)

def cleanApps():
    try:
        stopRedirect()
        serverConfig()
        redirect('_tmpApps', 'false')
        listApplications()
        stopRedirect()
        file = open('_tmpApps','rb')
        counter = 1
        for line in file.readlines():
            pscName = line.rstrip()
            print " Read line " +  str(pscName)
            if( str(pscName).startswith('WLST') ) == true:
                continue
            if len(pscName) != 0:
                result = re.split('(\s)', pscName)
                for i in result:
                    counter = counter + 1
                    if( (str(i).isspace() != true) and (str(i).startswith('[')!=true ) and (str(i) != "")):
                        print 'Undeploying PSC ' + str(i)
                        undeploy(str(i).rstrip(), gracefulIgnoreSessions=true,timeout=6000)
        file.close()
        path=os.getcwd()
        _tmpAppsfile = str(path + '\_tmpApps')
        check_tmpApps= os.path.isfile('_tmpApps')
        if (check_tmpApps):  os.remove(_tmpAppsfile)  
        
    except java.lang.Exception, usoe:
        pass

def getDSList():
    try:
        stopRedirect()
        serverConfig()
        cd('/JDBCSystemResources')        
        redirect('_tmpds', 'false')
        ls()
        stopRedirect()
        file = open('_tmpds','rb')
        datasource_list = []
        for line in file.readlines():
            pscName = line.rstrip()
            #print " Read line " +  str(pscName)
            if( str(pscName).startswith('WLST') ) == true:
                continue
            if len(pscName) != 0:
                result = re.split('(\s)', pscName)
                for i in result:
                    if(str(i).rstrip() == "PersistenceDS"):
                        continue
                    if( (str(i).isspace() != true) and (str(i).startswith('dr-')!=true ) and (str(i) != "")):
                        print 'Removing datastore ' + str(i)
                        datasource_list.append(str(i).rstrip())

        file.close()
        path=os.getcwd()
        _tmpdsfile = str(path + '\_tmpds')        
        check_tmpds= os.path.isfile('_tmpds')       
        if (check_tmpds):  os.remove(_tmpdsfile) 
        return datasource_list
    except java.lang.Exception, usoe:
        pass

def deleteDS(dslist):
        serverConfig()
        edit()
        startEdit()
        cd('/JDBCSystemResources')        
        for line in dslist:
            pscName = line.rstrip()
            if len(pscName) != 0:
                result = re.split('(\s)', pscName)
                for i in result:
                    if(str(i).rstrip() == "PersistenceDS"):
                        continue
                    if( (str(i).isspace() != true) and (str(i).startswith('dr-')!=true ) and (str(i) != "")):
                        print 'Removing datastore ' + str(i)
                        delete(str(i).rstrip(),'JDBCSystemResource')
        save()
        activate()    
    
  
    
try:
   
    #username = 'GWAApplicationsAdmin'
    #password = 'Or@c1e@pp@dm!n'
    #url = 't3s://10.240.15.21:9102'
    username = sys.argv[2]
    password = sys.argv[3]
    url = sys.argv[1]
    connectToDomain(url,username,password)
    serverRuntime()
    svrName = cmo.getName()
    if(str(svrName) == "ORADM20_APP_ADM"):
        cleanApps()
        datasource_list = getDSList()
        deleteDS(datasource_list)

    print "script returns SUCCESS"   
except Exception, e:
    print e 
    print "Error while trying to save and/or activate!!!"
    dumpStack()
    raise 
    
