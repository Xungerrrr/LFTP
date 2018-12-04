#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import threading
import os

from socket import *
from packet import Packet
from sender import Sender
from receiver import Receiver

serverPort = 12000
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('127.0.0.1', serverPort))

dataPort = [12001, 12002, 12003, 12004, 12005, 12006, 12007, 12008, 12009, 12010]
dataPortIsAvailable = [True, True, True, True, True, True, True, True, True, True]
threadPool = [None, None, None, None, None, None, None, None, None, None]

print("Bind UDP on %d. The server is ready to receive." % serverPort)

def findAvailablePort():
    for x in range(0,10):
        if threadPool[x] != None and not threadPool[x].is_alive():
            threadPool[x] = None
            dataPortIsAvailable[x] = True
    for x in range(0,10):
        if threadPool[x] == None:
            dataPortIsAvailable[x] = False
            return x
    return -1

while 1:
    data, clientAddress = serverSocket.recvfrom(2048)
    print('File transfer requested from %s:%s' % clientAddress)
    packet = Packet.decode(data)
    if packet.SYN:
        fileName = packet.data.decode('utf-8')
        action = packet.action
        x = findAvailablePort()
        if x == -1:
            print('No port available.')
            port = -1
            ack = Packet.encode(Packet(0, packet.seqNum+1, 1, 1, 0, action, 60, str(port).encode('utf-8')))
            serverSocket.sendto(ack, clientAddress)
            continue
        else:
            port = dataPort[x]
            ack = Packet.encode(Packet(0, packet.seqNum+1, 1, 1, 0, action, 60, str(port).encode('utf-8')))
            serverSocket.sendto(ack, clientAddress)
            dataSocket = socket(AF_INET, SOCK_DGRAM)
            dataSocket.bind(('127.0.0.1', port))
        if action:
            print('Start sending file %s to %s at port %s...' % (fileName, clientAddress, port))
            sender = Sender(dataSocket, clientAddress, fileName, 'server/')
            send = threading.Thread(target=sender.send)
            threadPool[x] = send
            send.start()
        else:
            print('Start receiving file %s from %s at port %s...' % (fileName, clientAddress, port))
            receiver = Receiver(dataSocket, clientAddress, fileName, 'server/')
            receive = threading.Thread(target=receiver.receive)
            threadPool[x] = receive
            receive.start()
    else:
        continue