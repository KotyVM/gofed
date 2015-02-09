#!/bin/python

from modules.Packages import Package
from modules.Packages import loadPackages
import optparse
from modules.Config import Config
from modules.ImportPaths import getDevelImportedPaths
from modules.ImportPaths import getDevelProvidedPaths

from time import time, strftime, gmtime
import sys

def getImportPaths(data):
	lines = []
	for devel in data:
		paths = ",".join(data[devel]['provides'])
		lines.append("Provides:%s:%s" % (devel, paths))
	return lines

def getImportedPaths(data):
	lines = []
	for devel in data:
		paths = ",".join(data[devel]['provides'])
		lines.append("Imports:%s:%s" % (devel, paths))
	return lines

def createDB():
	db_path = Config().getImportPathDb()
	if db_path == "":
		return False

	packages = loadPackages()
	pkg_cnt = len(packages)
	pkg_idx = 1

	with open(db_path, 'w') as file:
		for package in packages:
			starttime = time()
			file.write("# Scanning %s ... \n" % package)
			# TODO: add a progres how many packages are left (already/all)
			sys.stdout.write("Scanning %s ... %s/%s " % (package, pkg_idx, pkg_cnt))
			pkg = Package(package)
			info = pkg.getInfo()
			file.write("\n".join(getImportPaths(info)) + "\n")
			file.write("\n".join(getImportedPaths(info)) + "\n")
			pkg_idx += 1
			endtime = time()
			elapsedtime = endtime - starttime
			print strftime("[%Hh %Mm %Ss]", gmtime(elapsedtime))
	return True

def displayPaths(paths, prefix = '', minimal = False):
	for pkg in paths:
		found = False
		ips = []
		for path in paths[pkg]:
			if path.startswith(prefix):
				found = True
				ips.append(path)
			
		if found:
			print pkg
			if not minimal:
				for ip in ips:
					print "\t%s" % ip

if __name__ == "__main__":

	parser = optparse.OptionParser("%prog [-c] [-i|-p [-s [-m]]]")

	#parser.add_option_group( optparse.OptionGroup(parser, "directory", "Directory to inspect. If empty, current directory is used.") )

	parser.add_option(
	    "", "-c", "--create", dest="create", action = "store_true", default = False,
	    help = "Create database of import and imported paths for all available builds of golang devel source packages"
	)

	parser.add_option(
	    "", "-i", "--imported", dest="imports", action = "store_true", default = False,
	    help = "List all import paths devel packages need"
	)

	parser.add_option(
	    "", "-p", "--provided", dest="provides", action = "store_true", default = False,
	    help = "List all import paths devel packages provide"
	)

	parser.add_option(
	    "", "-s", "--prefix", dest="prefix", default = "",
	    help = "Prefix of import paths to display. Used with -i and -p options."
	)

	parser.add_option(
	    "", "-m", "--minimal", dest="minimal", action = "store_true",  default = False,
	    help = "List only packages. Used with -s option."
	)

	options, args = parser.parse_args()

	if options.create:
		if createDB():
			print "DB created"
		else:
			print "DB not created"
	elif options.imports:
		paths = getDevelImportedPaths()
		displayPaths(paths, options.prefix, options.minimal)
	elif options.provides:
		paths = getDevelProvidedPaths()
		displayPaths(paths, options.prefix, options.minimal)
	else:
		print "Synopsis: prog [-c] [-i|-p [-s [-m]]]"
		exit(1)

	exit(0)