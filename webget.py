import socket
import sys


BUFFER_SIZE = 4096


def parse_content_length(headers_text):
    #从响应头中读取 Content-Length
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
        print("Usage: python webget.py <ip address> <port>")
        print("Example: python webget.py 192.168.1.1 80")
        return 1
    host = sys.argv[1]
    path = sys.argv[2]
    port_text = sys.argv[3] if len(sys.argv) == 4 else "80"
    try:
        port = int(port_text)
        if not 1 <= port <= 65535:
            raise ValueError
    except ValueError:
        return 1
    if not path.startswith("/"):
        path = "/" + path

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
        with socket.create_connection((host, port), timeout=10) as sock:
            sock.settimeout(10)
            sock.sendall(request)

            #接收响应头读空行
            header_end = -1
            while header_end < 0:
                chunk = sock.recv(BUFFER_SIZE)
                recv_count += 1
                recv_sizes.append(len(chunk))
                print(f"recv #{recv_count}: {len(chunk)} 字节")

                if not chunk:
                    print("提前关闭")
                    return 1

                response.extend(chunk)
                header_end = response.find(b"\r\n\r\n")

            header_bytes = bytes(response[:header_end])
            body = bytearray(response[header_end + 4:])
            headers_text = header_bytes.decode("iso-8859-1")
            status_line = headers_text.split("\r\n", 1)[0]
            status_parts = status_line.split()
            status_code = status_parts[1] if len(status_parts) >= 2 else "未知"
            content_length = parse_content_length(headers_text)

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

                    if not chunk:
                        print(
                            "提前关闭"
                            f"body 收到 {len(body)} 字节，"
                            f"Content-Length 为 {content_length}。"
                        )
                        break

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

    except socket.timeout:
        print(f"超时")
        return 1

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