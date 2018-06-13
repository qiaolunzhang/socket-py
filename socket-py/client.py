# -*- coding: utf-8 -*-
import socket
import select
import struct
import sys
from datetime import datetime
import random
import math
import time


def encode_points(x, y, R):
    x = str(x)
    y = str(y)
    R = str(R)
    message = x + '|' + y + '|' + R
    return message


def get_packet_request(content_name, content, packet_type):
    # 请求名长度
    message = struct.pack('>I', len(content_name))
    # 请求名
    message = message + content_name + content
    # 长度+类型+message
    message = struct.pack('>I', len(message)) + struct.pack('>I', packet_type) + message
    return message


class Client:
    MAX_WAITING_CONNECTIONS = 100
    RECV_BUFFER = 4096
    RECV_msg_content = 4
    RECV_MSG_TYPE_LEN = 4


    def __init__(self, config_path):
        self.time_start = time.time()
        self.time_end = time.time()
        # store the data
        self.data_dic = {}

        self.host = ""
        self.port = 10000
        self.connections = [] # collects all the incoming connections
        self.load_config(config_path)
        print("Loading config complete")
        self._run()


    def load_config(self, config_path):
        try:
            with open(config_path) as f:
                for line in f:
                    if line[0] != '#':
                        line = line.split()
                        if line[0] == 'router_ip':
                            self.host = line[1]
                            self.port = int(line[2])
        except Exception, e:
            print(Exception, ", ", e)
            raise SystemExit


    def _bind_socket(self):
        """
        Create the sever socket and bind it to the given host and port
        :return:
        """
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.connect((self.host, self.port))
        self.connections.append(self.server_socket)
        self.connections.append(sys.stdin)


    def _receive(self, sock):
        """
        first get length
        then get type
        process
        :return:
        """
        data = None
        # Retrieves the first 4 bytes form message
        tot_len = 0
        msg_content = 0
        typ_content = 0

        # msg_content: 序列化后的数据包的总长度
        while tot_len < self.RECV_msg_content:
            msg_content = sock.recv(self.RECV_msg_content)
            tot_len += len(msg_content)
        tot_len = 0

        # typ_content: 序列化后的数据包的类型
        while tot_len < self.RECV_MSG_TYPE_LEN:
            typ_content = sock.recv(self.RECV_MSG_TYPE_LEN)
            tot_len += len(typ_content)

        if typ_content:
            try:
                packet_type = struct.unpack('>I', typ_content)[0]
                print("The package type is ", packet_type)
            except Exception, e:
                print(Exception, ", ", e)
                print("Failed to unpack the package type")
                return

        # 如果包里头没有内容，那就并不做处理
        if msg_content:
            data = ''
            try:
                # Unpacks the message and gets the message length
                msg_content_unpack = struct.unpack('>I', msg_content)[0]
                tot_data_len = 0
                while tot_data_len < msg_content_unpack:
                    # Retrieves the chunk i-th chunk of RECV_BUFFER size
                    chunk = sock.recv(self.RECV_BUFFER)
                    # If there isn't the expected chunk...
                    if not chunk:
                        data = None
                        break # ... Simply breaks the loop
                    else:
                        # Merges the chunks content
                        data += chunk
                        tot_data_len += len(chunk)
                # 原始的整个数据包
                data_origin = msg_content + typ_content + data
                # sock.send(data)
                print("The received data is ", data, 'the length is', len(data))
                self._process_packet(sock, packet_type, data_origin, data)
            except Exception, e:
                print(Exception, ", ", e)
                print("Failed to unpack the packet length")


    def _process_packet_interest(self, sock, content_name, content):
        pass


    def _process_packet_aid_reply(self, sock, content_name, content):
        pass

    def _process_packet_aid_query(self, sock, content_name, content):
        pass


    def _process_packet_data(self, sock, content_name, content):
        print("Succeed to get back data packet")
        try:
            print("Get the data: ")
            # 解码成utf-8才能正常显示
            print(content.decode('utf-8'))
        except Exception, e:
            print(Exception, ", ", e)


    def _process_packet(self, sock, typ_content, data_origin, data):
        print("Now process the packet: ", typ_content)

        content_name_len = data[0:4]
        content_name_len = struct.unpack('>I', content_name_len)[0]
        content_name = data[4:4+content_name_len]
        if (4+content_name_len) >= len(data):
            content = ""
        else:
            content = data[4+content_name_len:]

        print "The content name is: ",
        print content_name.decode('utf-8')
        print "The content is: ",
        print content.decode('utf-8')

        if typ_content == 1:
            self._process_packet_interest(sock, content_name, content)
        elif typ_content == 2:
            self.time_end = time.time()
            self._process_packet_data(sock, content_name, content)
        elif typ_content == 3:
            self._process_packet_aid_query(sock, content_name, content)
        elif typ_content == 4:
            self._process_packet_aid_reply(sock, content_name, content)

        print(self.time_end - self.time_start)
        print("*******************************************************************************")


    def _run(self):
        self._bind_socket()
        while True:
            """
            Actually runs the server.
            """
            # Gets the list of sockets which are ready to be read through select non-blocking calls
            # The select has a timeout of 60 seconds
            try:
                ready_to_read, ready_to_write, in_error = select.select(self.connections, [], [], 60)
            except socket.error:
                continue
            else:
                for sock in ready_to_read:
                    if sock == self.server_socket:
                        try:
                            self._receive(sock)
                        except Exception, e:
                            print(Exception, ", ", e)
                        # ... else is an incoming server socket connection
                    else:
                        # 如果是用户输入
                        message = sys.stdin.readline()
                        message = message[:-1]
                        message = message.split()
                        x = int(message[0])
                        y = int(message[1])
                        r = int(message[2])
                        # 保存真实发送的数据
                        print("x is ", x, " y is ", y, "r is ", r)
                        message = encode_points(x, y, r)
                        packet = get_packet_request(message, "", 1)
                        self.time_start = time.time()
                        self.server_socket.send(packet)

                        # 记录发送包
                        print("Content name is: ")
                        sys.stdout.write(message)
                        sys.stdout.write('\n')
                        sys.stdout.flush()


p = Client("./config/client.conf")
