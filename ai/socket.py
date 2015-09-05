import socket


class Socket:
    def __init__(self, host: str, port: int):
        """
        서버에 연결할 소켓을 초기화합니다.

        :param host: 연결한 호스트
        :param port: 연결할 포트
        """
        self.queue = b''
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port

    def connect(self):
        """
        게임 서버에 연결을 시도합니다.
        """
        self.socket.connect((self.host, self.port))

    def receive(self, num_bytes: int=1) -> bytes:
        """
        num_bytes 만큼을 서버에서 읽습니다.

        :param num_bytes: 서버에서 받아오고자 하는 바이트 수입니다.
        :return: 전송 받은 bytes 객체
        :raise RuntimeError:
        """
        while len(self.queue) < num_bytes:
            received = self.socket.recv(2048)
            if received == b'':
                raise RuntimeError("Socket Connection is Closed")
            self.queue += received
        data = self.queue[:num_bytes]
        self.queue = self.queue[num_bytes:]
        return data

    def send(self, *args):
        """
        서버에 데이터를 전송합니다.

        :param args: 전송할 데이터
        :raise RuntimeError:
        """
        data = b''
        for byte in args:
            data += byte

        sent = self.socket.send(data)
        if sent == b'':
            raise RuntimeError("Socket Connection is Closed")