from __future__ import print_function, absolute_import, unicode_literals
import os
import sys
import json
import redis
import argparse

import pyalerts


def create_job(r, hosts, command, code, drone):
	job_id = r.incr('job_id')
	data = {}
	data['id'] = job_id
	data['hosts'] = hosts
	if command is not None:
		data['command'] = command
	if code is not None:
		try:
			f = open(code, 'r')
			data['code'] = f.read()
			f.close()
		except IOError:
			raise Exception('Unable to read file: {0}'.format(code))

	data['drone'] = drone
	return (job_id, data)


def store_job(r, job_id, data):
	text = json.dumps(data)
	key = 'job:' + str(job_id)
	print('Storing \'{0}\': {1}'.format(key, text))
	r.set(key, text)
	print('Adding job id: {0} to job queue'.format(str(job_id)))
	r.rpush('job_queue', job_id)


def wait_for_results(r, job_id, hosts):
	key = 'job_done:{0}'.format(job_id)
	print('Waiting for results in job queue {0}'.format(key))
	for host in hosts:
		(queue, h) = r.blpop(key)
		print('Results retrieved from {0}'.format(h))


def print_results(r, job_id, hosts):
	hosts.sort()
	for host in hosts:
		text = r.get('Job result: {0}:{1}'.format(str(job_id), host))
		data = json.loads(text)
		output = data['results'].rstrip()
		print('{0} => {1}'.format(host, output))