import os
import sys
import redis
import pyalerts


from pyalerts.jobs.scheduled import *
from pyalerts.scheduler.queue import conn, listen
from rq import Worker, Queue, Connection


if __name__ == '__main__':
	with Connection(conn):
		worker = Worker(list(map(Queue, listen)))
		worker.work()