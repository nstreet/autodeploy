import os, sys, wl
from java.io import IOException
from java.security import GeneralSecurityException
from javax.crypto import Cipher
from javax.crypto import SecretKey
from javax.crypto import SecretKeyFactory
from javax.crypto.spec import PBEKeySpec
from javax.crypto.spec import PBEParameterSpec
from sun.misc import BASE64Decoder
from sun.misc import BASE64Encoder
from java.lang import String as JavaString
import threading
from java.io import *
from java.lang import Thread

class EncryptedPassword:
	""" stuff to do with encrypting passwords in property files
	"""
	def __init__(self):
		self.PASSWORD = wl.array("enfldsgbnlsngdlksdsgm", "c")
		self.SALT = wl.array([0xde, 0x33, 0x10, 0x12, 0xde, 0x33,0x10,0x12], "b")
	def encrypt(self, pystrPlaintext):
		try:
			plaintext = JavaString(pystrPlaintext)
			keyFactory = SecretKeyFactory.getInstance("PBEWithMD5AndDES")
			key = keyFactory.generateSecret(PBEKeySpec(self.PASSWORD))
			pbeCipher = Cipher.getInstance("PBEWithMD5AndDES")
			paramSpec = PBEParameterSpec(self.SALT, 20)
			pbeCipher.init(Cipher.ENCRYPT_MODE, key, paramSpec)
			return self._base64Encode(pbeCipher.doFinal(plaintext.getBytes()))
		except:
			raise
	
	def decrypt(self, pystrProperty):
		try:
			strProperty = JavaString(pystrProperty)
			keyFactory = SecretKeyFactory.getInstance("PBEWithMD5AndDES")
			key = keyFactory.generateSecret(PBEKeySpec(self.PASSWORD))
			pbeCipher = Cipher.getInstance("PBEWithMD5AndDES")
			paramSpec = PBEParameterSpec(self.SALT, 20)
			pbeCipher.init(Cipher.DECRYPT_MODE, key, paramSpec)
			return pbeCipher.doFinal(self._base64Decode(strProperty)).tostring()
		except:
			raise
		
	def _base64Encode(self, byteArray):
		return BASE64Encoder().encode(byteArray)
		
	def _base64Decode(self, strProperty):
		return BASE64Decoder().decodeBuffer(strProperty)
		
class MaskingPassword(threading.Thread):
	""" this is a hack to get around not having getpass() available in the jython library
	the idea is to replace typed characters with something else - default is asterisk
	"""
	def __init__(self, maskChar="*"):
		threading.Thread.__init__(self)
		self.stop_event = threading.Event()
		self.maskChar = maskChar
	def stop(self):
		self.stop_event.set()
	def run(self):
		Thread.currentThread().setPriority(Thread.MAX_PRIORITY)
		firstTime = 1
		while not self.stop_event.isSet():
			if not firstTime:
				sys.stdout.write("\010" + self.maskChar)
			firstTime = 0
			Thread.currentThread().sleep(1)
				