@echo off
@echo setting environment properties using values in local-environment.properties
@echo which should have been edited to describe the local install directories
@echo ---------------------------------------------------------------------------
for /F "eol=# tokens=1,2 delims==" %%i in (local-environment.properties) do (
	if /I "%%i" == "osbimp.install.path" (
		echo [INFO] setting environment variable OSB_HOME=%%j
		set OSB_HOME=%%j
	)
	if /I "%%i" == "wl.home" (
		echo [INFO] setting environment variable WL_HOME=%%j
		set WL_HOME=%%j
		echo [INFO] setting environment variable BEA_HOME=%%j/..
		set BEA_HOME=%%j/..
	)
	if /I "%%i" == "jrockit.home" (
		echo [INFO] setting environment variable JROCKIT_HOME=%%j
		set JROCKIT_HOME=%%j
	)
)	
@echo ---------------------------------------------------------------------------
@echo [INFO} validating...
set VALID_ENVIRONMENT=true
if NOT EXIST %OSB_HOME%\lib\alsb.jar (
	@echo [ERROR] %OSB_HOME%\lib\alsb.jar does not exist
	@echo [ERROR] invalid setting for osb.install.path in local-environment.properties
	set VALID_ENVIRONMENT=false
)
if NOT EXIST %WL_HOME%\server\bin\setWLSEnv.cmd (
	@echo [ERROR] %WL_HOME%\server\bin\setWLSEnv.cmd does not exist
	@echo [ERROR] invalid setting for wl.home in local-environment.properties
	set VALID_ENVIRONMENT=false
)
if NOT EXIST %BEA_HOME%\modules\com.bea.common.configfwk_1.2.1.0.jar (
	@echo [ERROR] %BEA_HOME%\modules\com.bea.common.configfwk_1.2.1.0.jar does not exist
	@echo [ERROR] invalid setting for wl.home in local-environment.properties
	@echo [ERROR] its parent directory is assumed to contain modules\com.bea.common.configfwk_1.2.1.0.jar
	set VALID_ENVIRONMENT=false
)
if NOT EXIST %JROCKIT_HOME%\jre\bin\java.exe (
	@echo [ERROR] %JROCKIT_HOME%\jre\bin\java.exe does not exist
	@echo [ERROR] invalid setting for jrockit.home in local-environment.properties
	set VALID_ENVIRONMENT=false
)
if /I "%VALID_ENVIRONMENT%" == "false" (
	@echo [ERROR] one or more problems exists with local-environment.properties
	@echo [ERROR] please correct the properties and rerun in a new command shell
	@echo ---------------------------------------------------------------------------
	set IGNORE_THIS_ERROR__SETTING_ERRORLEVEL
	goto finish
) else (
	@echo [INFO] local-environment.properties validated OK
	@echo ---------------------------------------------------------------------------
)
:: if PACKAGE_HOME is already set ok
:: otherwise try and set it
if NOT "%PACKAGE_HOME%" == "" goto finish
for /F "eol=# tokens=1,2 delims==" %%i in (environment-config.properties) do (
	if /I "%%i" == "package.home" (
		echo [INFO] setting PACKAGE_HOME=%%j
		set PACKAGE_HOME=%%j
	)
)

:finish