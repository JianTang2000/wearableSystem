"""
UDP communication test
"""

import UdpComms as U
import time

sock = U.UdpComms(udpIP="127.0.0.1", portTX=8000, portRX=8001, enableRX=True, suppressWarnings=True)

i = 0

while True:
    sock.SendData('Sent from Python: ' + str(i))  # Send this string to other application
    i += 1

    data = sock.ReadReceivedData()  # read data

    if data != None:  # if NEW data has been received since last ReadReceivedData function call
        print(data)  # print new received data
    time.sleep(1)
