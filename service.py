# service.py
import threading
import win32serviceutil
import win32service
import win32event
import ipwatchman


class MyService(win32serviceutil.ServiceFramework):
    _svc_name_ = "IpwatchmanService"
    _svc_display_name_ = "IP Watchman Service"
    
    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.threads=[]
       

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        ipwatchman.stop_event.set()
        [thread.join() for thread in self.threads]
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        ip_addresses = ipwatchman.read_ips_from_file()  
        packet_size = 2
        timeout = 10
        timepar = 0
       
     
        for ip_address in ip_addresses:
          thread = threading.Thread(target=ipwatchman.Ipwatchman, args=(ip_address, packet_size, timeout, timepar))
          self.threads.append(thread)
          thread.start()

    
if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(MyService)
