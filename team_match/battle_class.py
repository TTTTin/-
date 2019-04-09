
from team_match.battle_judge import gobang_judge
import random
from queue import PriorityQueue
# from team_match.public_resource import  random_opcode
from django.core.cache import cache

from abc import abstractmethod

TIME_TO_LIVE = 60 * 60 # second


class battle:
    def __init__(self, opCode, id1, id2):
        self.opCode = opCode
        self.production_id_1, self.production_id_2 = id1, id2
        self.map_channel_name_to_role = {}
        self.detail = []

    def add_channel(self, channel_name, role):
        self.map_channel_name_to_role[channel_name] = role
        cache.set(self.opCode, self, TIME_TO_LIVE)

    def remove_channel(self, channel_name):
        if channel_name in self.map_channel_name_to_role:
            self.map_channel_name_to_role.pop(channel_name)
            cache.set(self.opCode, self, TIME_TO_LIVE)

    def player_count(self):
        count = 0
        for key in self.map_channel_name_to_role:
            if self.map_channel_name_to_role[key][:6] == 'player':
                count += 1
        return count

    def start(self):
        cache.set(self.opCode, self, TIME_TO_LIVE)
        # pass

    def end(self):
        if not cache.has_key(self.opCode):
            return
        # cache.delete(self.opCode)

    def record_detail(self, detail):
        self.detail.append(detail)
        cache.set(self.opCode, self, TIME_TO_LIVE)

    @abstractmethod
    def send_start(self):
        pass

    @abstractmethod
    def action_and_judge_game_over(self, message):
        pass


class gobang_battle(battle):

    def __init__(self, opCode, id1, id2, first_go):
        battle.__init__(self, opCode, id1, id2)
        self.first_go = first_go
        self.BLOCK = 3
        self.WHITE = 2
        self.BLACK = 1
        self.EMPTY = 0
        self.BOARD_SIZE = 15
        self.PLAYER_NUM = 2
        self.REPEATED_MAX = 3
        # 棋盘外层一圈BLOCK
        self.chess_board = [[self.BLOCK for i in range(self.BOARD_SIZE + 2)] for j in range(self.BOARD_SIZE + 2)]
        self.step_count = [[0 for i in range(self.BOARD_SIZE + 2)] for j in range(self.BOARD_SIZE + 2)]
        self.repeated_count = {}
        # 将棋盘初始化为EMPTY
        for i in range(1, self.BOARD_SIZE + 1):
            for j in range(1, self.BOARD_SIZE + 1):
                self.chess_board[i][j] = self.EMPTY

    def send_start(self):
        return {'type': 'gameStart'}

    def action_and_judge_game_over(self, message):
        color = message['color']
        # 落子信息格式有误，比赛终止
        try:
            row = int(message['row'])
            col = int(message['col'])
            count = int(message['count'])
        except:
            return True

        if row not in range(1, self.BOARD_SIZE + 1) or col not in range(1, self.BOARD_SIZE + 1):
            return True
        if self.chess_board[row][col] != self.EMPTY:
            if color == 'black' and self.chess_board[row][col] == self.WHITE:
                return True
            if color == 'white' and self.chess_board[row][col] == self.BLACK:
                return True
            if self.step_count[row][col] != count:
                return True
            # 一方持续发送落子信息，表明另一方超时或掉线，比赛终止
            elif self.repeated_count[(row, col)] >= self.REPEATED_MAX:
                return True
            else:
                self.repeated_count[(row, col)] += 1
                return False
        else:
            self.record_detail({'color': color, 'row': row, 'col': col})
            self.repeated_count[(row, col)] = 1
            if color == 'black':
                self.chess_board[row][col] = self.BLACK
            else:
                self.chess_board[row][col] = self.WHITE
            self.step_count[row][col] = count
            cache.set(self.opCode, self, TIME_TO_LIVE)
            return gobang_judge(self.chess_board, row, col)

class nod():
    def __init__(self, h, g, x, y, target):
        self.h = h
        self.g = g
        self.f = h + g
        self.x = x
        self.y = y
        self.target = target

    def geth(self):
        return self.h

    def getx(self):
        return self.x

    def gety(self):
        return self.y

    def gett(self):
        return self.target

    def __lt__(self, other):
        return self.f < other.f

    def __str__(self):
        return 'h:' + str(self.h) + ' g:' + str(self.g)

class snake_battle(battle):

    def __init__(self, opCode, id1, id2, firstgo):
        battle.__init__(self, opCode, id1, id2)

        self.BOARD_SIZE = 30

        self.mapjz = [[0] * self.BOARD_SIZE for i in range(self.BOARD_SIZE)]
        self.tarjz1 = [[-1] * self.BOARD_SIZE for i in range(self.BOARD_SIZE)]
        self.tarjz2 = [[-1] * self.BOARD_SIZE for i in range(self.BOARD_SIZE)]


        self.message_set = set()
        self.BORDER = 18
        self.LEFTBOARD = -105
        self.RIGHTBOARD = 150
        self.UPBOARD = 150
        self.BOTTOMBOARD = -105 #四个边界的坐标
        self.UP = 0
        self.RIGHT = 90
        self.DOWN = 180
        self.LEFT = 270
        self.ALGORITHM1 = 1234
        self.ALGORITHM2 = 2345
        self.ALGORITHM3 = 3456
        self.PLAYER_NUM = 2
        self.COUNT_MAX = 200
        self.APPLE_NUM = 3
        self.FIRST_GO = 0
        if firstgo == 1:
            self.FIRST_GO = -1 #发起挑战的在坐下角
        else:
            self.FIRST_GO = 1
        self.ID1FIRSTX = -60 * self.FIRST_GO
        self.ID1FIRSTY = -60 * self.FIRST_GO
        self.ID2FIRSTX = 60 * self.FIRST_GO
        self.ID2FIRSTY = 60 * self.FIRST_GO





        self.inf1_counts = 0
        self.inf2_counts = 0
        self.repeat_max_counts = 20

        self.id1current_to = 0
        self.id2current_to = 0
        self.id1x = self.ID1FIRSTX
        self.id2x = self.ID2FIRSTX
        self.id1y = self.ID1FIRSTY
        self.id2y = self.ID2FIRSTY
        self.id1tx = self.id1x
        self.id1ty = self.id1y
        self.id2tx = self.id2x
        self.id2ty = self.id2y
        self.id1l = 0
        self.id2l = 0

        self.applex = [1,2,3]
        self.appley = [1,2,3]
        self.appleid = [0,0,0]
        self.apple_cnum = 0

        self.id1score = 0  #id1和id2的得分
        self.id2score = 0
        self.count = 0  #记录移动的次数
        self.id1movx = [] #记录id1和id2每次的移动位置
        self.id1movy = [] #game_replay相关的数据存储
        self.id2movx = []
        self.id2movy = []
        self.apple_mov_x = [[0 for i in range(self.APPLE_NUM+1)] for i in range(self.COUNT_MAX+1)]
        self.apple_mov_y = [[0 for i in range(self.APPLE_NUM+1)] for i in range(self.COUNT_MAX+1)]
        self.apple_mov_id = [[0 for i in range(self.APPLE_NUM+1)] for i in range(self.COUNT_MAX+1)]
        self.id1_score_count = []
        self.id2_score_count = [] #game_replay相关数据存储结束
        # self.applelist = [] #记录出现苹果的移动次数
        # self.applelistx = [] #记录出现第i次的苹果的x值
        # self.applelisty = [] #记录出现第i次的苹果的y
        #self.tcount = 0
        self.id1_movd = False
        self.id2_movd = False
        self.bodyx_list = [[] for i in range(3)]
        self.bodyy_list = [[] for i in range(3)]
        self.body_num = [0,0,0]
        self.opCode = opCode

        for i in range(self.BORDER):
            self.mapjz[i][1] = 1
            self.mapjz[1][i] = 1
            self.mapjz[i][self.BORDER] = 1
            self.mapjz[self.BORDER][i] = 1
            self.mapjz[self.BORDER][self.BORDER] = 1
        self.mapjz[int(self.id1x/15+8)][int(self.id1y/15+8)] = 1
        self.mapjz[int(self.id2x/15+8)][int(self.id2y/15+8)] = 1

    def mybfs(self,x1,y1,x2,y2):

        # for i in range(20):
        #     print(self.mapjz[i])

        x1 = int(x1 / 15 + 8)
        y1 = int(y1 / 15 + 8)
        x2 = int(x2 / 15 + 8)
        y2 = int(y2 / 15 + 8)
        mapai = [[0] * self.BOARD_SIZE for i in range(self.BOARD_SIZE)]
        mapvisit = [[0] * self.BOARD_SIZE for i in range(self.BOARD_SIZE)]
        queue = PriorityQueue()
        visited = set()

        s = abs(x2 - x1) + abs(y2 - y1)
        first_nod = nod(0, s, x1, y1, 'u')
        queue.put(first_nod)
        while not queue.empty():
            cnod = queue.get()
            pos = [cnod.getx(), cnod.gety()]
            if (pos[0], pos[1]) in visited:
                continue
            mapvisit[pos[0]][pos[1]] = cnod.gett()
            visited.add((pos[0], pos[1]))
            cstep = cnod.geth()
            if pos[0] == x2 and pos[1] == y2:
                x = x2
                y = y2
                while True:
                    if x == x1 and y == y1:
                        break
                    if mapvisit[x][y] == self.UP:
                        y += 1
                        mapai[x][y] = self.DOWN  # y-1=left y+1=right x-1=up x+1=down
                    elif mapvisit[x][y] == self.DOWN:
                        y -= 1
                        mapai[x][y] = self.UP
                    elif mapvisit[x][y] == self.RIGHT:
                        x += 1
                        mapai[x][y] = self.LEFT
                    elif mapvisit[x][y] == self.LEFT:
                        x -= 1
                        mapai[x][y] = self.RIGHT
                return mapai[x1][y1]
            else:
                if pos[0] + 1 >= 0 and pos[0] + 1 <= 20 and pos[1] >= 0 and pos[1] <= 20:
                    if self.mapjz[pos[0] + 1][pos[1]] == 0 and (pos[0] + 1, pos[1]) not in visited:
                        h = cstep + 1
                        g = abs(x2 - (pos[0] + 1)) + abs(y2 - (pos[1]))
                        nnod = nod(h, g, pos[0] + 1, pos[1], self.LEFT)
                        queue.put(nnod)

                if pos[0] >= 0 and pos[0] <= 20 and pos[1] + 1 >= 0 and pos[1] + 1 <= 20:
                    if self.mapjz[pos[0]][pos[1] + 1] == 0 and (pos[0], pos[1] + 1) not in visited:
                        h = cstep + 1
                        g = abs(x2 - (pos[0])) + abs(y2 - (pos[1] + 1))
                        nnod = nod(h, g, pos[0], pos[1] + 1, self.DOWN)
                        queue.put(nnod)

                if pos[0] - 1 >= 0 and pos[0] - 1 <= 20 and pos[1] >= 0 and pos[1] <= 20:
                    if self.mapjz[pos[0] - 1][pos[1]] == 0 and (pos[0] - 1, pos[1]) not in visited:
                        h = cstep + 1
                        g = abs(x2 - (pos[0] - 1)) + abs(y2 - (pos[1]))
                        nnod = nod(h, g, pos[0] - 1, pos[1], self.RIGHT)
                        queue.put(nnod)

                if pos[0] >= 0 and pos[0] <= 20 and pos[1] - 1 >= 0 and pos[1] - 1 <= 20:
                    if self.mapjz[pos[0]][pos[1] - 1] == 0 and (pos[0], pos[1] - 1) not in visited:
                        h = cstep + 1
                        g = abs(x2 - (pos[0])) + abs(y2 - (pos[1] - 1))
                        nnod = nod(h, g, pos[0], pos[1] - 1, self.UP)
                        queue.put(nnod)
        return random.choice([self.LEFT,self.RIGHT,self.DOWN,self.UP])

    def send_start(self):
        message = {}
        message['type']='gameStart'
        message['left_border'] = self.LEFTBOARD
        message['right_border'] = self.RIGHTBOARD
        message['bottom_border'] = self.BOTTOMBOARD
        message['top_border'] = self.UPBOARD
        message['max_count'] = self.COUNT_MAX
        message['id1x'] = self.ID1FIRSTX
        message['id1y'] = self.ID1FIRSTY
        message['id2x'] = self.ID2FIRSTX
        message['id2y'] = self.ID2FIRSTY
        message['apple_num'] = self.APPLE_NUM
        message['id1l'] = self.id1l
        message['id2l'] = self.id2l
        if self.FIRST_GO == -1:
            message['firstid'] = self.production_id_1
        else:
            message['firstid'] = self.production_id_2

        self.id1x = self.ID1FIRSTX
        self.id2x = self.ID2FIRSTX
        self.id1y = self.ID1FIRSTY
        self.id2y = self.ID2FIRSTY
        self.apple_flash()
        for var in range(self.APPLE_NUM):
            self.apple_mov_x[self.count][var] = self.applex[var]
            self.apple_mov_y[self.count][var] = self.appley[var]
            self.apple_mov_id[self.count][var] = self.appleid[var]
        for var in range(self.APPLE_NUM):
            message['applex'+str(var)] = self.applex[var]
            message['appley'+str(var)] = self.appley[var]
            message['appleid'+str(var)] = self.appleid[var]
        cache.set(self.opCode, self, TIME_TO_LIVE)

        return message

    def snake_col_judge(self,id1x,id1y,idd): #苹果碰撞检测

        for var in range(self.APPLE_NUM):
            if self.appleid[var] == 1:
                lx = id1x - self.applex[var]
                ly = id1y - self.appley[var]
                if lx < 0:
                    lx = -lx
                if ly < 0:
                    ly = -ly
                if lx < 15 and ly < 15:
                    return var
        if idd == 1:
            self.mapjz[int(self.id1tx / 15 + 8)][int(self.id1ty / 15 + 8)] -= 1
            if self.tarjz1[int(self.id1tx/15+8)][int(self.id1ty/15+8)] == self.UP:
                self.id1ty += 15
            elif self.tarjz1[int(self.id1tx/15+8)][int(self.id1ty/15+8)] == self.DOWN:
                self.id1ty -= 15
            elif self.tarjz1[int(self.id1tx/15+8)][int(self.id1ty/15+8)] == self.LEFT:
                self.id1tx -= 15
            elif self.tarjz1[int(self.id1tx/15+8)][int(self.id1ty/15+8)] == self.RIGHT:
                self.id1tx += 15
        if idd == 2:
            self.mapjz[int(self.id2tx / 15 + 8)][int(self.id2ty / 15 + 8)] -= 1
            if self.tarjz2[int(self.id2tx/15+8)][int(self.id2ty/15+8)] == self.UP:
                self.id2ty += 15
            elif self.tarjz2[int(self.id2tx/15+8)][int(self.id2ty/15+8)] == self.DOWN:
                self.id2ty -= 15
            elif self.tarjz2[int(self.id2tx/15+8)][int(self.id2ty/15+8)] == self.LEFT:
                self.id2tx -= 15
            elif self.tarjz2[int(self.id2tx/15+8)][int(self.id2ty/15+8)] == self.RIGHT:
                self.id2tx += 15
        return -1

    def action_and_judge_game_over(self, message): #控制运动
        if message['id'] == 1:  # 如果有一方停止发送数据 即一直只接受到另一方的数据 则游戏结束
            self.inf1_counts += 1
        if message['id'] == 2:
            self.inf2_counts += 1
        print("l1=" + str(self.inf1_counts))
        print("l2=" + str(self.inf2_counts))
        if abs(self.inf1_counts - self.inf2_counts) >= self.repeat_max_counts:
            return True


        if message['update'] == 'body_inf':
            pass
        else:
            if message['count'] != self.count:
                return self.snake_judge_if_end()

            if message['ramcod'] in self.message_set:
                cache.set(self.opCode, self, TIME_TO_LIVE)
                return False
            else:
                self.message_set.add(message['ramcod'])

            if message['id'] == 1:
                self.id1current_to = int(message['towards'])
                self.id1_movd = True
            if message['id'] == 2:
                self.id2current_to = int(message['towards'])
                self.id2_movd = True

        if self.id1_movd is True and self.id2_movd is True:
            self.id1_movd = False
            self.id2_movd = False
            self.inf1_counts = 0
            self.inf2_counts = 0
            self.body_board_col_judge()
            self.snake_move()

            t1 = self.snake_col_judge(self.id1x,self.id1y,1)
            t2 = self.snake_col_judge(self.id2x,self.id2y,2)
            if t1 != -1:
                self.id1_got_score(t1)
                self.id1l += 1
            if t2 != -1:
                self.id2_got_score(t2)
                self.id2l += 1
            if t1 != -1:
                self.appleid[t1] = 0
            if t2 != -1:
                self.appleid[t2] = 0 # 把果子id设为0（不可用）
            t3 = 0
            for var in range(self.APPLE_NUM):
                if self.appleid[var] == 1:
                    t3 = 1
            if t3 == 0:
                self.apple_flash()
            self.count += 1
            self.id1movx.append(self.id1x)      #双方的移动信息记录下来
            self.id1movy.append(self.id1y)
            self.id2movx.append(self.id2x)
            self.id2movy.append(self.id2y)
            for var in range(self.APPLE_NUM):
                self.apple_mov_x[self.count][var] = self.applex[var]
                self.apple_mov_y[self.count][var] = self.appley[var]
                self.apple_mov_id[self.count][var] = self.appleid[var]
            self.id1_score_count.append(self.id1score)
            self.id2_score_count.append(self.id2score)
            message['id'] = '3'
            message['id1x'] = self.id1x
            message['id1y'] = self.id1y
            message['id2x'] = self.id2x
            message['id2y'] = self.id2y
            message['id1score'] = self.id1score
            message['id2score'] = self.id2score
            message['id1towards'] = self.id1current_to
            message['id2towards'] = self.id2current_to
            message['count'] = self.count
            message['max_count'] = self.COUNT_MAX
            message['id1l'] = self.id1l
            message['id2l'] = self.id2l

            for var in range(self.APPLE_NUM):
                message['applex' + str(var)] = self.applex[var]
                message['appley' + str(var)] = self.appley[var]
                message['appleid' + str(var)] = self.appleid[var]


        cache.set(self.opCode, self, TIME_TO_LIVE)
        return self.snake_judge_if_end()




    def apple_flash(self):
        #苹果1必须距离id1近且不会生成在蛇的身子上
        while True:
            self.applex[1] = int(random.randint(self.LEFTBOARD + 10, self.RIGHTBOARD - 10) / 15) * 15
            self.appley[1] = int(random.randint(self.BOTTOMBOARD + 10, self.UPBOARD - 10) / 15) * 15
            if self.mapjz[int(self.applex[1]/15+8)][int(self.appley[1]/15+8)] != 0:
                continue
            if abs(self.applex[1]-self.id1x) + abs(self.appley[1]-self.id1y) <= abs(self.applex[1]-self.id2x) + abs(self.appley[1]-self.id2y):
                break
        #苹果2必须距离id2近且不会生成在蛇的身子上
        while True:
            self.applex[2] = int(random.randint(self.LEFTBOARD + 10, self.RIGHTBOARD - 10) / 15) * 15
            self.appley[2] = int(random.randint(self.BOTTOMBOARD + 10, self.UPBOARD - 10) / 15) * 15
            if self.mapjz[int(self.applex[2]/15+8)][int(self.appley[2]/15+8)] != 0:
                continue
            if abs(self.applex[2]-self.id2x) + abs(self.appley[2]-self.id2y) <= abs(self.applex[2]-self.id1x) + abs(self.appley[2]-self.id1y):
                break
        #大苹果必须距离id1和id2相差不多且不会生成在蛇的身子上
        while True:
            self.applex[0] = int(random.randint(self.LEFTBOARD + 10, self.RIGHTBOARD - 10) / 15) * 15
            self.appley[0] = int(random.randint(self.BOTTOMBOARD + 10, self.UPBOARD - 10) / 15) * 15
            if self.mapjz[int(self.applex[0]/15+8)][int(self.appley[0]/15+8)] != 0:
                continue
            if abs(abs(self.applex[0]-self.id2x) + abs(self.appley[0]-self.id2y) - abs(self.applex[0]-self.id1x) - abs(self.appley[0]-self.id1y)) <= 30:
                break
        for var in range(self.APPLE_NUM):
            self.appleid[var] = 1
        # for var in range(self.APPLE_NUM):
        #     self.applex[var] = int(random.randint(self.LEFTBOARD + 10, self.RIGHTBOARD - 10)/15)*15
        #     self.appley[var] = int(random.randint(self.BOTTOMBOARD + 10, self.UPBOARD - 10)/15)*15
        #     self.appleid[var] = 1




    def id1_got_score(self,t):
        if t == 0:
            self.id1score += 5
        else:
            self.id1score += 3
    def id2_got_score(self,t):
        if t == 0:
            self.id2score += 5
        else:
            self.id2score += 3
    def body_board_col_judge(self): #边界碰撞检测

        if self.id1current_to == self.ALGORITHM1: #内置算法
            self.id1current_to = self.mybfs(self.id1x,self.id1y,self.applex[1],self.appley[1])
        elif self.id1current_to == self.ALGORITHM2:
            self.id1current_to = self.mybfs(self.id1x, self.id1y, self.applex[2], self.appley[2])
        elif self.id1current_to == self.ALGORITHM3:
            self.id1current_to = self.mybfs(self.id2x, self.id2y, self.applex[0], self.appley[0])
        if self.id2current_to == self.ALGORITHM1:
            self.id2current_to = self.mybfs(self.id2x,self.id2y,self.applex[1],self.appley[1])
        elif self.id2current_to == self.ALGORITHM2:
            self.id2current_to = self.mybfs(self.id2x, self.id2y, self.applex[2], self.appley[2])
        elif self.id2current_to == self.ALGORITHM3:
            self.id2current_to = self.mybfs(self.id2x, self.id2y, self.applex[0], self.appley[0])

        if self.id1current_to == 0 and self.id1y+15 >= self.UPBOARD:
            self.id1current_to = -1
        if self.id1current_to == 90 and self.id1x+15 >= self.RIGHTBOARD:
            self.id1current_to = -1
        if self.id1current_to == 180 and self.id1y-15 <= self.BOTTOMBOARD:
            self.id1current_to = -1
        if self.id1current_to == 270 and self.id1x-15 <=self.LEFTBOARD:
            self.id1current_to = -1
        if self.id2current_to == 0 and self.id2y+15 >= self.UPBOARD:
            self.id2current_to = -1
        if self.id2current_to == 90 and self.id2x+15 >= self.RIGHTBOARD:
            self.id2current_to = -1
        if self.id2current_to == 180 and self.id2y-15 <= self.BOTTOMBOARD:
            self.id2current_to = -1
        if self.id2current_to == 270 and self.id2x-15 <= self.LEFTBOARD:
            self.id2current_to = -1
        return 0

    def snake_move(self):
        prex = self.id2x
        prey = self.id2y

        self.tarjz1[int(self.id1x / 15 + 8)][int(self.id1y / 15 + 8)] = self.id1current_to
        self.tarjz2[int(self.id2x / 15 + 8)][int(self.id2y / 15 + 8)] = self.id2current_to
        if self.id1current_to == self.UP:  # 蛇头的移动
            self.id1y += 15
        elif self.id1current_to == self.RIGHT:
           self.id1x += 15
        elif self.id1current_to == self.DOWN:
            self.id1y -= 15
        elif self.id1current_to == self.LEFT:
            self.id1x -= 15
        if self.id2current_to == self.UP:
            self.id2y += 15
        elif self.id2current_to == self.RIGHT:
            self.id2x += 15
        elif self.id2current_to == self.DOWN:
            self.id2y -= 15
        elif self.id2current_to == self.LEFT:
            self.id2x -= 15
        if self.id1x == self.id2x and self.id1y == self.id2y:
            self.id2x = prex
            self.id2y = prey
        if self.mapjz[int(self.id1x/15+8)][int(self.id1y/15+8)] != 0:
            if self.id1score >= 5:
                self.id1score -= 5
            else:
                self.id1score = 0
        if self.mapjz[int(self.id2x/15+8)][int(self.id2y/15+8)] != 0:
            if self.id2score >= 5:
                self.id2score -= 5
            else:
                self.id2score = 0
        self.mapjz[int(self.id1x / 15 + 8)][int(self.id1y / 15 + 8)] += 1
        self.mapjz[int(self.id2x / 15 + 8)][int(self.id2y / 15 + 8)] += 1

    def snake_judge_if_end(self):
        if self.count >= self.COUNT_MAX :
            return True
        else:
            return False

    def mmapjz(self,x,y):
        return self.mapjz[x][y]