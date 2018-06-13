"""
This module provides utility functions that are used within socket-py
"""

def get_packet_request(content_name):
    message = struct.pack('>I', 1) + struct.pack(len(content_name))
    message = message + content_name
    message = struct.pack('>I', len(message)) + message


def get_packet_reply(content_name, content):
    pass

def get_packet_request_aid(content_name):
    pass

def get_packet_reply_aid(content_name, content):
    pass

"""
header format:
"""
def send_with_header(data):
    pass

"""
get packet type:
"""
def get_packet_type(packet):
    pass
