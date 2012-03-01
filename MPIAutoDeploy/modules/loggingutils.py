
class SimpleReporter:
	def report(self, errString, level="i"):
		levels = {"i" : "[INFO] ", "w" : "[WARN] ", "e" : "[ERROR] "}
		print levels[level] + errString
