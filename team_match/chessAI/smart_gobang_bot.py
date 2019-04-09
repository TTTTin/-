from team_match.chessAI.score_with_info import score_with_count_emptyIndex_block
import sys
from team_match.chessAI.score_with_info import Score

MAX_INT = sys.maxsize
MIN_INT = -sys.maxsize

# 未完待续
class GobangBot:
    def __init__(self, chessboard, color):
        self.EMPTY, self.BLACK, self.WHITE = -1, 0, 1
        self.AI, self.PLAYER = color, color ^ 1
        self.SIZE = len(chessboard)

        self.MAX_DEPTH = 3
        self.GEN_POINT_NUM_MAX = 20
        # 初始化棋盘
        self.chessboard = [[(obj if obj == self.EMPTY else obj % 2) for obj in line] for line in chessboard]

        self.aiScore = [[0 for i in range(self.SIZE)] for j in range(self.SIZE)] # row 1-15, col 1-15
        self.aiScoreDifferentDir = [[[0, 0, 0, 0] for i in range(self.SIZE)] for j in range(self.SIZE)]

        self.playerScore = [[0 for i in range(self.SIZE)] for j in range(self.SIZE)] # row 1-15, col 1-15
        self.playerScoreDifferentDir = [[[0, 0, 0, 0] for i in range(self.SIZE)] for j in range(self.SIZE)]

        self.internal = [[0, -4], [-4, 0], [-4, -4], [4, -4]]
        self.direction = [[0, 1], [1, 0], [1, 1], [-1, 1]]

        self.allSteps = 0

        for i in range(self.SIZE):
            for j in range(self.SIZE):
                if self.chessboard[i][j] != self.EMPTY:
                    self.allSteps += 1
                    continue
                for direction in range(4):

                    tempScore = self.score(i, j, self.AI, direction)
                    self.aiScoreDifferentDir[i][j][direction] = tempScore
                    self.aiScore[i][j] += tempScore

                    tempScore = self.score(i, j, self.PLAYER, direction)
                    self.playerScoreDifferentDir[i][j][direction] = tempScore
                    self.playerScore[i][j] += tempScore

        self.over = 0  # AI or PLAYER or 0

    def judge(self, row, col):
        role = self.chessboard[row][col]
        # 别分别 横向 纵向 斜向右下 斜向右上
        dir = []
        dir.append([[1, 0], [-1, 0]])
        dir.append([[0, 1], [0, -1]])
        dir.append([[1, 1], [-1, -1]])
        dir.append([[1, -1], [-1, 1]])
        for k in range(4):
            count = 0
            i, j = row, col
            while i in range(self.SIZE) and j in range(self.SIZE) and self.chessboard[i][j] == role:
                i, j, count = i + dir[k][0][0], j + dir[k][0][1], count + 1
            i, j = row, col
            while i in range(self.SIZE) and j in range(self.SIZE) and self.chessboard[i][j] == role:
                i, j, count = i + dir[k][1][0], j + dir[k][1][1], count + 1
            if count - 1 >= 5:
                return True
        return False

    def dfs(self, depth, D, role, flag, over):
        # D 是对于每次迭代加深时的深度
        if depth == D or over:
            return self.score_board(self.AI), 0, 0

        genPoints = self.gen(role)

        if depth%2 == 0:
            targetScore, ansi, ansj = float("-inf"), 0, 0
            for point in genPoints:
                i, j = point[0], point[1]

                self.action(i, j, role)

                tempScore, tempi, tempj = self.dfs(depth + 1, D, self.reverseRole(role), targetScore, self.judge(i, j))

                self.remove(i, j)

                if tempScore > targetScore:
                    targetScore, ansi, ansj = tempScore, i, j
                if tempScore > flag:
                    return targetScore, ansi, ansj
                # MAX 层剪枝

        # MIN level
        else:
            targetScore, ansi, ansj = float("inf"), 0, 0
            for point in genPoints:
                i, j = point[0], point[1]

                self.action(i, j, role)

                tempScore, tempi, tempj = self.dfs(depth + 1, D, self.reverseRole(role), targetScore, self.judge(i, j))

                self.remove(i, j)

                if tempScore < targetScore:
                    targetScore, ansi, ansj = tempScore, i, j
                if tempScore < flag:
                    return tempScore, tempi, tempj
                # MIN 层剪枝

        return targetScore, ansi, ansj

    """
        row, col is the postsion of action
        role == PLAYER or AI
        return result is_actionError?
    """
    def action(self, row, col, role):
        if row not in range(self.SIZE) or col not in range(self.SIZE) or self.chessboard[row][col] != self.EMPTY:
            return False
        self.chessboard[row][col] = role
        if role == self.AI:
            self.playerScore[row][col] = 0
            for dir in range(4):
                self.playerScoreDifferentDir[row][col][dir] = 0
        else:
            self.aiScore[row][col] = 0
            for dir in range(4):
                self.aiScoreDifferentDir[row][col][dir] = 0
        self.update_score_points_around_one_point(row, col)
        self.allSteps += 1
        return True

    def remove(self, row, col):
        if row not in range(self.SIZE) or col not in range(self.SIZE) or self.chessboard[row][col] == self.EMPTY:
            return False
        self.chessboard[row][col] = self.EMPTY
        self.update_score_points_around_one_point(row, col)
        self.allSteps -= 1
        return True

    """
        evaluate the board for PLAYER or AI
    """

    def reverseRole(self, role):
        return role ^ 1

    """
        score board for role
    """
    def printChessBoard(self):
        print("*************************************************************************")
        print('\t', end='')
        for i in range(self.SIZE):
            print(i, end='\t')
        print()
        for i in range(self.SIZE):
            print(i, end='\t')
            for j in range(self.SIZE):
                if self.chessboard[i][j] == self.PLAYER:
                    ch = 'o'
                elif self.chessboard[i][j] == self.AI:
                    ch = 'x'
                else:
                    ch = '.'
                print(ch, end='\t')
            print()


    def score_board(self, role):
        scoreAI = 0
        scorePLAYER = 0
        for i in range(self.SIZE):
            for j in range(self.SIZE):
                if self.chessboard[i][j] == self.AI:
                    scoreAI += self.aiScore[i][j]           # 之后应对 aiScore 进行一个修正
                elif self.chessboard[i][j] == self.PLAYER:
                    scorePLAYER += self.playerScore[i][j]   # 之后应对 playerScore 进行一个修正
        # print("ai_score and player_score:",scoreAI,' ', scorePLAYER)
        if role == self.AI:
            return scoreAI - scorePLAYER
        else:
            return scorePLAYER - scoreAI

    def update_score_one_point(self, row, col, dir):
        role = self.chessboard[row][col]
        if role == self.AI:
            self.aiScore[row][col] -= self.aiScoreDifferentDir[row][col][dir]
            self.aiScoreDifferentDir[row][col][dir] = self.score(row, col, role, dir)
            self.aiScore[row][col] += self.aiScoreDifferentDir[row][col][dir]
        elif role == self.PLAYER:
            self.playerScore[row][col] -= self.playerScoreDifferentDir[row][col][dir]
            self.playerScoreDifferentDir[row][col][dir] = self.score(row, col, role, dir)
            self.playerScore[row][col] += self.playerScoreDifferentDir[row][col][dir]
        else:

            self.playerScore[row][col] -= self.playerScoreDifferentDir[row][col][dir]
            self.playerScoreDifferentDir[row][col][dir] = self.score(row, col, self.PLAYER, dir)
            self.playerScore[row][col] += self.playerScoreDifferentDir[row][col][dir]

            self.aiScore[row][col] -= self.aiScoreDifferentDir[row][col][dir]
            self.aiScoreDifferentDir[row][col][dir] = self.score(row, col, self.AI, dir)
            self.aiScore[row][col] += self.aiScoreDifferentDir[row][col][dir]


    # 已保证row, col位置不为空
    def score(self, row, col, role, dir):
        direction = self.direction[dir]
        count, emptyIndex, block = 1, -1, 0
        # 向一个方向搜索
        r, c = row, col
        while True:
            r, c = r + direction[0], c + direction[1]
            if r not in range(self.SIZE) or c not in range(self.SIZE):
                block += 1
                break
            if self.chessboard[r][c] == self.EMPTY:
                if emptyIndex == -1 \
                        and r + direction[0] in range(self.SIZE) and c + direction[1] in range(self.SIZE) and \
                                self.chessboard[r + direction[0]][c + direction[1]] == role:
                    emptyIndex = count
                else:
                    break
            elif self.chessboard[r][c] == role:
                count += 1
            else:
                block += 1
                break
    # 向反方向搜索
        r, c = row, col
        while True:
            r, c = r - direction[0], c - direction[1]
            if r not in range(self.SIZE) or c not in range(self.SIZE):
                block += 1
                break
            if self.chessboard[r][c] == self.EMPTY:
                if emptyIndex == -1 \
                        and r - direction[0] in range(self.SIZE) and c - direction[1] in range(self.SIZE) and \
                                self.chessboard[r - direction[0]][c - direction[1]] == role:
                    emptyIndex = 0
                else:
                    break
            elif self.chessboard[r][c] == role:
                count += 1
                if emptyIndex != -1:
                    emptyIndex += 1
            else:
                block += 1
                break
    # 根据 count、emptyIndex、 block 计算分数
        return score_with_count_emptyIndex_block(count, emptyIndex, block)

    def update_score_points_around_one_point(self, row, col):
        internal = self.internal
        dirction = self.direction
        for dir in range(4):
            x, y = row + internal[dir][0], col + internal[dir][1]
            for i in range(9):
                if x in range(self.SIZE) and y in range(self.SIZE):
                    self.update_score_one_point(x, y, dir)
                x, y = x + dirction[dir][0], y + dirction[dir][1]

    # 判断以row，col为中心，r为“半径”的范围内有没有count个邻居
    def has_neighbor(self, row, col, r, count):
        for i in range(row - r, row + r + 1):
            if i not in range(self.SIZE):
                continue
            for j in range(col - r, col + r + 1):
                if j not in range(self.SIZE):
                    continue
                if self.chessboard[i][j] != self.EMPTY:
                    count -= 1
                    if count <= 0:
                        return True
        return False

    # 启发式搜索，产生最有可能落子的点，并且按可能性大小从大到小排序
    def gen(self, role):
        if self.allSteps == 0:
            return [[8, 8]]

        fives = []
        aifours = []
        playerfours = []
        aiblockedfours = []
        playerblockedfours = []
        aitwothrees = []
        playertwothrees = []
        aithrees = []
        playerthrees = []
        aitwos = []
        playertwos = []
        neighbors = []
        for row in range(self.SIZE):
            for col in range(self.SIZE):
                if self.chessboard[row][col] != self.EMPTY:
                    continue
                if self.allSteps < 6:
                    if not self.has_neighbor(row, col, 1, 1):
                        continue
                else:
                    if not self.has_neighbor(row,col, 2, 2):
                        continue
                aiScore = self.aiScore[row][col]
                playerScore = self.playerScore[row][col]
                if aiScore >= Score.FIVE or playerScore >= Score.FIVE:
                    fives.append([row, col])
                elif aiScore >= Score.FOUR:
                    aifours.append([row, col])
                elif playerScore >= Score.FOUR:
                    playerfours.append([row, col])
                elif aiScore >= Score.BLOCKED_FOUR:
                    aiblockedfours.append([row, col])
                elif playerScore >= Score.BLOCKED_FOUR:
                    playerblockedfours.append([row, col])
                elif aiScore >= 2 * Score.THREE:
                    aitwothrees.append([row, col])
                elif playerScore >= 2 * Score.THREE:
                    playertwothrees.append([row, col])
                elif aiScore >= Score.THREE:
                    aithrees.append([row, col])
                elif playerScore >= Score.THREE:
                    playerthrees.append([row, col])
                elif aiScore >= Score.TWO:
                    aitwos.append([row, col, aiScore])
                elif playerScore >= Score.TWO:
                    playertwos.append([row, col, playerScore])
                else:
                    neighbors.append([row, col])

        if fives.__len__() > 0:
            return fives

        # 自己有活四
        if role == self.AI and aifours.__len__() > 0:
            return aifours
        if role == self.PLAYER and playerfours.__len__() > 0:
            return playerfours

        # 对面有活四，自己沖四都没有
        if role == self.AI and playerfours.__len__() > 0 and aiblockedfours.__len__() <= 0:
            return playerfours
        if role == self.PLAYER and aifours.__len__() > 0 and playerfours.__len__() <= 0:
            return aifours

        # 对面有活四，自己有沖四
        if role == self.AI and playerfours.__len__() > 0 and aiblockedfours.__len__() > 0:
            return playerfours + aiblockedfours
        if role == self.PLAYER and aifours.__len__() > 0 and playerblockedfours.__len__() > 0:
            return aifours + playerblockedfours

        # 其它情况
        if role == self.AI:
            result = aitwothrees + playertwothrees + aiblockedfours + playerblockedfours + aithrees + playerthrees
        else:
            result = playertwothrees + aitwothrees + playerblockedfours + aiblockedfours + playerthrees + aithrees

        # only threes ???
        if aitwos.__len__() > 0 or playertwos.__len__() > 0:
            if role == self.AI:
                twos = aitwos[::-1] + playertwos[::-1]
            else:
                twos = playertwos[::-1] + aitwos[::-1]
            def cmp_key(point):
                return point[2]
            twos.sort(key = cmp_key)
            twos = [[two[0], two[1]] for two in twos]
            result = result + twos
        else:
            result = result + neighbors

        return  result[:self.GEN_POINT_NUM_MAX] if result.__len__() > self.GEN_POINT_NUM_MAX else result

    def deep_go_gradually(self):
        D = 1
        score, i, j = MIN_INT, 0, 0
        while D <= self.MAX_DEPTH:
            score, i, j = self.dfs(0, D, self.AI, MAX_INT, False)
            if score > Score.FIVE:
                break
            D += 2
        return score, i, j


