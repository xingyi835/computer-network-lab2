# GitHub public repository: https://github.com/xingyi835/computer-network-lab2
import socket
import sys
#缓冲区
BUFFER_SIZE = 4096
#这里选择建立一个函数,来截取Content-Length
def parse_content_length(headers_text):
    #从响应头中读取 Content-Length字段并返回数字
    for line in headers_text.split("\r\n")[1:]:
        name, separator, value = line.partition(":")
        if separator and name.strip().lower() == "content-length":
            try:
                return int(value.strip())
            except ValueError:
                return None
    return None


def main():
    if len(sys.argv) not in (3, 4):
        #把命令行参数提取出来并进行分析
        print("Usage: python webget.py host path [port]")
        print("Example: python webget.py www.bjfu.edu.cn /")
        print("Example: python webget.py www.bjfu.edu.cn / 80")
        return 1
    #读取并设置
    host = sys.argv[1]
    path = sys.argv[2]
    port_text = sys.argv[3] if len(sys.argv) == 4 else "80"
    try:
        port = int(port_text)
        if not 1 <= port <= 65535:
            raise ValueError
    except ValueError:
        #错误处理
        print(f"Invalid port: {port_text!r}. Port must be an integer from 1 to 65535.")
        print("Usage: python webget.py host path [port]")
        return 1
    if not path.startswith("/"):
        path = "/" + path
#请求行获取
    request = (
        f"GET {path} HTTP/1.1\r\n"
        f"Host: {host}\r\n"
        "Connection: close\r\n"
        "\r\n"
    ).encode("ascii")
    response = bytearray()
    recv_count = 0
    recv_sizes = []

    try:
        #建立连接
        with socket.create_connection((host, port), timeout=10) as sock:
            #设置超时
            sock.settimeout(10)
            sock.sendall(request)

            #接收响应头读空行
            header_end = -1
            while header_end < 0:
                chunk = sock.recv(BUFFER_SIZE)
                recv_count += 1
                recv_sizes.append(len(chunk))
                print(f"recv #{recv_count}: {len(chunk)} 字节")
            #在没达到之前提前退出,返回
                if not chunk:
                    print("提前关闭")
                    return 1
            #加入
                response.extend(chunk)
                #通过\r\n\r\n寻找末尾
                header_end = response.find(b"\r\n\r\n")
            #找到头了,后面就是body
            header_bytes = bytes(response[:header_end])
            #把最初的4个字节去掉
            body = bytearray(response[header_end + 4:])
            headers_text = header_bytes.decode("iso-8859-1")
            #以\r\n做寻找符号
            status_line = headers_text.split("\r\n", 1)[0]
            #分部
            status_parts = status_line.split()
            status_code = status_parts[1] if len(status_parts) >= 2 else "未知"
            content_length = parse_content_length(headers_text)
            #这里是关于content_length与body长度的对比
            if content_length is not None:
                if content_length < 0:
                    print(f"错误: Content-Length 为负数 ({content_length})。")
                    return 1
                body = body[:content_length]
                while len(body) < content_length:
                    chunk = sock.recv(BUFFER_SIZE)
                    recv_count += 1
                    recv_sizes.append(len(chunk))
                    print(f"recv #{recv_count}: {len(chunk)} 字节")
                #同上,提前关闭
                    if not chunk:
                        print(
                            "错误：服务器提前关闭，"
                            f"body 收到 {len(body)} 字节，"
                            f"Content-Length 为 {content_length}。未保存不完整响应。"
                        )
                        return 1
                #更新body
                    remaining = content_length - len(body)
                    body.extend(chunk[:remaining])
            else:
                # 无Content-Length
                while True:
                    chunk = sock.recv(BUFFER_SIZE)
                    recv_count += 1
                    recv_sizes.append(len(chunk))
                    print(f"recv #{recv_count}: {len(chunk)} 字节")

                    if not chunk:
                        break

                    body.extend(chunk)
    #超时判断
    except socket.timeout:
        print(f"超时")
        return 1
    #文本打印
    print("\n状态行和响应头:")
    print(headers_text.replace("\r\n", "\n"))
    print(f"HTTP状态码: {status_code}")
    actual_body_length = len(body)
    if content_length is None:
        print("Content-Length:None")
    else:
        print(f"Content-Length: {content_length} 字节")
        print(f"body 实际长度: {actual_body_length} 字节")
#   t2
    output_file = "response.bin"
    try:
        with open(output_file, "wb") as file:
            file.write(body)
    except OSError as exc:
        print(f"保存响应 body 失败: {exc}")
        return 1

    print(f"\nbody共{len(body)}字节")
    print(f"recv次数 {recv_count}")
    print(f"recv字节数: {recv_sizes}")
    print(f"recv总数: {sum(recv_sizes)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())