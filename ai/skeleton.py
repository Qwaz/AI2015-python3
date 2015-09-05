from ai import env
from .socket import Socket


def padding(msg: str, num_bytes: int) -> bytes:
    """
    문자열 메시지를 UTF-8 인코딩 후 `num_bytes`에 맞게 조정합니다,

    :param msg: 인코딩할 메시지
    :param num_bytes: 바이트 수
    :return: 인코딩 된 bytes 객체
    """
    data = msg.encode('utf-8')[:num_bytes]
    if len(data) < num_bytes:
        data += b'\x00' * (num_bytes-len(data))
    return data


def print_map(map, slime1, slime2) -> None:
    """
    맵 정보를 출력합니다.

    :param map: 맵 데이터를 담고 있는 이차원 배열
    :param slime1: 1팀의 슬라임 데이터를 담고 있는 이차원 배열
    :param slime2: 2팀의 슬라임 데이터를 담고 있는 이차원 배열
    """
    print_data = []
    for row in map:
        print_row = []
        for num in row:
            if num is 255:
                print_row.append('_')
            elif num is 0:
                print_row.append('1')
            elif num is 1:
                print_row.append('2')
        print_data.append(print_row)

    for i in range(5):
        print_data[slime1[i][0]][slime1[i][1]] = 'O'
        print_data[slime2[i][0]][slime2[i][1]] = 'X'

    for y in reversed(range(env.map_height)):
        for x in range(env.map_width):
            print(print_data[x][y], end='')
        print()
    print()


class Skeleton:
    def __init__(self):
        """
        AI를 초기화합니다.
        """
        self.socket = Socket(host=env.host, port=env.port)

        self.team = -1
        self.turn = -1

        self.ai_name = '파이썬 스켈레톤'
        self.wait_message = ''
        self.start_message = ''

    def connect(self):
        """
        게임 서버에 접속을 시도합니다.
        """
        self.socket.connect()
        self.socket.send(bytes([env.team]), padding(self.ai_name, 23))  # 게임 서버에 접속을 시도합니다.
        if not env.fix_team:
            self.get_team_info()

        if self.wait_message != '':
            # 대기 메시지 출력
            self.change_message(self.wait_message)

        while True:
            map_data, slime1_data, slime2_data = self.parse()
            if env.fix_team and self.turn == 0:
                self.get_team_info()

            if self.turn == 0 and self.start_message != '':
                # 게임 시작 메시지 출력
                self.change_message(self.start_message)

            print('팀 %d - 턴 %d 진행중' % (self.team+1, self.turn))
            print_map(map_data, slime1_data, slime2_data)

            self.think(map_data, slime1_data, slime2_data)

    def parse(self):
        self.turn = int.from_bytes(self.socket.receive(2), byteorder=env.endian)  # 턴 정보 읽기
        map_data = self.parse_map(self.socket.receive(env.map_width * env.map_height))  # 맵 정보 저장
        slime1_data = self.parse_slime(self.socket.receive(10))  # 팀 1 슬라임 위치 저장
        slime2_data = self.parse_slime(self.socket.receive(10))  # 팀 2 슬라임 위치 저장
        return map_data, slime1_data, slime2_data

    def get_team_info(self):
        self.team = 0 if self.socket.receive(1) == b'\x00' else 1
        print('%d팀을 배정받았습니다' % (self.team + 1))

    def change_message(self, msg: str):
        """
        게임 메시지를 변경합니다.

        :param msg: 변경할 메시지. ~40bytes
        """
        self.socket.send(bytes([255]), padding(msg, 40))

    def change_direction(self, directions):
        """
        슬라임들의 방향을 변경합니다.

        :param directions: 슬라임들의 방향을 담고 있는 배열. →↑←↓ 순서로 0123에 대응된다. ex) [0, 1, 2, 1, 1]
        """
        data = self.turn.to_bytes(2, byteorder=env.endian)
        for i in range(5):
            data += directions[i].to_bytes(1, byteorder=env.endian)
        self.socket.send(data)
        print('방향 변경 %s\n\n' % ''.join(map((lambda x: '→↑←↓'[x]), directions)))

    def think(self, map_data, slime1_data, slime2_data):
        """
        매 턴마다 호출되는 함수. 오버라이드해서 사용하자.

        :param map_data: 맵 데이터
        :param slime1_data: 1팀 슬라임 데이터
        :param slime2_data: 2팀 슬라임 데이터
        :raise NotImplementedError:
        """
        raise NotImplementedError('Override this method')

    def parse_map(self, data: bytes):
        """
        비트 데이터에서 맵 정보를 파싱합니다.

        :param data: 맵 데이터를 담고 있는 bytes 객체 (325bytes)
        :return: 이차원 맵 배열 (255: 중립, 0: 1팀, 1: 2팀)
        """
        map_data = []
        index = 0

        # 맵 정보 읽어서 저장
        for x in range(env.map_width):
            column = []
            for y in range(env.map_height):
                column.append(data[index])
                index += 1
            map_data.append(column)

        return map_data

    def parse_slime(self, data: bytes):
        """
        비트 데이터에서 슬라임 정보를 파싱합니다.

        :param data: 슬라임 데이터를 담고 있는 bytes 객체 (10bytes)
        :return: 이차원 슬라임 배열 [[x ,y], [x, y], ...]
        """
        slime_data = []
        index = 0

        # 슬라임 위치 읽어서 저장
        for i in range(5):
            slime_data.append([data[index], data[index+1]])
            index += 2

        return slime_data


def mirror(coordinate):
    return [env.map_width-1 - coordinate[0], env.map_height-1 - coordinate[1]]


class Doppelganger(Skeleton):
    order = [2, 1, 0, 4, 3]
    mirror_dir = [2, 3, 0, 1]

    def __init__(self):
        Skeleton.__init__(self)
        self.ai_name = '파이썬 도플갱어'

    def parse(self):
        map_data, slime1_data, slime2_data = Skeleton.parse(self)

        if self.team == 0:
            return map_data, slime1_data, slime2_data
        else:
            map_parsed = [[255 for i in range(env.map_height)] for i in range(env.map_width)]
            slime1_parsed = [mirror(slime2_data[Doppelganger.order[i]]) for i in range(5)]
            slime2_parsed = [mirror(slime1_data[Doppelganger.order[i]]) for i in range(5)]
            for x in range(env.map_width):
                for y in range(env.map_height):
                    map_parsed[x][y] = map_data[env.map_width-1 - x][env.map_height-1 - y]
            return map_parsed, slime1_parsed, slime2_parsed

    def change_direction(self, directions):
        data = self.turn.to_bytes(2, byteorder=env.endian)
        if self.team == 0:
            for i in range(5):
                data += directions[i].to_bytes(1, byteorder=env.endian)
        else:
            for i in range(5):
                data += Doppelganger.mirror_dir[directions[Doppelganger.order[i]]].to_bytes(1, byteorder=env.endian)
        self.socket.send(data)
        print('방향 변경 %s\n\n' % ''.join(map((lambda x: '→↑←↓'[x]), directions)))
