import unittest
import testpropertiesutils
import testhelpers
import testwlstutils
import testcrypto
import testmanifest
import testdeploymetadata
import testftpsitenav
# propertiesutils
suite = testpropertiesutils.suite()
runner = unittest.TextTestRunner()
runner.run(suite)
# helpers
suite = testhelpers.suite()
runner = unittest.TextTestRunner()
runner.run(suite)
# wlstutils
suite = testwlstutils.suite()
runner = unittest.TextTestRunner()
runner.run(suite)
# crypto
suite = testcrypto.suite()
runner = unittest.TextTestRunner()
runner.run(suite)
# manifest
suite = testmanifest.suite()
runner = unittest.TextTestRunner()
runner.run(suite)
# deploymetadata
suite = testdeploymetadata.suite()
runner = unittest.TextTestRunner()
runner.run(suite)
# ftpsitenav
suite = testftpsitenav.suite()
runner = unittest.TextTestRunner()
runner.run(suite)
