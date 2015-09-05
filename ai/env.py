import argparse

endian = 'big'

map_width = 25
map_height = 13

host = 'localhost'
port = 25252

team = 0
'''
원하는 팀 번호. 1팀일 경우 0, 2팀일 경우 1

주의! 원하는 팀 번호와 배정 받은 팀 번호가 다를 수 있으며,
배정 받은 팀 번호는 AI 클래스 내에서 `self.team`으로 접근합니다.
'''

fix_team = False

def initialize():
    global host, port, team, fix_team

    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--team', choices=['1', '2'], default='1',
                        help='팀을 선택합니다.')
    parser.add_argument('--host', default=host,
                        help='연결할 호스트를 설정합니다')
    parser.add_argument('--port', type=int, default=port,
                        help='연결할 포트를 설정합니다')
    parser.add_argument('--fix_team', action='store_true',
                        help='1.1 버전에서 두 번째로 연결하는 팀이 사용합니다')

    args = parser.parse_args()

    host = args.host
    port = args.port
    team = int(args.team) - 1
    fix_team = args.fix_team