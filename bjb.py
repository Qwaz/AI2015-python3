from ai import env
from ai.skeleton import Doppelganger
from random import randrange, random, choice

def distance(a, b):
    return abs(a[0]-b[0]) + abs(a[1]-b[1])

def on_wall(coordinate):
    return coordinate[0] == 0 or coordinate[0] == env.map_width-1 or coordinate[1] == 0 or coordinate[1] == env.map_height-1

def nearest_wall(coordinate, exception=-1):
    candidates = []
    score = 100

    def update(new_candidate, new_score):
        if new_candidate == exception:
            return
        nonlocal candidates, score
        if new_score == score:
            candidates.append(new_candidate)
        elif new_score < score:
            candidates = [new_candidate]
            score = new_score

    update(2, coordinate[0])
    update(3, coordinate[1])
    update(0, env.map_width-1 - coordinate[0])
    update(1, env.map_height-1 - coordinate[1])

    return choice(candidates)


class BJ(Doppelganger):
    def __init__(self):
        Doppelganger.__init__(self)

        self.ai_name = 'BVM'
        self.start_message = '빙그레 바닐라맛 우유'

        self.rotate = [0, 0, 0, 0, 0]
        self.dir = [0, 0, 0, 0, 0]
        self.prev_dir = [0, 0, 0, 0, 0]
        self.dir_count = [0, 0, 0, 0, 0]
        self.prev = [[0, 12], [0, 6], [0, 0], [6, 3], [6, 9]]

    def think(self, map_data, slime1_data, slime2_data):
        for i in range(5):
            # 초반 수동 패턴
            if self.turn == 0:
                self.rotate = [0, 0, 0, 0, 0]
                self.dir = [3, 3, 0, 0, 1]
            if self.turn == 7:
                self.dir[2] = 1
            if self.turn == 8:
                self.rotate[3] = 0
                self.dir[3] = 3
                self.rotate[4] = 1
                self.dir[4] = 0

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
            elif self.rotate[i] == 1:
                # 시계방향
                if self.dir[i] == 0 and slime1_data[i][0] == env.map_width-1:
                    self.dir[i] = 3
                if self.dir[i] == 1 and slime1_data[i][1] == env.map_height-1:
                    self.dir[i] = 0
                if self.dir[i] == 2 and slime1_data[i][0] == 0:
                    self.dir[i] = 1
                if self.dir[i] == 3 and slime1_data[i][1] == 0:
                    self.dir[i] = 2

        if self.turn >= 20:
            for i in range(5):
                if self.dir[i] == self.prev_dir[i]:
                    self.dir_count[i] += 1
                else:
                    self.dir_count[i] = 0
                if not on_wall(slime1_data[i]) and self.dir_count[i] > 4 and random() < 0.2:
                    self.dir[i] = nearest_wall(slime1_data[i], (self.dir[i]+2)%4)

        if self.turn >= 20 and (self.turn-20)%11 == 0:
            horizontal = []
            vertical = []
            for i in range(5):
                if 3 <= slime1_data[i][1]:
                    if slime1_data[i][0] == 0:
                        horizontal.append((i, 0))
                    if slime1_data[i][0] == env.map_width-1:
                        horizontal.append((i, 2))
                if 4 <= slime1_data[i][0]:
                    if slime1_data[i][1] == 0:
                        vertical.append((i, 1))
                    if slime1_data[i][1] == env.map_height-1:
                        vertical.append((i, 3))

            if len(horizontal) > 0:
                pair = choice(horizontal)
                self.dir[pair[0]] = pair[1]
                self.rotate[pair[0]] = 1-self.rotate[pair[0]]
            if len(vertical) > 0:
                pair = choice(vertical)
                self.dir[pair[0]] = pair[1]
                self.rotate[pair[0]] = 1-self.rotate[pair[0]]

        self.change_direction(self.dir)
        self.prev = slime1_data
        self.prev_dir = self.dir.copy()

env.initialize()
BJ().connect()
