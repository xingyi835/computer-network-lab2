#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""UDP 服务器（教材 UDPServer.py）—— 运行在 Debian 虚拟机
改动：端口 12000 -> 5201；多打印一行，把 client 发来的内容显示出来（A1 验收要求）。
运行：python3 udp_server.py
"""
from socket import *

serverPort = 5201                                   # A1 要求：教材的 12000 改成 5201
serverSocket = socket(AF_INET, SOCK_DGRAM)          # SOCK_DGRAM = UDP；没有 listen、没有 accept
serverSocket.bind(('', serverPort))
print('The server is ready to receive', flush=True)

while True:
    message, clientAddress = serverSocket.recvfrom(65535)   # 一次取一个完整数据报，顺带拿到对端地址
    print(f'[收到] 来自 {clientAddress} 的 {len(message)} 字节：{message[:80]!r}', flush=True)

    modifiedMessage = message.decode(errors='replace').upper()
    serverSocket.sendto(modifiedMessage.encode(), clientAddress)
