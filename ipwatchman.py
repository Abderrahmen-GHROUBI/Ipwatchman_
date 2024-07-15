# ipwatchman.py
import subprocess
import time
from datetime import datetime
import threading
import ipaddress
from Database import add_ip_event
from logger import logger


db_lock = threading.Lock()
stop_event = threading.Event()

def ping_ip(ip, packet_size, timeout=1000):
    try:
        ipaddress.ip_address(ip)

        def perform_ping():
            return subprocess.Popen(['ping', '-n', '1', '-l', str(packet_size), '-w', str(timeout), ip],
                                    stdout=subprocess.PIPE).communicate()[0].decode('utf-8')

        output_decoded = perform_ping()

        if f'Reply from {ip}' in output_decoded:
            return True
        else:
            for _ in range(2):
                if "Destination host unreachable" in output_decoded:
                    return False
                elif "Request timed out" in output_decoded:
                    output_decoded = perform_ping()
                    if f'Reply from {ip}' in output_decoded:
                        return True

        return False
    except ValueError:
        print(f"Invalid IP address: {ip}")
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

def Ipwatchman(ip_address, packet_size=2, timeout=1, timepar=0):
    while True:  
        result = ping_ip(ip_address, packet_size, timeout)
        print(f"Ping result for {ip_address}: {result}")

        if not result:
            time.sleep(timepar)
            if not ping_ip(ip_address, packet_size, timeout):
                fail_time = datetime.now()
                print(f"Failed to ping {ip_address}. Sending notification...")
                logger.info(f"Failed to ping {ip_address}. Sending notification...")

                with db_lock:
                    add_ip_event(ip_address=ip_address, event_type="Failure",
                                 date_=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

                while not ping_ip(ip_address, packet_size, timeout):
                    if stop_event.is_set(): 
                        break
                    print(f"Ping failed: {ip_address}. Waiting to recover...")
                    
                    
                if stop_event.is_set():  
                        break
                recovery_time = int((datetime.now() - fail_time).total_seconds())
                print(f"{ip_address} is reachable after {recovery_time} seconds.")
                logger.info(f"{ip_address} is reachable after {recovery_time} seconds.")
                with db_lock:
                    add_ip_event(ip_address=ip_address, event_type="Recovery",
                                 date_=datetime.now().strftime("%Y-%m-%d %H:%M:%S"), recovery_time=recovery_time)

def read_ips_from_file(file_path='ips.txt'):
    
    with open(file_path, 'r') as file:
         ips = [line.strip() for line in file]
    return ips
    

if __name__ == "__main__":
    ip_addresses = read_ips_from_file('ips.txt')
    packet_size = 2
    timeout = 10
    timepar=0
    #timepar=60
    
    threads = []
    for ip_address in ip_addresses:
          thread = threading.Thread(target=Ipwatchman, args=(ip_address, packet_size, timeout, timepar))
          threads.append(thread)
          thread.start()
          
    time.sleep(2)
    stop_event.set()
    [thread.join() for thread in threads]
  

    
    