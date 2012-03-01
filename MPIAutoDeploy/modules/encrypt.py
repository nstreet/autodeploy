import os, sys
from crypto import EncryptedPassword
from crypto import MaskingPassword
while true:
	MaskingThread = MaskingPassword("-")
	MaskingThread.start()
	input1 = raw_input("Enter the password: ")
	input2 = raw_input("Confirm password: ")
	MaskingThread.stop()
	if input1 == input2:
		break
	else:
		print "[WARN] confirmation does not match the original password"
password = input1.strip()
ep = EncryptedPassword()
encrypted = ep.encrypt(password)
print "[INFO] encrypted password is : %s" % (encrypted)
