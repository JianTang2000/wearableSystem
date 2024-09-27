"""
UDP communication between Unity and python server
"""


class UdpComms():
    def __init__(self, udpIP, portTX, portRX, enableRX=False, suppressWarnings=True):
        import socket
        self.udpIP = udpIP
        self.udpSendPort = portTX
        self.udpRcvPort = portRX
        self.enableRX = enableRX
        self.suppressWarnings = suppressWarnings  # when true warnings are suppressed
        self.isDataReceived = False
        self.dataRX = None
        self.udpSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # internet protocol, udp (DGRAM) socket
        self.udpSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,
                                1)  # allows the address/port to be reused immediately instead of it being stuck in the TIME_WAIT state waiting for late packets to arrive.
        if enableRX:
            import threading
            self.rxThread = threading.Thread(target=self.ReadUdpThreadFunc, daemon=True)
            self.rxThread.start()

    def __del__(self):
        self.CloseSocket()

    def CloseSocket(self):
        self.udpSock.close()

    def SendData(self, strToSend):
        self.udpSock.sendto(bytes(strToSend, 'utf-8'), (self.udpIP, self.udpSendPort))

    def ReceiveData(self):
        if not self.enableRX:  # if RX is not enabled, raise error
            raise ValueError("Attempting to receive data without enabling this setting. Ensure this is enabled from the constructor")

        data = None
        try:
            data, _ = self.udpSock.recvfrom(1024)
            data = data.decode('utf-8')
        except WindowsError as e:
            if e.winerror == 10054:  # An error occurs if you try to receive before connecting to other application
                if not self.suppressWarnings:
                    print("Are You connected to the other application? Connect to it!")
                else:
                    pass
            else:
                raise ValueError("Unexpected Error. Are you sure that the received data can be converted to a string")

        return data

    def ReadUdpThreadFunc(self):  # Should be called from thread

        self.isDataReceived = False  # Initially nothing received

        while True:
            data = self.ReceiveData()  # Blocks (in thread) until data is returned (OR MAYBE UNTIL SOME TIMEOUT AS WELL)
            self.dataRX = data  # Populate AFTER new data is received
            self.isDataReceived = True
            # When it reaches here, data received is available

    def ReadReceivedData(self):

        data = None

        if self.isDataReceived:  # if data has been received
            self.isDataReceived = False
            data = self.dataRX
            self.dataRX = None  # Empty receive buffer

        return data
