def gobang_judge(chessboard, row, col):
    color = chessboard[row][col]
    count = 0
    i, j = row, col
    while i >= 1 and i <= 15 and j >= 1 and j <= 15 and chessboard[i][j] == color:
        i, count = i + 1, count + 1
    i, j = row, col
    while i >= 1 and i <= 15 and j >= 1 and j <= 15 and chessboard[i][j] == color:
        i, count = i - 1, count + 1
    if count - 1 >= 5:
        return True

    count = 0
    i, j = row, col
    while i >= 1 and i <= 15 and j >= 1 and j <= 15 and chessboard[i][j] == color:
        j, count = j + 1, count + 1
    i, j = row, col
    while i >= 1 and i <= 15 and j >= 1 and j <= 15 and chessboard[i][j] == color:
        j, count = j - 1, count + 1
    if count - 1 >= 5:
        return True

    count = 0
    i, j = row, col
    while i >= 1 and i <= 15 and j >= 1 and j <= 15 and chessboard[i][j] == color:
        i, j, count = i + 1, j + 1, count + 1
    i, j = row, col
    while i >= 1 and i <= 15 and j >= 1 and j <= 15 and chessboard[i][j] == color:
        i, j, count = i - 1, j - 1, count + 1
    if count - 1 >= 5:
        return True

    count = 0
    i, j = row, col
    while i >= 1 and i <= 15 and j >= 1 and j <= 15 and chessboard[i][j] == color:
        i, j, count = i - 1, j + 1, count + 1
    i, j = row, col
    while i >= 1 and i <= 15 and j >= 1 and j <= 15 and chessboard[i][j] == color:
        i, j, count = i + 1, j - 1, count + 1
    if count - 1 >= 5:
        return True

    return False

