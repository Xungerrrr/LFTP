#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import threading
import os

from socket import *
from packet import Packet

class Sender:

    SS = 0
    CA = 1

    def __init__(self, sendSocket, clientAddress, fileName, filePath):
        self.sendSocket = sendSocket
        self.clientAddress = clientAddress
        self.fileName = fileName
        self.filePath = filePath
        self.sendBase = 1
        self.nextSeqNum = 1
        self.swnd = 1
        self.cwnd = 1
        self.rwnd = 80
        self.sendBuffer = []
        self.congestionState = Sender.SS
        self.ssthresh = 60
        self.currentAck = 0
        self.aheadLimit = 30
        

    def send(self):
        with open(self.filePath + self.fileName, 'rb') as file:
            print('Sending file %s...' % self.fileName)
            while 1:
                if self.nextSeqNum >= self.sendBase + self.swnd or self.nextSeqNum >= self.currentAck + self.aheadLimit: # 超出发送窗口
                    #print('Sending window is full')
                    continue
                else:
                    data = file.read(1010)
                    if not data: # 传输完毕
                        if len(self.sendBuffer) == 0: # 若所有数据包都收到ACK，则退出线程
                            self.close()
                            break
                    else:
                        packet = Packet.encode(Packet(self.nextSeqNum, 0, 0, 0, 0, 0, 0, data))
                        self.sendBuffer.append(packet)
                        if len(self.sendBuffer) == 1:
                            threading.Thread(target=self.receiveAck).start() # 启动接收ACK的线程
                        self.sendSocket.sendto(packet, self.clientAddress)
                        self.nextSeqNum += 1
            print('Send %s to %s successfully!' % (self.fileName, self.clientAddress))
            self.sendSocket.close()

    def receiveAck(self):
        duplicateNum = 0
        while 1:
            try:
                self.sendSocket.settimeout(5)
                if len(self.sendBuffer) == 0: # 所有发送的数据包已收到ACK
                    self.sendSocket.settimeout(None)
                    break
                data, clientAddr = self.sendSocket.recvfrom(2048)
                self.sendSocket.settimeout(None)
                packet = Packet.decode(data)
                if packet.ACK: # 如果是ACK
                    self.currentAck = packet.ackNum
                    self.rwnd = packet.rwnd # 流控制
                    if packet.ackNum == self.sendBase:
                        duplicateNum += 1
                        if duplicateNum == 3: # 收到3次重复的ACK
                            # 阻塞控制，快速恢复，进入阻塞避免
                            if self.ssthresh >= 2:
                                self.ssthresh = self.cwnd / 2
                            else:
                                self.ssthresh = 1
                            self.cwnd = self.ssthresh
                            self.congestionState = Sender.CA
                            self.swnd = min(self.rwnd, self.cwnd)
                            duplicateNum = 0
                            print("Duplicate Acks!")
                            self.retransmit() # 重传

                    elif packet.ackNum > self.sendBase:
                        for x in range(0, packet.ackNum - self.sendBase):
                            self.sendBuffer.pop(0)  # 从缓冲区移除已收到ACK的数据包
                        self.sendBase = packet.ackNum
                        duplicateNum = 0
                        # 阻塞控制
                        if self.congestionState == Sender.SS:
                            self.cwnd += 1
                            self.swnd = min(self.rwnd, self.cwnd)
                            if (self.cwnd > self.ssthresh):
                                self.congestionState = Sender.CA
                        elif self.congestionState == Sender.CA:
                            self.cwnd += (1 / self.cwnd)
                            self.swnd = min(self.rwnd, self.cwnd)
                    if len(self.sendBuffer) == 0: # 所有发送的数据包已收到ACK
                        self.sendSocket.settimeout(None)
                        break
            except timeout: # 超时
                # 阻塞控制，进入慢启动
                if self.ssthresh >= 2:
                    self.ssthresh = self.cwnd / 2
                else:
                    self.ssthresh = 1
                self.cwnd = 1
                self.congestionState = Sender.SS
                self.swnd = min(self.rwnd, self.cwnd)
                print("Timeout!")
                self.retransmit() # 重传
                
    def retransmit(self):
        packet = self.sendBuffer[0]
        print("Retransmitting packet %s" % Packet.decode(packet).seqNum)
        self.sendSocket.sendto(packet, self.clientAddress)   

    def close(self):
        fin = Packet.encode(Packet(self.nextSeqNum, 0, 0, 0, 1, 0, self.rwnd))
        self.sendSocket.sendto(fin, self.clientAddress)
