"""
Script to create the Windows Service
"""
import os
import pathlib
import subprocess
import traceback

import env_file
import servicemanager
import win32event
import win32service
import win32serviceutil
from win32api import SetConsoleCtrlHandler

import settings


class AppServerSvc(win32serviceutil.ServiceFramework):
    """
    Service Create class
    """
    _svc_name_ = "KelloggWebApplication"  # service name
    _svc_display_name_ = "KelloggWebApplication"  # display name

    def __init__(self, args):
        """
        Constructor
        """
        win32serviceutil.ServiceFramework.__init__(self, args)
        SetConsoleCtrlHandler(lambda x: True, True)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)

    def SvcStop(self):
        """
        Function to stop the windows service
        """
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.proc.terminate()

    def SvcDoRun(self):
        """
        Function to create and start the windows service
        """
        self.ReportServiceStatus(win32service.SERVICE_START_PENDING)
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ''))
        try:
            self.main()

        except Exception as exp_msg:
            servicemanager.LogErrorMsg(traceback.format_exc())
            os._exit(-1)

    def main(self):
        """
        Script to run as the windows service
        """
        env_file.load(f'{os.path.join(pathlib.Path(__file__).parent.absolute(), "config.env")}')
        settings.set_env_variables()
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)
        self.proc = subprocess.Popen(f"python"
                                     f" {os.path.join(pathlib.Path(__file__).parent.absolute(), 'cherry.py')} 1"
                                     , stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                     stdin=subprocess.DEVNULL)
        stdout, stderr = self.proc.communicate()
        if (self.proc.poll() == 0):
            servicemanager.LogMsg(f"Successfully started the process with PID: {self.proc.pid}")
        else:
            servicemanager.LogErrorMsg(f"Failed to start the services")


if __name__ == '__main__':
    # Start of the process
    win32serviceutil.HandleCommandLine(AppServerSvc)
