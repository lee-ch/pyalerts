from __future__ import print_function, absolute_import
import zmq
import sys
import psutil
import subprocess
import pyalerts


def get_usage(resource):
	'''
	Get system resource ``stat`` usage
	'''
	config = pyalerts.config
	port = config['drone']['ports']['zmq']

	context = zmq.Context()
	socket = context.socket(zmq.REQ)
	socket.connect ('tcp://localhost:{0}'.format(port))

	if type(resource) is not str:
		data = str(resource)
	else:
		data = resource

	socket.send(data)
	reply = socket.recv()

	return reply