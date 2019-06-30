from state import FileTransferState
from client import Client
from server import Server

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

