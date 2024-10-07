import socket

def start_server(host='127.0.0.1', port=65432):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((host, port))
        
        server_socket.listen()
        print(f"Сервер запущен. Ожидание подключения...")

        conn, addr = server_socket.accept()
        with conn:
            print(f"Подключен клиент: {addr}")
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                print(f"Получено сообщение: {data.decode()}")
                conn.sendall(data)

if __name__ == "__main__":
    start_server()
