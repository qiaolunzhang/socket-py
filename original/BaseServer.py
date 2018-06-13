# -*- coding: utf-8 -*-
import select
import socket
import struct
import os
from datetime import datetime

import utils


class BaseServer:
    MAX_WAITING_CONNECTIONS = 100
    RECV_BUFFER = 4096
    RECV_msg_content = 4
    RECV_MSG_TYPE_LEN = 4

    def __init__(self, config_file):
        # 用于保存文件名
        self.host = ''
        self.port = 20000
        self.connections = [] # collects all the incoming connections
        self.out_conn_dic = {} # collects all the outcoming connections
        self.ip_to_sock_dic = {}
        self.sock_to_ip_dic = {}
        self.load_config(config_file)
        print("loading config complete.")
        self._run()


    def load_config(self, config_file):
        try:
            with open(config_file) as f:
                for line in f:
                    if line[0] != '#':
                        line = line.split()
                        if line[0] == 'local_ip':
                            self.host = line[1]
                            self.port = int(line[2])
                            continue
                        if line[0] == 'aid_ip':
                            self.aid_host = line[1]
                            self.aid_port = int(line[2])
                            continue
                        if line[0] == 'server_ip':
                            self.server_host = line[1]
                            self.server_port = int(line[2])
                            continue
                        if line[0] == 'client_ip':
                            self.client_host = line[1]
                            continue
        except Exception, e:
            print(Exception, ", ", e)
            print("Failed to load the config file")
            raise SystemExit


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
        send packet to aid
        """
        if self.aid_host in self.out_conn_dic.keys():
            self.out_conn_dic[self.aid_host].send(data_origin)
        else:
            sock_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock_client.connect((self.aid_host, self.aid_port))
            self.out_conn_dic[self.aid_host] = sock_client
            self.sock_to_ip_dic[sock_client] = self.aid_host
            self.connections.append(sock_client)

            # @todo data_origin需要修改
            sock_client.send(data_origin)
            print("\n****************************************************\n")


    def _process_packet_aid(self, sock, data_origin, data):
        """
        get the packet from aid
        """
        print("Succeed to get packet from aid")
        aid_packet_type_pack = data[:4]
        try:
            aid_packet_type = struct.unpack('>I', aid_packet_type_pack)[0]
            print("Aid packet type is ", aid_packet_type)
            # 包的数据
            content = data[4:]
            print("Content is ", content_name)
            if aid_packet_type == 1:
                message = struct.pack('>I', len(content)) + struct.pack('>I', 1) + content
                if self.server_host in self.out_conn_dic.keys():
                    self.out_conn_dic[self.server_host].send(message)
                else:
                    sock_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock_client.connect((self.server_host, self.server_port))
                    self.out_conn_dic[self.server_host] = sock_client
                    self.sock_to_ip_dic[sock_client] = self.server_host
                    self.connections.append(sock_client)
                    sock_client.send(message)
            elif aid_packet_type == 2:
                message = struct.pack('>I', len(content)) + struct.pack('>I', 2) + content
                sock_client = self.ip_to_sock_dic[self.client_host]
                sock_client.send(message)

            print("\n****************************************************\n")
        except Exception, e:
            print(Exception, ", ", e)
            print("\n****************************************************\n")


    def _process_packet_data(self, sock, data_origin, data):
        """
        get the data from the server, send it to aid
        """
        if self.aid_host in self.out_conn_dic.keys():
            self.out_conn_dic[self.aid_host].send(data_origin)
        else:
            sock_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock_client.connect((self.aid_host, self.aid_port))
            self.out_conn_dic[self.aid_host] = sock_client
            self.sock_to_ip_dic[sock_client] = self.aid_host
            self.connections.append(sock_client)

            sock_client.send(data_origin)
            print("\n****************************************************\n")


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
            self._process_packet_data(sock, content_name, content)
        elif typ_content == 3:
            self._process_packet_aid_query(sock, content_name, content)
        elif typ_content == 4:
            self._process_packet_aid_reply(sock, content_name, content)

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


r = BaseServer("./config/router.conf")
