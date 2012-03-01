@rem ##
@rem ## this assumes that you are running this file from its directory
@rem ##
@echo off

if /I "%AUTODEPLOY_SETENV_RUN%" == "true" (
	@echo --------------------------------------------------------
	@echo [WARNING] setenv has already been run
	@echo           if you have changed the environment in any way
	@echo           start a new command line and rerun
	GOTO finish
)
:: parse the local-environment.properties file and set the environment variables accordingly
call setenvfromproperties.cmd
if ERRORLEVEL 1 (
	echo [ERROR] ERRORLEVEL is set - not running WLST environment setup
	echo [ERROR] if there are no other error messages
	echo [ERROR] try running in a new command shell
	goto finish
)
@ rem  PLEASE DONT CHANGE THE BELOW

set AUTODEPLOY_HOME=%cd%
set ANT_HOME=%AUTODEPLOY_HOME%/ANT_1.7.1.v20100518-1145
set JAVA_HOME=%JROCKIT_HOME%
set CHANGE_REQUEST_NUMBER=autodeploy


@ REM DONT CHANGE THE BELOW
if NOT "%cd%\" == "%~dp0" (
	echo ----------------------------------------------------
	echo Please run this file from %~pd0
	echo just in case there is a problem with relative paths
	echo -----------------------------------------------------
	goto finish
)

@ REM Please don't change the below

set CLASSPATH=
set OLD_PATH=%PATH%
set PATH=
set PATH=%ANT_HOME%\bin;%JAVA_HOME%\bin
@echo [INFO] running weblogic provided environment setup: %WL_HOME%\server\bin\setWLSEnv.cmd
CALL %WL_HOME%\server\bin\setWLSEnv.cmd
set PATH=%PATH%;%OLD_PATH%
set CLASSPATH=%CLASSPATH%;%WL_HOME%\server\lib\weblogic.jar;%WL_HOME%\..\modules\com.bea.common.configfwk_1.2.1.0.jar;%OSB_HOME%\lib\alsb.jar;.\lib\custom_wsdl_validation.jar
set ANT_HOME=%AUTODEPLOY_HOME%\ANT_1.7.1.v20100518-1145
set AUTODEPLOY_SETENV_RUN=true
:finish


