from __future__ import print_function, absolute_import
import os
import re
import rq
import sys
import redis
import pyalerts

from rq import Worker, Queue, Connection, get_current_job
from rq.decorators import job


config = pyalerts.config
port = config['redis']['port']
timeout = config['redis']['timeout']

# Set default timeout for failed jobs
if timeout is not None:
	default_timeout = timeout
else:
	default_timeout = 60

listen = ['default']
redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:{0}'.format(port))

conn = redis.Redis()

q = Queue(connection=conn, default_timeout=default_timeout)
def queue_job(job, *args):
	#job = q.enqueue_call(
	#	func=job, args=('{0}'.format(*args),), result_ttl=5000
	#)
	try:
		job = q.enqueue(job, result_ttl=config['redis']['ttl'], *args)
		return job
	except:
		job = q.enqueue_call(
			func=job, args=('{0}'.format(*args),), result_ttl=config['redis']['ttl'])
		return job