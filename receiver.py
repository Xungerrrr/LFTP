#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import threading
import os

from socket import *
from packet import Packet

class Receiver:

    def __init__(self, receiveSocket, clientAddress, fileName, filePath):
        self.receiveSocket = receiveSocket
        self.clientAddress = clientAddress
        self.fileName = fileName
        self.filePath = filePath
        self.expectedSeqNum = 1
        self.rwnd = 80
        self.receiveBuffer = {}

    def receive(self):
        print('start receiving data')
        if os.path.exists(self.filePath + self.fileName):
            os.remove(self.filePath + self.fileName)
        with open(self.filePath + self.fileName, 'ab') as file:
            while 1:
                data, clientAddress = self.receiveSocket.recvfrom(2048)
                packet = Packet.decode(data)
                if packet.FIN:  # 传输完毕
                    print('Write successfully to %s.' % self.fileName)
                    self.receiveSocket.close()
                    break
                elif packet.seqNum == self.expectedSeqNum: # 收到期望的数据包
                    file.write(packet.data)
                    self.expectedSeqNum += 1
                    while self.expectedSeqNum in self.receiveBuffer: # 将之前收到的乱序数据包写入文件
                        file.write(self.receiveBuffer[self.expectedSeqNum])
                        self.expectedSeqNum += 1
                        # 流控制
                        if self.rwnd < 80:
                            self.rwnd += 1
                    ack = Packet.encode(Packet(0, self.expectedSeqNum, 1, 0, 0, 0, self.rwnd))
                    self.receiveSocket.sendto(ack, clientAddress)
                    #print("Sending ACK = %s" % self.expectedSeqNum)
                elif packet.seqNum > self.expectedSeqNum: # 收到乱序数据包
                    # 流控制
                    if self.rwnd > 0:
                        self.rwnd -= 1
                    #print('receive packet %s' % packet.seqNum)
                    self.receiveBuffer[packet.seqNum] = packet.data
                    ack = Packet.encode(Packet(0, self.expectedSeqNum, 1, 0, 0, 0, self.rwnd))
                    self.receiveSocket.sendto(ack, clientAddress)
                    #print("Sending ACK = %s" % self.expectedSeqNum)
                else:
                    #print('receive packet %s' % packet.seqNum)
                    ack = Packet.encode(Packet(0, self.expectedSeqNum, 1, 0, 0, 0, self.rwnd))
                    self.receiveSocket.sendto(ack, clientAddress)
                    #print("Sending ACK = %s" % self.expectedSeqNum)