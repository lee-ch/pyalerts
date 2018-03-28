'''
pyalerts.transport.master
-------------------------

Used to manually pass process to drone
'''
import zmq
import sys
import psutil
import subprocess
import pyalerts


config = pyalerts.config
port = config['drone']['ports']['zmq']

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect ('tcp://localhost:{0}'.format(port))

def exec_proc(resource):
	if type(resource) is not str:
		data = str(resource)

	try:
		socket.send(data)
		reply = socket.recv()
		if type(reply) is int:
			return int(reply)

		return reply
	except:
		raise Exception(
			'Failed to retrieve system resource: {0}'.format(resource)
		)
	finally:
		socket.send(data)
		reply = socket.recv()

	return reply