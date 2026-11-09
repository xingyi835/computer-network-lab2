
import sys
from socket import *
serverName = sys.argv[1] if len(sys.argv) > 1 else '192.168.159.16'
serverPort = int(sys.argv[2]) if len(sys.argv) > 2 else 5201
payloadFile = sys.argv[3] if len(sys.argv) > 3 else None

clientSocket = socket(AF_INET, SOCK_DGRAM)
clientSocket.settimeout(3.0)

if payloadFile:
    with open(payloadFile, 'rb') as f:
        message = f.read()
    print(f'[从文件读取] {payloadFile}：{len(message)} 字节')
else:
    message = input('Input lowercase sentence:').encode()
clientSocket.sendto(message, (serverName, serverPort))
print(f'[已发送] {len(message)} 字节 -> {serverName}:{serverPort}')
try:
    modifiedMessage, serverAddress = clientSocket.recvfrom(65535)
    print(f'[收到] 来自 {serverAddress}：{modifiedMessage[:80]!r}')
except timeout:
    print('[超时]')
except ConnectionRefusedError:
    print('[ICMP]')

clientSocket.close()
