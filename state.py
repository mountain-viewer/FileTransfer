import argparse

class FileTransferState:

    def __init__(self):
        self.parser = argparse.ArgumentParser()

        self.parser.add_argument('-send', action='store_true')
        self.parser.add_argument('-receive', action='store_true')

        self.parser.add_argument('-ip', type=str)
        self.parser.add_argument('-file', type=str)
        self.parser.add_argument('-threads', type=int)
        
        self.args = self.parser.parse_args()