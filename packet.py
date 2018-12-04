#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import struct
class Packet:

    format = '!II????H'

    def __init__(self, seqNum, ackNum, ACK, SYN, FIN, action, rwnd, data=b''):
        self.seqNum = seqNum
        self.ackNum = ackNum
        self.ACK = ACK
        self.SYN = SYN
        self.FIN = FIN
        self.action = action
        self.rwnd = rwnd
        self.data = data

    def encode(self):
        header = struct.pack(Packet.format, self.seqNum, self.ackNum, self.ACK, self.SYN, self.FIN, self.action, self.rwnd)
        return header + self.data;

    @classmethod
    def decode(cls, binaryData):
        seqNum, ackNum, ACK, SYN, FIN, action, rwnd = struct.unpack(Packet.format, binaryData[:14])
        return cls(seqNum, ackNum, ACK, SYN, FIN, action, rwnd, binaryData[14:])