import zmq
import sys
import time
import subprocess
import psutil

import pyalerts
from pyalerts.utils.system import System


config = pyalerts.config
port = config['drone']['ports']['zmq']

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind('tcp://*:{0}'.format(port))

# Listen for command
while True:
	proc = socket.recv()
	try:
		command = int(getattr(System, proc))
		socket.send('{0}'.format(command))
	except:
		pass