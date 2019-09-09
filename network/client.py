import socket
import pickle
import math


class ClientNetwork:
    """Client network object handing sending and receiving of data from the client to the host"""

    def __init__(self, host_ip):
        # Create socket
        self.hostsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Constants
        self.BUFFER_SIZE = 16
        self.HEADER_SIZE = 10

        # Save host information
        self.host_ip = host_ip
        self.port = 55555

    def connect(self):
        """Connect to the host"""

        self.hostsocket.connect((self.host_ip, self.port))

    def disconnect(self):
        """Disconnect from the host"""

        self.hostsocket.close()

    def recv(self, socket):
        """Receive and decode data from the host

        Returns data received"""

        # Fetch fixed length header
        header = socket.recv(self.HEADER_SIZE)
        datalen = int(header)

        # Buffer data sent by the host in chunks and join it together
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