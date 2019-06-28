import argparse
import socket
import threading
import time
import os

class FileTransferState:

    def __init__(self):
        self.parser = argparse.ArgumentParser()

        self.parser.add_argument('-send', action='store_true')
        self.parser.add_argument('-receive', action='store_true')

        self.parser.add_argument('-ip', type=str)
        self.parser.add_argument('-file', type=str)
        self.parser.add_argument('-threads', type=int)
        
        self.args = self.parser.parse_args()


class Server:

    def __init__(self):
        print("Server is running.")
        
        self.host = socket.gethostbyname(socket.gethostname())
        self.basic_port = 2406
        self.file_port = 1998

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

        basic_info_split = basic_info.split("##########")

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


class Client:

    def __init__(self, ip, file, threads):
        print("Client is running.")

        self.host = ip
        self.path = file

        self.filename = self.path.split("/")[-1]

        self.n_threads = threads

        self.basic_port = 2406
        self.file_port = 1998


    def send_basic_info(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        sock.connect((self.host, self.basic_port))

        basic_info = self.filename + "##########" + str(self.n_threads)
        sock.send(basic_info.encode())
        
        print("Basic info sent")
        
        sock.close()


    def send_file_chunks(self):
        threads = [None] * self.n_threads
        print(threads)

        chunk_size = os.path.getsize(self.path) // self.n_threads + 1

        for thread_id in range(self.n_threads):
            thread = threading.Thread(target=self._send_chunk, args=(self.path, thread_id, chunk_size))
            threads[thread_id] = thread
            thread.start()

        for thread in threads:
            thread.join()

        print("File chunks sent")


    def _send_chunk(self, path, thread_id, chunk_size):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.host, self.file_port))

        sock.send(str(thread_id).encode())

        time.sleep(0.1)

        with open(path, 'rb') as f:
            f.seek(thread_id * chunk_size)

            raw_data = f.read(chunk_size)
            sock.send(raw_data)

        sock.close()

if __name__ == '__main__':
    file_transfer_state = FileTransferState()
    
    if file_transfer_state.args.send:
        client = Client(file_transfer_state.args.ip,
                        file_transfer_state.args.file,
                        file_transfer_state.args.threads)

        client.send_basic_info()
        client.send_file_chunks()

    elif file_transfer_state.args.receive:
        server = Server()

        server.receive_basic_info()
        server.receive_file_chunks()
        server.save_file()

