from ai import env
from ai.skeleton import Doppelganger
from random import randrange

def distance(a, b):
    return abs(a[0]-b[0]) + abs(a[1]-b[1])


class Binggeul(Doppelganger):
    def __init__(self):
        Doppelganger.__init__(self)

        self.ai_name = '빙글빙글'
        self.start_message = '돌고 도는 세상'

        self.rotate = [0, 0, 0, 0, 0]
        self.dir = [0, 0, 0, 0, 0]
        self.prev = [[-1, -1] for i in range(5)]

    def think(self, map_data, slime1_data, slime2_data):
        for i in range(5):
            if distance(self.prev[i], slime1_data[i]) > 1:
                # 부딪혀서 죽은 경우
                self.rotate[i] = randrange(0, 2)
                self.dir[i] = self.rotate[i]

            if self.rotate[i] == 0:
                # 반시계방향
                if self.dir[i] == 0 and slime1_data[i][0] == env.map_width-1:
                    self.dir[i] = 1
                if self.dir[i] == 1 and slime1_data[i][1] == env.map_height-1:
                    self.dir[i] = 2
                if self.dir[i] == 2 and slime1_data[i][0] == 0:
                    self.dir[i] = 3
                if self.dir[i] == 3 and slime1_data[i][1] == 0:
                    self.dir[i] = 0
            else:
                # 시계방향
                if self.dir[i] == 0 and slime1_data[i][0] == env.map_width-1:
                    self.dir[i] = 3
                if self.dir[i] == 1 and slime1_data[i][1] == env.map_height-1:
                    self.dir[i] = 0
                if self.dir[i] == 2 and slime1_data[i][0] == 0:
                    self.dir[i] = 1
                if self.dir[i] == 3 and slime1_data[i][1] == 0:
                    self.dir[i] = 2

        self.change_direction(self.dir)
        self.prev = slime1_data

env.initialize()
Binggeul().connect()
