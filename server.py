#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import threading
from socket import *
from packet import Packet
from sender import Sender
from receiver import Receiver

serverName = '127.0.0.1'
serverPort = 12000
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind((serverName, serverPort))

print("**********************************************")
print("Welcome to the LFTP server application")
print("**********************************************")

dataPort = [12001, 12002, 12003, 12004, 12005, 12006, 12007, 12008, 12009, 12010]   # 数据端口号
dataPortIsAvailable = [True, True, True, True, True, True, True, True, True, True]  # 端口占用情况
threadPool = [None, None, None, None, None, None, None, None, None, None]           # 端口对应的线程

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
    data, clientAddress = serverSocket.recvfrom(2048)  # 接收连接请求
    print('File transfer requested from %s:%s' % clientAddress)
    packet = Packet.decode(data)
    if packet.SYN:
        fileName = packet.data.decode('utf-8')
        action = packet.action
        x = findAvailablePort()
        if x == -1: # 没有空闲端口
            print('No port available.')
            port = -1
            ack = Packet.encode(Packet(0, packet.seqNum+1, 1, 1, 0, action, 60, str(port).encode('utf-8')))
            serverSocket.sendto(ack, clientAddress) # 反馈端口信息
            continue
        else:
            port = dataPort[x]
            ack = Packet.encode(Packet(0, packet.seqNum+1, 1, 1, 0, action, 60, str(port).encode('utf-8')))
            serverSocket.sendto(ack, clientAddress) # 反馈端口信息
            dataSocket = socket(AF_INET, SOCK_DGRAM)
            dataSocket.bind((serverName, port)) # 绑定空闲的端口到Socket
        if action:  # 发送文件（客户端下载）
            print('Start sending file %s to %s at port %s...' % (fileName, clientAddress, port))
            sender = Sender(dataSocket, clientAddress, fileName, 'server/')
            send = threading.Thread(target=sender.send) # 新建线程进行传输
            threadPool[x] = send
            send.start()
        else:       # 接收文件（客户端上传）
            print('Start receiving file %s from %s at port %s...' % (fileName, clientAddress, port))
            receiver = Receiver(dataSocket, clientAddress, fileName, 'server/')
            receive = threading.Thread(target=receiver.receive) # 新建线程进行传输
            threadPool[x] = receive
            receive.start()
    else:
        continue