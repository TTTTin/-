
class GobangBot:

    def __init__(self, chessboard, color):
        self.chess_board, self.color, self.SIZE = chessboard, color, len(chessboard)
        self.EMPTY, self.BLACK, self.WHITE = -1, 0, 1
        self.strategy = [[set() for j in range(self.SIZE)] for i in range(self.SIZE)]
        self.strategy_count = 0

        for i in range(self.SIZE):
            for j in range(self.SIZE - 4):
                for k in range(5):
                    self.strategy[i][j + k].add(self.strategy_count)
                self.strategy_count += 1
        for i in range(self.SIZE - 4):
            for j in range(self.SIZE):
                for k in range(5):
                    self.strategy[i + k][j].add(self.strategy_count)
                self.strategy_count += 1
        for i in range(self.SIZE - 4):
            for j in range(self.SIZE - 4):
                for k in range(5):
                    self.strategy[i + k][j + k].add(self.strategy_count)
                self.strategy_count += 1
        for i in range(self.SIZE - 4):
            for j in range(4, self.SIZE):
                for k in range(5):
                    self.strategy[i + k][j - k].add(self.strategy_count)
                self.strategy_count += 1

        self.black_wins, self.white_wins = [0 for i in range(self.strategy_count)], [0 for i in range(self.strategy_count)]

        for row in range(self.SIZE):
            for col in range(self.SIZE):
                if self.chess_board[row][col] == self.EMPTY:
                    continue
                self.one_step(row, col, self.chess_board[row][col] % 2)

    def one_step(self, row, col, color):
        self.chess_board[row][col] = color
        if color == self.BLACK:
            for s in self.strategy[row][col]:
                self.black_wins[s], self.white_wins[s] = self.black_wins[s] + 1, 6
        else:
            for s in self.strategy[row][col]:
                self.black_wins[s], self.white_wins[s] = 6, self.white_wins[s] + 1

    def action(self):
        ans = (self.SIZE // 2, self.SIZE // 2, 0)
        if self.chess_board[ans[0]][ans[1]] != self.EMPTY:
            for row in range(self.SIZE):
                for col in range(self.SIZE):
                    if self.chess_board[row][col] != self.EMPTY:
                        continue
                    ans = (row, col, 0)
                    break
        for row in range(self.SIZE):
            for col in range(self.SIZE):
                if self.chess_board[row][col] != self.EMPTY:
                    continue
                black_score, white_score = 0, 0
                for s in self.strategy[row][col]:
                    if self.color == self.BLACK:
                        if self.black_wins[s] == 1:
                            black_score += 200
                        elif self.black_wins[s] == 2:
                            black_score += 400
                        elif self.black_wins[s] == 3:
                            black_score += 2000
                        elif self.black_wins[s] == 4:
                            black_score += 10000

                        if self.white_wins[s] == 1:
                            white_score += 220
                        elif self.white_wins[s] == 2:
                            white_score += 420
                        elif self.white_wins[s] == 3:
                            white_score += 2400
                        elif self.white_wins[s] == 4:
                            white_score += 20000
                    else:
                        if self.black_wins[s] == 1:
                            black_score += 220
                        elif self.black_wins[s] == 2:
                            black_score += 420
                        elif self.black_wins[s] == 3:
                            black_score += 2400
                        elif self.black_wins[s] == 4:
                            black_score += 20000

                        if self.white_wins[s] == 1:
                            white_score += 200
                        elif self.white_wins[s] == 2:
                            white_score += 400
                        elif self.white_wins[s] == 3:
                            white_score += 2000
                        elif self.white_wins[s] == 4:
                            white_score += 10000

                    if black_score == 0 and white_score == 0:
                        continue
                    if black_score + white_score > ans[2]:
                        ans = (row, col, black_score + white_score)

        return ans[0], ans[1]