import math
import socket
import sys
import time
from threading import Thread
import json
from util import UdpComms as U
from scipy.signal import butter, filtfilt
import numpy as np

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
udp_sock = U.UdpComms(udpIP="127.0.0.1", portTX=8000, portRX=8001, enableRX=True, suppressWarnings=True)


def lowpass_filter(data, alpha=0.03):
    b, a = butter(1, alpha)
    return filtfilt(b, a, data, axis=0)


def append_and_trim(data_list, new_data, max_length=50):
    data_list.append(new_data)
    data_list[:] = data_list[-max_length:]


class TCPConnect:
    def __init__(self):
        self.client_sockets = []
        self.Coord = dict()

    def start_tcp_server(self, ip, port):

        server_address = (ip, port)

        sock.bind(server_address)
        print('starting listen on ip %s, port %s' % server_address)
        try:
            sock.listen(1024)
        except socket.error as e:
            print("fail to listen on port %s" % e)
            sys.exit(1)
        while True:
            print("waiting for connection")
            client, addr = sock.accept()
            self.client_sockets.append(client)
            print(self.client_sockets)

            print("having a connection")

            t = Thread(target=self.sock_threading, args=(client, addr))
            t.setDaemon(True)
            t.start()

    def sock_threading(self, client, addr):
        pre_data_x = []
        pre_data_y = []
        windows_x = []
        windows_y = []
        top_10 = 0
        file_name = "UWB-log-" + time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time())) + ".txt"
        uwb_pos_send_gap = 10
        uwb_pos_send_curr = 0
        with open(file_name, "w") as f:
            while True:
                try:
                    msg = client.recv(16384)
                    if len(msg) == 0:
                        f.close()
                        return
                    temp = json.loads(msg)
                    self.Coord = temp['Coord']

                    if top_10 <= 10:
                        top_10 += 1
                        append_and_trim(pre_data_x, float(self.Coord['x']))
                        append_and_trim(pre_data_y, float(self.Coord['y']))
                        continue

                    append_and_trim(pre_data_x, float(self.Coord['x']))
                    append_and_trim(pre_data_y, float(self.Coord['y']))
                    xy_smoothed = lowpass_filter(np.column_stack((pre_data_x, pre_data_y)), alpha=0.02)
                    x_smoothed = xy_smoothed[:, 0][-1]
                    y_smoothed = xy_smoothed[:, 1][-1]

                    unity_x = round(x_smoothed * 0.35 + 5.525 - (-4.5 * 0.35), 6)
                    unity_z = round(y_smoothed * 0.35 - 7.1 - (0 * 0.35), 6)
                    uwb_pos_send_curr += 1
                    if uwb_pos_send_curr % uwb_pos_send_gap == 0:
                        print(f"sending msg :  {'training=' + str(unity_x) + '=' + str(unity_z)}")
                        udp_sock.SendData("training=" + str(unity_x) + "=" + str(unity_z))

                    windows_x.append(x_smoothed)
                    windows_y.append(y_smoothed)
                    if len(windows_x) == 25:

                        dx = np.diff(windows_x)
                        dy = np.diff(windows_y)
                        distances = np.sqrt((dx ** 2) + (dy ** 2)).cumsum()
                        dist_end2start = distances[-1]
                        if dist_end2start > 0.16:
                            udp_sock.SendData("animation=walk")
                        else:
                            udp_sock.SendData("animation=stop")
                        windows_x.clear()
                        windows_y.clear()

                    f.write(self.Coord['x'] + ", " + self.Coord['y'] + ", " + str(time.time()) + "\n")  # 写还是写原始数据
                    print(self.Coord['x'], self.Coord['y'])
                except Exception as e:
                    print(" *** ", e)
                    f.close()
                    client.close()
                    return


if __name__ == "__main__":
    tcpsever = TCPConnect()
    print(tcpsever)
    tcpsever.start_tcp_server(ip='127.0.0.1', port=8342)
