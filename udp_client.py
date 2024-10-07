import socket

def start_udp_client(host='127.0.0.1', port=65432):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client_socket:
        message = "от клиента серверу udp".encode()
        client_socket.sendto(message, (host, port))
        
        data, server = client_socket.recvfrom(1024)
        print(f"Ответ от сервера: {data.decode()}")

if __name__ == "__main__":
    start_udp_client()
