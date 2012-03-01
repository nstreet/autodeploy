:: used to out all of the osb jars on the classpath
:: this is done in ant using a classpath configuration
:: this doe the same thing for using wlst interactively
if not "%OSB_JARS_RUN%" EQU "true" (
	set CLASSPATH=%CLASSPATH%;C:\Tool\bea\osb_10.3\lib\alertfwk.jar;C:\Tool\bea\osb_10.3\lib\alsb.jar;C:\Tool\bea\osb_10.3\lib\debuglog.jar;C:\Tool\bea\osb_10.3\lib\emplugin_client.jar;C:\Tool\bea\osb_10.3\lib\emplugin_kernel.jar;C:\Tool\bea\osb_10.3\lib\sb-debugfwk.jar;C:\Tool\bea\osb_10.3\lib\sb-kernel-api.jar;C:\Tool\bea\osb_10.3\lib\sb-kernel-common.jar;C:\Tool\bea\osb_10.3\lib\sb-kernel-impl.jar;C:\Tool\bea\osb_10.3\lib\sb-kernel-resources.jar;C:\Tool\bea\osb_10.3\lib\sb-mdif-endpoint.jar;C:\Tool\bea\osb_10.3\lib\sb-schemas.jar;C:\Tool\bea\osb_10.3\lib\sb-security.jar;C:\Tool\bea\osb_10.3\lib\sb-transports-main.jar;C:\Tool\bea\osb_10.3\lib\stage-utils.jar;C:\Tool\bea\osb_10.3\lib\uddi_client_v3.jar;C:\Tool\bea\osb_10.3\lib\uddi_library.jar;C:\Tool\bea\osb_10.3\lib\version.jar;C:\Tool\bea\osb_10.3\lib\ws-core.jar
	set OSB_JARS_RUN=true
)