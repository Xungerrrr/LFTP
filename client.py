#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import threading
from socket import *
from packet import Packet
from sender import Sender
from receiver import Receiver

serverPort = 12000
rwnd = 10

print("**********************************************")
print("Welcome to the LFTP client application")
print("Usage:\n\tSend file: LFTP lsend <myserver> <mylargefile>\n\tGet file: LFTP lget <myserver> <mylargefile>")
print("Enter exit() to exit.")
print("**********************************************")


def connect():
    global rwnd, dataAddress
    try:
        sendBase = 0
        cwnd = 1
        syn = Packet.encode(Packet(0, 0, 0, 1, 0, action, rwnd, fileName.encode('utf-8')))
        clientSocket.sendto(syn, serverAddress)
        clientSocket.settimeout(5)

        data, serverAddrress = clientSocket.recvfrom(2048)
        packet = Packet.decode(data)
        if packet.ACK and packet.SYN and packet.ackNum == 1:
            rwnd = packet.rwnd
            port = packet.data
            if port == '-1':
                print('No port available.')
                return False
            else:
                dataAddress = (serverName, int(port))
                print("Connection established!")
                return True
        else:
            print("Server not respond. Reconnecting...")
            connect()
    except timeout:
        print("Server not respond. Reconnecting...")
        connect()

while True:
    # 用户输入命令
    userInput = input()
    userInput = userInput.split()

    if len(userInput) == 1 and userInput[0] == 'exit()':
        exit()
    if len(userInput) != 4:
        print("Usage:\n\tSend file: LFTP lsend <myserver> <mylargefile>\n\tGet file: LFTP lget <myserver> <mylargefile>")
        print("Enter exit() to exit.")
        continue
    if userInput[0] != 'LFTP':
        print("Usage:\n\tSend file: LFTP lsend <myserver> <mylargefile>\n\tGet file: LFTP lget <myserver> <mylargefile>")
        continue
    if userInput[1] == 'lsend':
        action = 0
    elif userInput[1] == 'lget':
        action = 1
    else:
        print("Usage:\n\tSend file: LFTP lsend <myserver> <mylargefile>\n\tGet file: LFTP lget <myserver> <mylargefile>")
        continue

    serverName = userInput[2]
    fileName = userInput[3]
    serverAddress = (serverName, serverPort)
    dataAddress = (serverName, serverPort)
    clientSocket = socket(AF_INET, SOCK_DGRAM)

    
    if action == 0:     # 发送文件
        print("Connecting to server...")
        if not connect():
            continue
        else:
            sender = Sender(clientSocket, dataAddress, fileName, 'client/')
            threading.Thread(target=sender.send()).start()
    
    elif action == 1:   # 下载文件
        print("Connecting to server...")
        if not connect():
            continue
        else:
            receiver = Receiver(clientSocket, dataAddress, fileName, 'client/')
            threading.Thread(target=receiver.receive()).start()