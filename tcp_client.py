import socket

def start_client(host='127.0.0.1', port=65432):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((host, port))
        
        message = "от клиента серверу tcp".encode()
        client_socket.sendall(message)
        
        data = client_socket.recv(1024)
        print(f"Ответ от сервера: {data.decode()}")

if __name__ == "__main__":
    start_client()
