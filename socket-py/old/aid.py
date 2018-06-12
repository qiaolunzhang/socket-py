# -*- coding: utf-8 -*-
import select
import socket
import struct
import os
from datetime import datetime

import utils


class Router:
    MAX_WAITING_CONNECTIONS = 100
    RECV_BUFFER = 4096
    RECV_msg_content = 4
    RECV_MSG_TYPE_LEN = 4

    def __init__(self):
        # 用于保存文件名
        self.file_number = 1
        # store the fib form
        self.fib_dic = {}
        # store the pit form
        self.pit_dic = {}
        # store the cs form
        self.cs_dic = {}

        self.host = ''
        self.port = 20000
        self.aid_host = ''
        self.aid_port = 11111
        self.connections = [] # collects all the incoming connections
        self.out_conn_dic = {} # collects all the outcoming connections
        self.ip_to_sock_dic = {}
        self.sock_to_ip_dic = {}
        self.load_config()
        print("loading config complete.")
        self._run()


    def load_config(self):
        try:
            with open('./config/aid.conf') as f:
                for line in f:
                    if line[0] != '#':
                        line = line.split()
                        if line[0] == 'local_ip':
                            self.host = line[1]
                            self.port = int(line[2])
                            continue
        except Exception, e:
            print(Exception, ", ", e)
            print("Failed to load the config file")
            raise SystemExit

        try:
            if not os._exists('./cache/'):
                os.mkdir('./cache')
        except:
            return


    def _bind_socket(self):
        """
        Create the sever socket and bind it to the given host and port
        :return:
        """
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        print("Now binding the socket, host is ", self.host, " port is ", self.port)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(self.MAX_WAITING_CONNECTIONS)
        self.connections.append(self.server_socket)


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


    def _process_packet_interest(self, sock, data_origin, data):
        """
        发送改变后的消息，判断缓存中是否有，翻译的时候加一个不同的字段
        """
        if data in self.cs_dic.keys():
            try:
                message = self.cs_dic[data]
                message = struct.pack('>I', 2) + message
                message = struct.pack('>I', len(message)) + struct.pack('>I', 3) + message
                sock.send(message)
            except Exception, e:
                print(Exception, ", ", e)
                return
        else:
            try:
                message = "from aid"
                message = struct.pack('>I', 1) + message
                message = struct.pack('>I', len(message)) + struct.pack('>I', 3) + message
                sock_client.send(data_origin)
        print("\n****************************************************\n")


    def _process_packet_data(self, sock, data_origin, data):
        """
        get the data from the router, send query result back to router
        """
        print("Succeed to get data packet")
        content_name_len = struct.unpack('>I', content_name_len_pack)[0]
        print("Content name length is ", content_name_len)
        content_name = data[4: 4 + content_name_len]
        print("Content name is ", content_name)

        content = data[4 + content_name_len:]
        self.cs_dic[content_name] = content

        message = data + "get the data"
        message = struct.pack('>I', 2) + message
        message = struct.pack('>I', len(message)) + struct.pack('>I', 3) + message
        sock.send(data_origin)


    def _process_packet(self, sock, typ_content, data_origin, data):
        print("\n")
        print("Now process the packet type: ", typ_content)
        print("\n")

        if typ_content == 1:
            self._process_packet_interest(sock, data_origin, data)
        elif typ_content == 2:
            self._process_packet_data(sock, data_origin, data)


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
                        if sock == self.server_socket:
                            try:
                                # Handles a new client connection
                                client_socket, client_address = self.server_socket.accept()
                                self.ip_to_sock_dic[client_address[0]] = client_socket
                                self.sock_to_ip_dic[client_socket] = client_address[0]
                            except socket.error:
                                break
                            else:
                                self.connections.append(client_socket)
                                print "Client (%s, %s) connected" % client_address
                        # ... else is an incoming client socket connection
                    else:
                        try:
                            #next_route_ip, data = self._receive(sock)
                            self._receive(sock)
                        except socket.error:
                            #print("Client is offline" % client_address)
                            sock.close()
                            self.connections.remove(sock)
                            continue


r = Router()
