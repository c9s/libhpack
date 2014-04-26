#!/usr/bin/env python

# All files in libhpack are Copyright (C) 2014 Alvaro Lopez Ortega.
#
#   Authors:
#    # Alvaro Lopez Ortega <alvaro@gnu.org>
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#    # Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#
#    # Redistributions in binary form must reproduce the above
#       copyright notice, this list of conditions and the following
#       disclaimer in the documentation and/or other materials provided
#       with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


import os
import re
import sys
import fnmatch

def _find_files (paths, match_filter, match_postskip):
	h_files = []
	for d in paths:
		for root, dirnames, filenames in os.walk(d):
			for filename in fnmatch.filter(filenames, match_filter):
				fp = os.path.join(root, filename)
				if not match_postskip in fp:
					h_files.append (fp)
	return h_files

def check_ifdef_HAVE():
	"""Find conditional inclusions in header files.

	Ideally, none of the header files shipped in the library should
	use "#ifdef HAVE_*" preprocessor entries, so the project's
	config.h file doesn't have to by included along with them. This
	function finds the .h files that should be worked out to avoid
	these conditional inclusions.
	"""

	def _check_header (h_path):
		with open(h_path,'r') as f:
			return re.findall(r'\#ifdef\s+(HAVE_.+)\s', f.read()) or []

	def _print_report (offenders):
		if not offenders:
			print "Everything okay!"
			return

		for h in offenders:
			print "[% 2d errors] %s:\n\t%s" %(len(offenders[h]), h, ', '.join (offenders[h]))

		print

	offenders = {}
	for h_path in _find_files (sys.argv[1:], '*.h', '-internal'):
		errors = _check_header(h_path)
		if errors:
			offenders[h_path] = errors

	_print_report (offenders)
	return len(offenders)


def check_common_internal():
	"""Makes sure .c files include the common-internal.h file.

	This function checks the .c files to make sure they include the
	common-internal.h header file. It isn't strictly necessary,
	however it is a good practice that we'd like to enforce. In the
	past we've found a few bugs caused by the lack of some of the
	headers that are pulled from common-internal.h.
	"""

	def _check_header (c_path):
		with open(c_path,'r') as f:
			return ("Doesn't use common-internal.h", None)['common-internal.h' in f.read()]

	def _print_report (offenders):
		print "[% 2d errors] .c files not using common-internal.h:" %(len(offenders))

		if not offenders:
			print "None!"
		else:
			print "\t%s" %("\n\t".join (offenders))

	offenders = []
	for c_path in _find_files (sys.argv[1:], '*.c', '/test/'):
		error = _check_header(c_path)
		if error:
			offenders += [c_path]

	_print_report (offenders)
	return len(offenders)


def main():
	errors = 0
	errors += check_ifdef_HAVE()
	errors += check_common_internal()

	print "\nTotal: %d offending files"%(errors)
	return errors

if __name__ == "__main__":
	sys.exit(main())