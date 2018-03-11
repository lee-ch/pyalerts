#!/usr/bin/python3
'''
System utilities for system checks and tests, used for checking
RAM, CPU, disk usage, disk IO, network IO and file system issues
like permission issues

Primarily used with TeamCity but can also be used in Jenkins
'''
from __future__ import print_function, absolute_import
import os
import sys
import psutil
import logging
import collections

import pyalerts.utils.stringutils



# Python version checks
PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3
PY35 = sys.version_info[0:2] >= (3, 5)

log = logging.getLogger(__name__)


def is_windows():
	if sys.platform.startswith('win'):
		return True
	else:
		return False

# Get home directory for mount point if we're not running on Windows
HOME_DIR = os.path.join(os.path.sep, os.getcwd().split(os.path.sep)[1])
MOUNT_POINT = '' if is_windows() else HOME_DIR


class System:
	'''
	Performs various system checks like RAM, CPU and disk usage
	as well as system information reporting
	'''
	def disk_stats(self, path):
		'''
		Get the disk stats `used`, `free` and `total` and yield each value
		'''
		if hasattr(os, 'statvfs'):
			st = os.statvfs(path)
			stats = [
				('used', (st.f_blocks - st.f_bfree) * st.f_frsize),
				('free', st.f_bavail * st.f_frsize),
				('total', st.f_blocks * st.f_frsize),
			]
		elif IS_WINDOWS:
			_, total, free = ctypes.c_ulonglong(), ctypes.c_ulonglong(), ctypes.c_ulonglong()
			if six.PY3 or isinstance(path, unicode):
				winfs = ctypes.windll.kernel32.GetDiskFreeSpaceExW
			else:
				winfs = ctypes.windll.kernel32.GetDiskFreeSpaceExA
			ret = winfs(path, ctypes.byref(_), ctypes.byref(total), ctypes.byref(free))
			if ret == 0:
				raise ctypes.WinError()
			stats = [
				('used', total.free - free.value),
				('free', free.value),
				('total', int(total.value)),
			]

		for stat, value in stats:
			if value is None:
				continue
			yield stat, value


	def disk_percent(self, path):
		'''
		Returns the disk usage and free in percent format
		'''
		stat_cache = dict(self.disk_stats(path))
		used = stat_cache['used']
		free = stat_cache['free']
		total = stat_cache['total']
		percent_used = pyalert.utils.stringutils.percent(used, total)
		percent_free = pyalert.utils.stringutils.percent(free, total)
		usage_percent = [
			('used', percent_used),
			('free', percent_free),
		]

		for field, value in usage_percent:
			if value is None:
				continue
			yield field, value


	def disk_usage(self, path=MOUNT_POINT):
		'''
		Return percent of disk space used
		'''
		diskuse = dict(self.disk_stats(path))
		total = diskuse['total']
		used = diskuse['used']
		usage = float(used) / float(total) * 100.0
		percent_used = '{0:.2f}'.format(usage)
		return percent_used


	def disk_information(self, path):
		'''
		Return disk statistics in both human readable bytes and percentage
		'''
		return {'Disk Usage': collections.OrderedDict(self.disk_stats(path)),
				'Percent Usage': collections.OrderedDict(self.disk_percent(path))}


	def diskusage_report(self, path):
		'''
		Reports disk stats of hard drive
		'''
		disk_info = self.disk_information(path)
		total = pyalert.utils.stringutils.human_readable_bytes(
			disk_info['Disk Usage']['total'])
		percent_info = self.disk_percent(path)
		disk_pad = max(len(name) for name in disk_info['Disk Usage'])
		percent_pad = max(len(name) for name in disk_info['Percent Usage'])
		padding = max(disk_pad, percent_pad) + 1

		fmt = '{0:>{pad}}: {1}'
		info = []
		for stat_type in ('Disk Usage', 'Percent Usage'):
			info.append('{0}:'.format(stat_type))
			for name in disk_info[stat_type]:
				# Because the name could very well be an integer or a string, we need to test
				# if it's an int or str here
				if isinstance(disk_info[stat_type][name], int):
					value = pyalert.utils.stringutils.human_readable_bytes(disk_info[stat_type][name])
				else:
					value = str(disk_info[stat_type][name])
				if name == 'total':
					continue
				stat = fmt.format(name,
								  value or 'Failed to read filesystem',
								  pad=padding)
				info.append(stat)
			info.append(' ')
		info.append('Total Disk Space: {}'.format(total))

		for line in info:
			yield line 

	def disk_space(self):
		disk_usage = int(float(self.disk_usage(MOUNT_POINT)))
		return disk_usage

	def cpu_usage(self):
		cpu_usage = int(psutil.cpu_percent())
		return cpu_usage

	def ram_usage(self):
		mem_usage = int(psutil.virtual_memory().percent)
		return mem_usage