from ai import env
from ai.skeleton import Doppelganger
from random import randrange


class FiveGap(Doppelganger):
    def __init__(self):
        Doppelganger.__init__(self)

        self.ai_name = '5 Gap'
        self.start_message = '냠냠'

        self.prev_dir = [-1 for i in range(5)]
        self.dir = [-1 for i in range(5)]

    def think(self, map_data, slime1_data, slime2_data):
        for i in range(5):
            if slime1_data[i][0]%6 == 0 and slime1_data[i][1]%6 == 0 or self.turn == 0: # 격자점이거나 첫 턴일 때
                while True:
                    self.prev_dir[i] = self.dir[i]
                    self.dir[i] = randrange(0, 4)
                    if not (
                        self.turn == 0 and (i == 3 or i == 4) and self.dir[i]%2 == 0 or # 첫 턴에 3, 4번 슬라임은 세로로 이동
                        self.dir == 0 and slime1_data[i][0] == env.map_width-1 or
                        self.dir == 1 and slime1_data[i][1] == env.map_width-1 or
                        self.dir == 2 and slime1_data[i][0] == 0 or
                        self.dir == 3 and slime1_data[i][1] == 0 or
                        self.dir[i] == (self.prev_dir[i]+2)%4 # 왔던 방향으로 다시 돌아가지 못 하게 함
                    ):
                        break
        self.change_direction(self.dir)

env.initialize()
FiveGap().connect()
