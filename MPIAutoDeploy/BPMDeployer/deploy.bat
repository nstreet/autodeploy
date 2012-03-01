@ REM Properties that needs changing

set JAVA_HOME=D:\Java\jrmc-3.1.2-1.6.0
set ANT_HOME=D:\Oracle\BPM_10.3.1\modules\org.apache.ant_1.6.5
set BEA_HOME=D:\Oracle\BPM_10.3.1


@ REM Please don't change the below

set CLASSPATH=
set PATH=
set PATH=%PATH%;%ANT_HOME%\bin;%JAVA_HOME%\bin
CALL %BEA_HOME%\wlserver_10.3\server\bin\setWLSEnv.cmd
set CLASSPATH=%CLASSPATH%;%BEA_HOME%\modules\com.bea.common.configfwk_1.2.1.0.jar
set ANT_ARGS= -lib "D:/Oracle/OraBPMwlHome/lib;D:/Oracle/OraBPMwlHome/ext"
set ant_opts= "-Dsun.lang.ClassLoader.allowArraySyntax=true"

rem ## starting the service
ant -buildfile D:\Tools\BPMDeployer\build.xml bpmremotedeploy





