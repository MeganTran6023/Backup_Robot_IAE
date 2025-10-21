# server_laptop.py (with print statements)
import socket

HOST = '0.0.0.0'
PORT = 5001

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print(f"Server: Listening on {HOST}:{PORT}")
    conn, addr = s.accept()
    with conn:
        print(f"Server: Connected by {addr}")
        while True:
            data = conn.recv(1024)
            if not data:
                print("Server: Connection closed")
                break
            print('Server: Sonar Data:', data.decode())
