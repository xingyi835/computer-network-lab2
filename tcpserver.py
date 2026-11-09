from socket import *

serverPort = 5202
serverSocket = socket(AF_INET, SOCK_STREAM)     # SOCK_STREAM = TCP，面向连接
serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)    # 教材没有：避免重启时端口被 TIME_WAIT 占住
serverSocket.bind(('', serverPort))
serverSocket.listen(1)
print('The server is ready to receive', flush=True)

while True:
    connectionSocket, addr = serverSocket.accept()      # 三次握手由内核完成，这一行等的是握手后的连接
    print(f'[accept] 对端 {addr} -> 本端 {connectionSocket.getsockname()}', flush=True)

    sentence = connectionSocket.recv(1024).decode(errors='replace')
    if sentence == '':
        print('[对端已关闭] recv 返回空串 b\'\'（收到 FIN）', flush=True)
    print(f'[收到] {len(sentence)} 字节：{sentence!r}', flush=True)

    capitalizedSentence = sentence.upper()
    connectionSocket.send(capitalizedSentence.encode())

    # 教学版：服务器主动关闭，会成为 TIME_WAIT 的一方。
    # S3 想观察 server 停在 CLOSE_WAIT，就把下面这行注释掉。
    connectionSocket.close()
