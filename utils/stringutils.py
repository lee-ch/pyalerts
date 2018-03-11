'''
Functions for manipulating and processing strings
'''
from __future__ import absolute_import, print_function, unicode_literals
import logging
import fnmatch
import shlex
import errno
import time
import re


# We use `__name__` instead of `__file__` because we want the logger's name
# to be the same as this modules name for logging purposes-
log = logging.getLogger(__name__)

def percent(num1, num2, suffix='%'):
	'''
	Return the percentage of `num1` and `num2`
	'''
	nums = float(num1), float(num2)
	percentage = '{0:.2f}'.format((nums[0] / nums[1] * 100))
	formatted = '{percent}{suffix}'.format(percent=percentage, suffix=suffix)
	return formatted



def human_readable_bytes(num, suffix='B'):
	# Converts bytes into human readable format
	units = ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']
	for unit in units:
		if float(num) < 1024.0:
			return '%3.1f%s%s' % (num, unit, suffix)
		num /= 1024.0
	return '%.1f%s%s' % (num, 'Y', suffix)