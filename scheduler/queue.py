from __future__ import print_function, absolute_import
import os
import re
import rq
import sys
import redis
import pyalerts

from rq import Worker, Queue, Connection


config = pyalerts.config
port = config['redis']['port']

listen = ['default']
redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:{0}'.format(port))

conn = redis.from_url(redis_url)

q = Queue(connection=conn)
def queue_job(job, *args):
	job = q.enqueue_call(
		func=job, args=('{0}'.format(*args),), result_ttl=5000
	)

	print(job.get_id())