import threading
import time
import socket

is_connected = False

def internet(host="8.8.8.8", port=53, timeout=3):
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except socket.error:
        return False

def monitor_connection():
    global is_connected
    while True:
        is_connected = internet()
        time.sleep(5)

thread = threading.Thread(target=monitor_connection)
thread.daemon = True
thread.start()

while True:
    if is_connected:
        print("You are connected to the internet.")
    else:
        print("You are not connected to the internet.")
    time.sleep(5)