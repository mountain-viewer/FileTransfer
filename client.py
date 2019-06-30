import socket
import threading
import time
import os

from utils import *

class Client:

    def __init__(self, ip, file, threads):
        print("Client is running.")

        self.host = ip
        self.path = file

        self.filename = self.path.split("/")[-1]

        self.n_threads = threads

        self.basic_port = BASIC_PORT
        self.file_port = FILE_PORT


    def send_basic_info(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        sock.connect((self.host, self.basic_port))

        basic_info = self.filename + MSG_SEPARATOR + str(self.n_threads)
        sock.send(basic_info.encode())
        
        print("Basic info sent")
        
        sock.close()


    def send_file_chunks(self):
        threads = [None] * self.n_threads

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