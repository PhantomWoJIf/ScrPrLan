import socket

def start_udp_server(host='127.0.0.1', port=65432):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_socket:
        server_socket.bind((host, port))
        print(f"Cервер запущен. Ожидание сообщений...")

        data, addr = server_socket.recvfrom(1024)
        print(f"Получено сообщение от {addr}: {data.decode()}")
        server_socket.sendto(data, addr)

if __name__ == "__main__":
    start_udp_server()
