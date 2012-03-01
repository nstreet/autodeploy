:: start wlst the same way as ant does
:: add the osb jars
@echo off
call osb-jars.cmd
:: are we running a script
set script=
set scripthome=modules/
set scriptname=%1
if not "%scriptname%"=="" (
	set script=%scripthome%%1.py
)
:: fire up wlst shell
java -Dpython.path=modules -Dweblogic.security.TrustKeyStore=CustomTrust -Dweblogic.security.CustomTrustKeyStoreFileName=AppsMPITrustList.jks -Dweblogic.security.CustomTrustKeystorePassPhrase=Password123!MP -Dweblogic.security.SSL.ignoreHostnameVerification=true weblogic.WLST %script%