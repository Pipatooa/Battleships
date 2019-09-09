import socket
import pickle
import math


class HostNetwork:
    """Host network object handing sending and receiving of data from the host to the client"""

    def __init__(self):
        # Create sockets
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Constants
        self.BUFFER_SIZE = 16
        self.HEADER_SIZE = 10

        # Get local ip
        ip = socket.gethostname()
        ip = socket.gethostbyname(ip)

        # Connection information
        self.ip = ip
        self.port = 55555

    def connect(self):
        """Binds the host to ip and port"""

        self.socket.bind((self.ip, self.port))
        self.socket.listen(5)

    def disconnect(self):
        """Closes all connections"""

        self.socket.close()

    def accept(self):
        """Get new connection made to the host by client

        :returns: socket, address"""

        return self.socket.accept()

    def recv(self, socket):
        """Receive and decode data from 'socket'

        Returns data received"""

        # Fetch fixed length header
        header = socket.recv(self.HEADER_SIZE)
        datalen = int(header)

        # Buffer data sent by the client in chunks and join it together
        chunks = [socket.recv(self.BUFFER_SIZE) for i in range(math.floor(datalen / self.BUFFER_SIZE))]
        if datalen % self.BUFFER_SIZE: chunks += [socket.recv(datalen % self.BUFFER_SIZE)]

        data = b"".join(chunks)

        # Decode data and return it
        return pickle.loads(data)

    def send(self, socket, data):
        """Encodes and sends data to 'socket'"""

        # Encode data and create fixed length header
        data = pickle.dumps(data)
        header = bytes("{:<{}}".format(len(data), self.HEADER_SIZE), "utf-8")

        # Send data to client
        socket.send(header + data)
