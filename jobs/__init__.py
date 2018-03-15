from __future__ import print_function, absolute_import, unicode_literals
import os
import sys
import json
import redis
import argparse


parser = argparse.ArgumentParser(description='Create jobs to execute asynchronous commands')
parser.add_argument('--host', dest='host',
					action='append',
					required=True,
					help='Target host(s)')
parser.add_argument('--master', dest='master',
					required=True,
					help='Master server to send output to')
parser.add_argument('--verbose', dest='verbose',
					action='store_true',
					help='Verbose output')
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('--command', dest='command',
					help='Command to be executed')
group.add_argument('--code', dest='code',
					help='Script file to be ran')
args = parser.parse_args()

r = redis.Redis('localhost')


def create_job(r, hosts, command, code, master):
	job_id = r.incr('job_id')
	data = {}
	data['id'] = hosts
	if command is not None:
		data['command'] = command
	if code is not None:
		try:
			f = open(code, 'r')
			data['code'] = f.read()
			f.close()
		except IOError:
			raise Exception('Unable to read file: {}'.format(code))

	data['master'] = master
	return (job_id, data)


def store_job(r, job_id, data):
	text = json.dumps(data)
	key = 'job:' + str(job_id)
	if args.verbose is True:
		print('Storing \'{}\': {}'.format(key, text))
	r.set(key, text)
	if args.verbose is True:
		print('Adding job id: {} to job queue'.format(str(job_id)))
	r.rpush('job_queue', job_id)


def wait_for_results(r, job_id, hosts):
	key = 'job_done:{}'.format(job_id)
	if args.verbose is True:
		print('Waiting for results in job queue {}'.format(key))
	for host in hosts:
		(queue, h) = r.blpop(key)
		if args.verbose is True:
			print('Results retrieved from {}'.format(h))


def print_results(r, job_id, hosts):
	hosts.sort()
	for host in hosts:
		text = r.get('Job result: {}:{}'.format(str(job_id), host))
		data = json.loads(text)
		output = data['results'].rstrip()
		print('{} => {}'.format(host, output))