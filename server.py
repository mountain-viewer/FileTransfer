import socket
import threading

from utils import *

class Server:

    def __init__(self):
        print("Server is running.")
        
        self.host = socket.gethostbyname(socket.gethostname())
        self.basic_port = BASIC_PORT
        self.file_port = FILE_PORT

        print("Host:", self.host)
        print("Basic info port:", self.basic_port)
        print("File port:", self.file_port)


    def receive_basic_info(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        sock.bind((self.host, self.basic_port))
        sock.listen()
        (conn, address) = sock.accept()

        print("Received basic info from:", address)
    
        raw_data = conn.recv(1024)
        basic_info = raw_data.decode()  

        basic_info_split = basic_info.split(MSG_SEPARATOR)

        self.filename = basic_info_split[0]
        self.n_threads = int(basic_info_split[1])

        print("Waiting for file:", self.filename)
        print("Transfer is processing in", self.n_threads, "threads")

        sock.close()


    def receive_file_chunks(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        sock.bind((self.host, self.file_port))
        sock.listen(self.n_threads)

        threads = []
        self.chunks = [None] * self.n_threads
        
        for thread_id in range(self.n_threads):
            conn, address = sock.accept()
    
            thread = threading.Thread(target=self._load_chunks, args=(conn,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        print("Received all chunks")

        sock.close()


    def save_file(self):
        print("Saving the file")

        with open(self.filename, "wb") as f:
            for order in range(self.n_threads):
                f.write(self.chunks[order])

        print("Saving done")


    def _load_chunks(self, conn):
        raw_data = b''

        order_data = conn.recv(1024)
        order = int(order_data.decode())

        while True:
            data = conn.recv(1024)

            if not data:
                break
                
            raw_data += data

        self.chunks[order] = raw_data