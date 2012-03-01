from ftplib import FTP
from java.util import Date

class FTPSiteNav:
	""" a wrapper rounf the ftp client to do stuff with ftp sites
	"""
	def __init__(self, host, username=None, password=None):
		self.host = host
		self.login = {"user" : username, "passwd" : password}
		self.lines = []
	def getLatestFromPattern(self, directory, pattern):
		""" takes a pattern containing exactly one asterisk and finds the file that matches with the latest timestamp
		pattern file.name.build.*.ear  => should return the filename with the latest build number and the value of the build number
		as a tuple (file.name.build.nnn.ear, nnn)
		"""
		ftp = FTP(self.host)
		ftp.login(**self.login)
		ftp.sendcmd("cwd " + directory)
		lines = []
		ftp.retrlines("LIST", lines.append)
		self.lines = lines
		matchPatternBits = pattern.split("*")
		matched = 0
		# store the current (date, filename) pair
		current = (("01-01-80","00:59AM"), "")
		for line in lines:
			lineBits = line.split()
			fileName = lineBits[3]
			if fileName.startswith(matchPatternBits[0]) and fileName.endswith(matchPatternBits[1]):
				currentDate = self._createDate(current[0][0], current[0][1])
				thisDate = self._createDate(lineBits[0], lineBits[1])
				if thisDate.after(currentDate):
					current = ((lineBits[0], lineBits[1]), fileName)
		latestFile = current[1]
		latestBit = latestFile[len(matchPatternBits[0]):-len(matchPatternBits[1])]
		return (latestFile, latestBit)
		
	def _createDate(self, date, time):
		""" turn a date and time from the ftp output into a java.util.Date
		"""
		mdyBits = date.split("-")
		m = int(mdyBits[0]) - 1
		d = int(mdyBits[1])
		year = int(mdyBits[2])
		# not wonderfully date-compliant
		if year < 80:
			y = year + 100
		else:
			# later this century we'd probably need to add 200 here
			y = year
		
		hhmmBits = time.split(":")
		if hhmmBits[1].endswith("PM"):
			hh = int(hhmmBits[0]) + 12
		else:
			hh = int(hhmmBits[0])
		mm = int(hhmmBits[1][:-2])
		
		jDate = Date(y, m, d, hh, mm)
		return jDate