# 计算机网络期中项目
# LFTP应用
---
| 学号 | 姓名 |
| :-: | :-: |
| 16340109 | 黎汛言 |

## 项目简介
本项目实现了一个简单的LFTP（Large File Transfer Protocal）应用，来支持网络中两台计算机之间进行大文件传输

A network application to support large file transfer between two computers in the Internet.

## 应用特性
* 编程环境
	Python 3.7

* 网络架构
	CS（client-server）网络架构

* 功能
	* 上传
		客户端可以通过如下命令从服务端下载文件：

		```
		LFTP lget <servername> <filename>
		```

	* 下载
		客户端可以通过如下命令向服务端上传文件：

		```
		LFTP lsend <servername> <filename>
		```

	* 多用户
		服务端支持最多10个用户同时上传或下载文件

* 网络传输特性
	* 使用UDP作为传输层协议
	* 100%可靠数据传输
	* 提供流控制
	* 提供拥塞控制

## 启动方法（Windows）
运行该应用前，需要安装Python 3.x版本，并配置好Python的系统环境变量。

启动服务端：

```
python server.py
```

启动客户端：

```
python client.py
```

## 应用设计

### 自定义数据包的设计

```py
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
```

### 发送端


## 应用测试
* 单个客户端上传

* 单个客户端下载

* 多个客户端同时上传

* 多个客户端同时下载

* 多个客户端同时上传或下载

* 可靠传输

* 流控制

* 拥塞控制
