#!/bin/sh
# consumer
ifconfig enp0s25:0 192.168.80.134
# router, visualize 
ifconfig enp0s25:1 192.168.80.135
# firewall
ifconfig enp0s25:2 192.168.80.136
# publisher
ifconfig enp0s25:3 192.168.80.137
