import os, sys
from crypto import EncryptedPassword
from crypto import MaskingPassword
MaskingThread = MaskingPassword("-")
MaskingThread.start()
input = raw_input("Enter the password: ")
MaskingThread.stop()
password = input.strip()
print "[INFO] original password is : %s" % (password)
ep = EncryptedPassword()
encrypted = ep.encrypt(password)
print "[INFO] encrypted password is : %s" % (encrypted)
decrypted = ep.decrypt(encrypted)
print "[INFO] when \t\t\t %s\nis decrypted we get\t\t %s\nwhich ought to be the same as\t %s" % (encrypted, decrypted, password)