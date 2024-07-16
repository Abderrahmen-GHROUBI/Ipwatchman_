import threading
import win32serviceutil
import win32service
import win32event
import ipwatchman



class MyService(win32serviceutil.ServiceFramework):
    _svc_name_ = "IpwatchmanService1"
    _svc_display_name_ = "IP Watchman Service1"
    
    
    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.threads = []
        self.service_running = True  
        

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self.service_running = False 
        ipwatchman.stop_event.set()  
        for thread in self.threads:
            thread.join()  
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

        while self.service_running:
            win32event.WaitForSingleObject(self.hWaitStop, 1000)  

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(MyService)
