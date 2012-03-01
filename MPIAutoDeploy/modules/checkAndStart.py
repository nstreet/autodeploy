## Checks the servers status
## Author - Surendar Patchimalla 


if __name__ == '__main__': 
    from wlstModule import *#@UnusedWildImport
_serverNames=[]
import re
import os


def connectToDomain( url, username,  password):
    connect(username,password,url)

def checkAndStart(cluster):
    try:
        redirect('_svrStat', 'false')
        state(cluster,'Cluster')
        file = open('_svrStat','rb')
        for line in file.readlines():
            if( (line.startswith('There')== true) or (line.startswith('States')) or (line.strip() == "") ):
                continue
            strbuf = line.strip()
            status = strbuf.split('---')
            if(str(status[1])!= "RUNNING"):
                print 'Server  State of ' + status[0] + ' is ' + status[1]
                print 'Starting the server'
                start(status[0],'Server')

        stopRedirect()
        file.close()
        path=os.getcwd()
        _tmpsvrStat = str(path + '\_svrStat')
        check_tmpApps= os.path.isfile('_svrStat')
        if (check_tmpApps):  os.remove(_tmpsvrStat)  
        
    except java.lang.Exception, usoe:
        pass

    
try:
   
    #username = 'GWAApplicationsAdmin'
    #password = 'Or@c1e@pp@dm!n'
    #url = 't3s://10.240.15.21:9102'
    #clName='GWA_User_Applications'
    username = sys.argv[2]
    password = sys.argv[3]
    url = sys.argv[1]
    clName = sys.argv[4]
    connectToDomain(url,username,password)
    checkAndStart(clName)



    print "script returns SUCCESS"   
except Exception, e:
    print e 
    dumpStack()
    raise 
    
