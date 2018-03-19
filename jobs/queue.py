from __future__ import print_function, absolute_import
import os
import zmq
import sys
import time
import json
import tempfile
import multiprocessing
import subprocess

import pyalerts
import pyalerts.jobs.scheduler

config = pyalerts.config
port = config['master']['ports']['zmq']

def get_job(socket):
	print('Waiting for job to process')
	message = socket.recv()
	print('Retrieved job: {0}'.format(message))
	return json.loads(message)


def process_command(data):
	proc = subprocess.Popen(data['command'],
							stdout=subprocess.PIPE,
							stderr=subprocess.STDOUT,
							shell=True)
	stdout, stderr = proc.communicate('')
	data['exit_code'] = proc.returncode
	data['results'] = str(stdout)
	text = json.dumps(data)
	print('Sending to {0}: {1}'.format(data['receiver'], text))
	context = zmq.Context()
	rep = context.socket(zmq.PUSH)
	rep.connect(data['receiver'])
	rep.send(text)
	rep.close()


def remove_processes(procs):
	for p in procs:
		if not p.is_alive():
			p.join()
			procs.remove(p)
	return procs


context = zmq.Context()
socket = context.socket(zmq.PULL)
socket.bind('tcp://*:{0}'.format(port))
procs = []
while True:
	data = get_job(socket)
	p = Process(target=process_command, args=(data,))
	p.start()
	procs.append(p)
	procs = remove_processes(procs)