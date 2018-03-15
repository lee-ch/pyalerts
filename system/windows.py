import win32serviceutil
import win32service
import win32api
import win32event
import servicemanager
import socket
import time
import string
import sys
import os
import logging
import tempfile
import subprocess

from subprocess import PIPE
from subprocess import Popen
from subprocess import STDOUT



tmpdir = tempfile.gettempdir()
tmpfile = os.path.join(tmpdir, 'pyalerts-service.log')
logging.basicConfig(
    filename = tmpfile,
    level = logging.DEBUG, 
    format = '[pyalerts-service] %(levelname)-7.7s %(message)s'
)

cwd = os.getcwd()
parentdir = os.path.abspath(os.path.join(cwd, os.pardir))
progfile = os.path.join(parentdir, 'alerts.py')


class PyalertsService(win32serviceutil.ServiceFramework):
    _svc_name_ = 'PyAlerts Service'
    _svc_display_name_ = 'PyAlerts Service'
    _svc_description_ = 'PyAlerts for system alerts through slack'
    
    def __init__(self,args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
    	servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE, servicemanager.PYS_SERVICE_STARTED, (self._svc_name_, ''))
    	self.timeout = 120000
    	while True:
    		rc = win32event.WaitForSingleObject(self.hWaitStop, self.timeout)
    		if rc == win32event.WAIT_OBJECT_0:
    			servicemanager.LogInfoMsg('{} - Stopped'.format(_svc_name_))
    			break
    		else:
    			try:
    				p = Popen(['python', progfile],
    						   stdout=PIPE,
    						   stderr=STDOUT,
    						   cwd=cwd)
    				out = p.communicate()[0]
    				if (not p.returncode) and out:
    					servicemanager.LogInfoMsg('{} executed successfully'.format(progfile))
    			except:
    				pass



def ctrlHandler(ctrlType):
	return True