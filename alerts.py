from __future__ import print_function, absolute_import, unicode_literals
import os
import sys
import zmq
import yaml
import time
import redis
import json
import socket
import logging

if sys.platform.startswith('win'):
	try:
		import win32event
		import win32service
		import servicemanager
		import win32serviceutil

		from pyalerts.system.windows import PyalertsService
		from pyalerts.system.windows import ctrlHandler
	except ImportError:
		raise Exception(
			'ERROR: PyAlerts requires pywin32 to run on Windows'
		)

from pyalerts.utils.system import System
from slackclient import SlackClient


log = logging.getLogger(__name__)

__BASE_DIR = os.path.abspath(os.path.dirname(__file__))
__CONF_DIR = os.path.join(__BASE_DIR, 'config')
__CONF_FILE = os.path.join(__CONF_DIR, 'config.yml')

with open(__CONF_FILE, 'r') as conf:
  config = yaml.load(conf)

slack_token = config['slack']['token']
slack_webhook = config['slack']['webhook']
alert_channel = config['slack']['channel']
alert_username = config['slack']['username']
alert_timeout = config['config']['timeout']
default_timeout = 60

timeout = alert_timeout if alert_timeout else default_timeout


class PyAlerts:
	'''
	This class has two methods, ``send_alert`` and ``receive_alert`` which send an
	alert to Slack and receives an alert from slack to the alert site configured
	'''
  
	def send_alert(self, channel, username, alert_message):
		message_attachment = [
			{
				"text": "{}".format(alert_message),
				"callback_id": "incident_actions",
				"color": "#f91313",
				"attachment_type": "default",
				"actions": [
					{
						"name": "incident",
						"text": "View Incident",
						"type": "button",
						"url": "https://www.google.com"
					}
				]
			}
		]

		slack = SlackClient(slack_token)
		slack.api_call(
		'chat.postMessage',
		channel=alert_channel,
		attachments=message_attachment,
  		username=alert_username)

	'''
	@app.route('/slack', methods=['POST'])
	def receive_alert(self):
		if request.form.get('token') == slack_webhook:
		username = request.form.get('user_name')
		alert = request.form.get('text')
		received_message = 'Alert: {}, submitted by {}'.format(alert, username)
	'''

if __name__ == '__main__':
	if sys.platform.startswith('win'):
		win32api.SetConsoleCtrlHandler(ctrlHandler, True)
		win32serviceutil.HandleCommandLine(PyalertsService)

	pyalerts = PyAlerts()
	cpu_threshold = config['config']['percent_threshold']['cpu_threshold']
	ram_threshold = config['config']['percent_threshold']['ram_threshold']
	disk_threshold = config['config']['percent_threshold']['disk_threshold']

	system = System()
	cpuusage = system.cpu_usage()
	ramusage = system.ram_usage()
	diskusage = system.disk_space()

	# Alert if cpu, ram or disk usage is above the specified threshold in
	# config file
	while True:
		if cpuusage >= cpu_threshold:
			pyalerts.send_alert(channel=alert_channel,
								username=alert_username,
								alert_message="CPU usage: {}% "
											  "which is above the maximum "
											  "threshold of {}%".format(cpuusage, cpu_threshold))
		if ramusage >= ram_threshold:
			pyalerts.send_alert(channel=alert_channel,
								username=alert_username,
								alert_message="RAM usage: {}% "
											  "which is above the maximum "
											  "threshold of {}%".format(ramusage, ram_threshold))
		if diskusage >= disk_threshold:
			pyalerts.send_alert(channel=alert_channel,
								username=alert_username,
								alert_message="Disk usage: {}% "
											  "which is above the maximum "
											  "threshold of {}%".format(diskusage, disk_threshold))
		time.sleep(timeout)