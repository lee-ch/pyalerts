from __future__ import print_function, division
import os
import re
import datetime

from subprocess import PIPE
from subprocess import Popen
from subprocess import STDOUT



def gitDescribe(version):
	'''
	git describe produces version in the form of: x.x.x-xx
	'''
	VERSION_MATCH = re.compile(r'v(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)(-(?P<dev>\d+))?')
	v = VERSION_MATCH.search(version)
	if v:
		major = int(v.group('major'))
		minor = int(v.group('minor'))
		patch = int(v.group('patch'))
		if v.group('dev'):
			dev = int(v.group('dev'))
			return '{}.{}.{}-{} dev'.format(major, minor, patch, dev)
		return '{}.{}.{}'.format(major, minor, patch)
	return v


def getVersion(init_file):
	try:
		cwd = os.path.dirname(os.path.abspath(init_file))
		fn = os.path.join(cwd, 'VERSION')
		with open(fn) as f:
			return f.read().strip()
	except IOError:
		pass

	try:
		p = Popen(['git', 'describe', '--tags', '--always'], stdout=PIPE, stderr=STDOUT, cwd=cwd)
		out = p.communicate()[0]

		if (not p.returncode) and (out):
			v = gitDescribe(str(out))
			if v:
				return v
	except OSError:
		pass

	return 'latest'


version = getVersion(__file__)
__version__ = version