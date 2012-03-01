@echo off
:: ## wrapper for the autodeploy ant script
:: ## all properties should come from property files
:: ## environment-config.properties = properties describing the deployment session
:: ## local-environment.properties = properties that are specific to this machine
:: ## global-environment.properties = properties that are common to all deployments
:: ## package properties = properties that are supplied in this deployment package
:: ## the environment will be set using the setenv batch file this is stuff that is required to run ant and the weblogic ant tasks
:: ## this wrapper validates the value of %1 against the contents of the text file modules\valid-autodeploy-targets.txt
:: ## it then checks for the presence of each of the other required locally variable bits of information in the environment
:: ## and either prompts for input or asks for confirmation

goto start
:usage
echo usage:
echo.
echo autodeploy ^<argument^>
echo.
echo where valid arguments are:
for /F "eol=# tokens=1 delims=," %%t in (.\valid-autodeploy-targets.txt) do echo %%t
goto finish

:start
if NOT "%PACKAGE_HOME%" == "" (
	call setenvfromproperties.cmd
)
:parse-args
if /I "%1" == "" goto no-more-args
if /I "%1" == "-q" (
	set QUIET=true
	shift
	goto parse-args
) else (
	set GOAL=%1
	shift
	goto parse-args
)
:no-more-args
set VALID_TARGET=false
set REQUIRES_WL_PROPERTIES=false
for /F "eol=# tokens=1,2,3,4 delims=, " %%t in (.\valid-autodeploy-targets.txt) do if "%GOAL%" == "%%t" (
	set VALID_TARGET=true
	set REQUIRES_WL_PROPERTIES=%%u
	set PACKAGE_REQUIRED=%%v
	set INTEGRATED_GOAL=%%w
)
if "%VALID_TARGET%" == "false" (
	echo "%GOAL%" is not a valid argument
	goto usage
	)
:: DEBUG
if /I "%DEBUG%" == "ON" (
	echo .
	echo ^<DEBUG^>
	echo VALID_TARGET="%VALID_TARGET%"
	echo REQUIRES_WL_PROPERTIES="%REQUIRES_WL_PROPERTIES%"
	echo PACKAGE_REQUIRED="%PACKAGE_REQUIRED%"
	echo INTEGRATED_GOAL="%INTEGRATED_GOAL%"
	echo command-line=%1
	echo ^<\DEBUG^>
	echo .
)

:: if the package is not required skip package related validation
:checkPackageHome
if /I "%QUIET%" == "true" goto donepackagecheck
if /I "%PACKAGE_REQUIRED%" == "false" (
	goto donepackagecheck
)
if "%PACKAGE_HOME%" == "" (
	set /p PACKAGE_HOME=Please enter the home directory of the package: 
	)
echo The PACKAGE_HOME variable is set to:
echo %PACKAGE_HOME%
ECHO.
ECHO.
set /p YESNO=is this correct? (y or n): 
if /I NOT "%YESNO%" == "Y" (
	set PACKAGE_HOME=
	goto checkPackageHome 
	)
set YESNO=
ECHO.
ECHO.

:checkCRNumber
if "%CHANGE_REQUEST_NUMBER%" == "" (
	set /p CHANGE_REQUEST_NUMBER=Please enter Change Request Number: 
	)
echo Change Request Number is set to:
echo %CHANGE_REQUEST_NUMBER%
ECHO.
set /p YESNO=is this correct? (y or n): 
if /I NOT "%YESNO%" == "Y" (
	set CHANGE_REQUEST_NUMBER=
	goto checkCRNumber
	)
set YESNO=
ECHO.
ECHO. 

:beahome
if "%BEA_HOME%" == "" (
	set /p BEA_HOME=Please enter the path for BEA_HOME: 
	)
echo BEA_HOME is set to: %BEA_HOME%
ECHO.
set /p YESNO=is this correct? (y or n): 
if /I NOT "%YESNO%" == "Y" (
	set BEA_HOME=
	goto beahome
	)
set YESNO=
ECHO.
ECHO.
	
if NOT EXIST %BEA_HOME%\modules\com.bea.common.configfwk_1.2.1.0.jar (
	echo The path for BEA_HOME is  %BEA_HOME%  not right .. Please check and try again
	goto beahome
	)

if NOT EXIST %BEA_HOME%\wlserver_10.3\server\bin\setWLSEnv.cmd (
	echo The path for BEA_HOME is  %BEA_HOME%  not right .. Please check and try again
	goto beahome
	)

	
:osbhome
if "%OSB_HOME%" == "" (
	set /p OSB_HOME=Please enter the path for OSB_HOME: 
	)
echo OSB_HOME is set to: %OSB_HOME%
ECHO.
set /p YESNO=is this correct? (y or n): 
if /I NOT "%YESNO%" == "Y" (
	set OSB_HOME=
	goto osbhome
	)
set YESNO=
ECHO.
ECHO.

if NOT EXIST %OSB_HOME%\lib\alsb.jar (
	echo The path for BEA_HOME is  %OSB_HOME%  not right .. Please check and try again
	goto osbhome
	)
:donepackagecheck


:: CALL setEnv.bat
:: check that the required property files are available depending on the target
:: this doesn't look very elegant but there probably isn't a good way of doing this 
:: that is very extendable. We already know that %1 is one of the entries in valid-autodeploy-targets.txt
::
:: to add a target validation:
:: 	if "%1" == "target" goto label
:: 	goto skip_label
:: 	:label
:: 	validation code...
:: 	:skip_label


if "%REQUIRES_WL_PROPERTIES%"=="true" (

	if  NOT EXIST weblogic-domain.properties  (
		echo There is no weblogic-domain.properties  .. Please check the documentation and try again
		goto finish	
		)  else  goto runcommand

		


	if NOT EXIST local-environment.properties {
		echo There is no local-environment.properties  .. Please check the documentation and try again
		goto finish	
		}  else  goto runcommand



	if NOT EXIST global-environment.properties {
		echo There is no global-environment.properties  .. Please check the documentation and try again
		goto finish	
		}  else  goto  runcommand
)


:runcommand
if /I "%INTEGRATED_GOAL%" == "true" GOTO %GOAL%


:: the -D options have to contain something
if "%PACKAGE_HOME%" == "" set PACKAGE_HOME=foo & goto checkcr
echo Cleaning up generated files
if  EXIST %PACKAGE_HOME%\_*  del /F  _*
if  EXIST %PACKAGE_HOME%\*.lok  del /F *.lok
:checkcr
if "%CHANGE_REQUEST_NUMBER%" == "" set CHANGE_REQUEST_NUMBER=autodeploy
:antgo
:: DEBUG
if /I "%DEBUG%" == "ON" (
	echo .
	echo ^<DEBUG^>
	echo running :ant -Dpackage.home=%PACKAGE_HOME% -Dchange.request.no=%CHANGE_REQUEST_NUMBER% %GOAL%
	echo ^<\DEBUG^>
	echo .
)
ant -Dchange.request.no=%CHANGE_REQUEST_NUMBER% %GOAL% 
goto finish

:package-prepare
echo [INFO] processing the zipped distribution
java org.apache.tools.ant.launch.Launcher create-temp-package
if /I "%DEBUG%" == "ON" (
	echo .
	echo ERRORLEVEL=%ERRORLEVEL% 
	echo .
)
if ERRORLEVEL 1 (
	echo [ERROR] processing of distribution zip failed
	goto finish
)
echo [INFO] preparing the extracted zip for the target environment
java org.apache.tools.ant.launch.Launcher prepare-package-for-environment
call setPACKAGE_HOME & erase setPACKAGE_HOME.cmd
:finish
set GOAL=.
set QUIET=.
