import os
import sys

from pyalerts.scheduler.queue import queue_job

def list_dir(path):
	contents = []
	for _, subdirs, files in os.walk(path):
		for subdir in subdirs:
			dirname = os.path.join(_, subdir)
			for item in os.listdir(dirname):
				filename = os.path.join(dirname, item)
				contents.append(filename)


queue_job(list_dir, '/home/lee/pyalerts')