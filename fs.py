from random import choice

from ai import env
from ai.skeleton import Doppelganger

TURN = 5
DEATH_PENALTY = 5


class Slime:
    def __init__(self, x, y, dir):
        self.x = x
        self.y = y
        self.dir = dir

    def copy(self):
        return Slime(self.x, self.y, self.dir)

    def step(self):
        if self.dir == 0:
            self.x += 1
        if self.dir == 1:
            self.y += 1
        if self.dir == 2:
            self.x -= 1
        if self.dir == 3:
            self.y -= 1

    def available_dir(self):
        candidate = []
        if self.x != env.map_width - 1:
            candidate.append(0)
        if self.y != env.map_height - 1:
            candidate.append(1)
        if self.x != 0:
            candidate.append(2)
        if self.y != 0:
            candidate.append(3)
        return candidate


def parse_slime(slime_data, slime_prev):
    slimes = []
    for i in range(5):
        dir = -1
        if slime_prev[i].x + 1 == slime_data[i][0] and slime_prev[i].y == slime_data[i][1]:
            dir = 0
        if slime_prev[i].x == slime_data[i][0] and slime_prev[i].y + 1 == slime_data[i][1]:
            dir = 1
        if slime_prev[i].x - 1 == slime_data[i][0] and slime_prev[i].y == slime_data[i][1]:
            dir = 2
        if slime_prev[i].x == slime_data[i][0] and slime_prev[i].y - 1 == slime_data[i][1]:
            dir = 3

        slimes.append(Slime(
            x=slime_data[i][0],
            y=slime_data[i][1],
            dir=dir
        ))
    return slimes


def map_copy(map):
    return [[cell for cell in column] for column in map]


def valid_coordinate(x, y):
    return 0 <= x < env.map_width and 0 <= y < env.map_height


def fill_map(map):
    result = map_copy(map)

    for color in [0, 1]:
        dominate = [[1 for y in range(env.map_height)] for x in range(env.map_width)]

        def dfs(x, y):
            delta = [[0, 1], [1, 0], [0, -1], [-1, 0]]
            dominate[x][y] = 0
            for i in range(4):
                next_x = x + delta[i][0]
                next_y = y + delta[i][1]
                if valid_coordinate(next_x, next_y) and dominate[next_x][next_y] and map[next_x][next_y] != color:
                    dfs(next_x, next_y)

        for x in range(env.map_width):
            if dominate[x][0] and map[x][0] != color:
                dfs(x, 0)

            if dominate[x][env.map_height - 1] and map[x][env.map_height - 1] != color:
                dfs(x, env.map_height - 1)

        for y in range(env.map_height):
            if dominate[0][y] and map[0][y] != color:
                dfs(0, y)

            if dominate[env.map_width - 1][y] and map[env.map_width - 1][y] != color:
                dfs(env.map_width - 1, y)

        for x in range(env.map_width):
            for y in range(env.map_height):
                if dominate[x][y]:
                    result[x][y] = color

    return result


def foretell(team, enemy, color, map):
    # 슬라임이 점프를 한 경우와 안 한 경우 시나리오를 비교
    team = [slime.copy() for slime in team]
    enemy = [slime.copy() for slime in enemy]
    map = map_copy(map)

    # 부딪히거나 먹혀서 죽은 수만 센다
    death_count = 0

    # 시뮬레이션할 턴 수
    for turn in range(TURN):
        # 슬라임들 이동 및 사망 처리
        dead_team = [False for i in range(5)]
        dead_enemy = [False for i in range(5)]

        for i in range(5):
            if not team[i]: continue
            shadow = team[i].copy()
            shadow.step()

            for j in range(5):
                if not enemy[j]: continue
                now = enemy[j].copy()

                # 엇갈려서 죽은 경우
                if shadow.x == now.x and shadow.y == now.y and shadow.dir == (now.dir + 2) % 4:
                    dead_team[i] = True
                    dead_enemy[j] = True

                now.step()
                # 같은 칸에 도달해서 죽은 경우
                if shadow.x == now.x and shadow.y == now.y:
                    dead_team[i] = True
                    dead_enemy[j] = True

            # 죽거나 화면 밖에 나간 경우
            for i in range(5):
                if team[i]: team[i].step()
                if enemy[i]: enemy[i].step()

                if dead_team[i]:
                    death_count += 1
                if dead_enemy[i]:
                    death_count -= 1

                if (dead_team[i] or
                        (team[i] and not valid_coordinate(team[i].x, team[i].y))):
                    team[i] = None
                if (dead_enemy[i] or
                        (enemy[i] and not valid_coordinate(enemy[i].x, enemy[i].y))):
                    enemy[i] = None

            # 자기 땅 칠하기
            for i in range(5):
                now = team[i]
                if now:
                    map[now.x][now.y] = color

                now = enemy[i]
                if now:
                    map[now.x][now.y] = 1 - color

            # 땅따먹기 시뮬레이션
            map = fill_map(map)

            # 땅이 따먹혀서 죽은 슬라임 제거
            for i in range(5):
                now = team[i]
                if now and map[now.x][now.y] == 1 - color:
                    team[i] = None
                    death_count += 1

            for i in range(5):
                now = enemy[i]
                if now and map[now.x][now.y] == color:
                    enemy[i] = None
                    death_count -= 1

        """
        print("맵 시뮬레이션 %d" % turn)
        for y in reversed(range(env.map_height)):
            for x in range(env.map_width):
                print('_' if map[x][y] == 255 else map[x][y], end='')
            print('')
        print('\n')
        """

    team_count = 0
    enemy_count = 0

    for x in range(env.map_width):
        for y in range(env.map_height):
            if map[x][y] == color:
                team_count += 1
            elif map[x][y] == 1 - color:
                enemy_count += 1

    return team_count - enemy_count - DEATH_PENALTY * death_count


class FinalSpark(Doppelganger):
    def __init__(self):
        Doppelganger.__init__(self)

        self.ai_name = 'Final Spark'
        self.start_message = '↑ ↑ ↓ ↓ ← → ← → B A'
        self.win_message = '너는 이미 죽어있다'
        self.lose_message = '제가 없는 사이 고양이가'

        self.dir = []
        self.prev_team = [
            Slime(x=0, y=12, dir=0),
            Slime(x=0, y=6, dir=0),
            Slime(x=0, y=0, dir=0),
            Slime(x=6, y=3, dir=0),
            Slime(x=6, y=9, dir=0),
        ]
        self.prev_enemy = [
            Slime(x=24, y=12, dir=0),
            Slime(x=24, y=12, dir=0),
            Slime(x=24, y=12, dir=0),
            Slime(x=18, y=12, dir=0),
            Slime(x=18, y=12, dir=0),
        ]

    def think(self, map_data, slime1_data, slime2_data):
        # < AI를 짤 때 유용한 정보 >
        # self.team: 1팀이라면 0, 2팀이라면 1
        # self.turn: 현재 턴 수
        # map_data[y][x]: (x. y) 좌표의 맵 정보
        # slime1_data[i]: 1번팀 슬라임의 [x, y] 좌표
        # 0123 - 우상좌하

        if self.turn == 0:
            self.dir = [0, 1, 1, 3, 0]
        elif self.turn == 3:
            self.dir[3] = 2
            self.dir[4] = 3
        elif self.turn == 5:
            self.dir = [0, 0, 0, 2, 0]
        elif self.turn == 8:
            self.dir[3] = 0
            self.dir[4] = 1
        elif self.turn == 12:
            self.dir[1] = 3
            self.dir[2] = 3
        elif self.turn == 13:
            self.dir[2] = 0
        elif self.turn == 14:
            self.dir[2] = 1
        elif self.turn >= 16:
            # 코딩하기 편하게 이름 붙이기
            team = parse_slime(slime1_data, self.prev_team)
            enemy = parse_slime(slime2_data, self.prev_enemy)

            # 갈 수 없는 방향은 제외
            for i in range(5):
                if not team[i].dir in team[i].available_dir():
                    team[i].dir = choice(team[i].available_dir())

            best = team
            best_score = foretell(team, enemy, color=self.team, map=map_data)

            for i in range(5):
                for next_dir in team[i].available_dir():
                    if next_dir == team[i].dir:
                        continue
                    tmp = [team[i].copy() for i in range(5)]
                    tmp[i].dir = next_dir
                    score = foretell(tmp, enemy, color=self.team, map=map_data)
                    if score > best_score:
                        team = tmp
                        best = team
                        best_score = score

            # 실제 전송할 방향 설정
            self.dir = [best[i].dir for i in range(5)]

        self.prev_team = parse_slime(slime1_data, self.prev_team)
        self.prev_enemy = parse_slime(slime2_data, self.prev_enemy)
        self.change_direction(self.dir)


env.initialize()
FinalSpark().connect()
