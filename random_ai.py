from ai import env
from ai.skeleton import Skeleton
from random import randrange


class RandomAI(Skeleton):
    def __init__(self):
        Skeleton.__init__(self)

        self.ai_name = '랜덤 인공지능'

        # < 메시지 설정하기 >
        # self.wait_message = '다른 플레이어를 기다리는동안 표시할 메시지'
        # self.start_message = '게임이 시작되면 표시할 메시지'
        #  self.win_message = '승리했을 때 표시할 메시지'
        # self.lose_message = '패배했을 때 표시할 메시지'
        # self.change_message('All your base belong to us')로 언제든지 변경 가능합니다.

    def think(self, map_data, slime1_data, slime2_data):
        # < AI를 짤 때 유용한 정보 >
        # self.team: 1팀이라면 0, 2팀이라면 1
        # self.turn: 현재 턴 수
        # map_data[y][x]: (x. y) 좌표의 맵 정보
        # slime1_data[i]: 1번팀 슬라임의 [x, y] 좌표

        self.change_direction([randrange(0, 4) for i in range(5)])

env.initialize()
RandomAI().connect()
