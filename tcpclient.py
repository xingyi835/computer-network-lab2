import sys
from socket import *
serverName = sys.argv[1] if len(sys.argv) > 1 else '192.168.159.16'
serverPort = int(sys.argv[2]) if len(sys.argv) > 2 else 5202

clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.settimeout(5.0)
try:
    clientSocket.connect((serverName, serverPort))
except ConnectionRefusedError:
    print(f'[拒绝] {serverName}:{serverPort}')
    clientSocket.close()
    sys.exit(1)
except timeout:
    print(f'[超时]')
    clientSocket.close()
    sys.exit(1)

print(f'[已连接] {serverName}:{serverPort}，本端端口 {clientSocket.getsockname()[1]}')

sentence = input('Input lowercase sentence:')
clientSocket.sendall(sentence.encode())
print(f'[已发送] {len(sentence.encode())} 字节')

modifiedSentence = clientSocket.recv(1024)
print('From Server:', modifiedSentence.decode(errors='replace'))
try:
    input('正常 close?')
except EOFError:
    pass

clientSocket.close()
