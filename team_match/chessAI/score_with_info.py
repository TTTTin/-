
class Score:
    ONE = 10
    TWO = 100
    THREE = 1000
    FOUR = 100000
    FIVE = 10000000
    BLOCKED_ONE = 1
    BLOCKED_TWO = 10
    BLOCKED_THREE = 100
    BLOCKED_FOUR = 10000

def score_with_count_emptyIndex_block(count, emptyIndex, block):
    '''
    :param count:
    :param emptyIndex:
    :param block:
    :return:
    '''
    # 没有空位
    if emptyIndex <= 0:
        if count >= 5: return Score.FIVE
        if block == 0:
            if count == 4: return Score.FOUR
            if count == 3: return Score.THREE
            if count == 2: return Score.TWO
            if count == 1: return Score.ONE
        if block == 1:
            if count == 4: return Score.BLOCKED_FOUR
            if count == 3: return Score.BLOCKED_THREE
            if count == 2: return Score.BLOCKED_TWO
            if count == 1: return Score.BLOCKED_ONE
    # 空位位置为 1
    elif emptyIndex == 1 or emptyIndex == count - 1:
        if count >= 6: return Score.FIVE
        if block == 0:
            if count == 5: return Score.FOUR
            if count == 4: return Score.BLOCKED_FOUR
            if count == 3: return Score.THREE
            if count == 2: return Score.TWO / 2
        if block == 1:
            if count == 5: return Score.BLOCKED_FOUR
            if count == 4: return Score.BLOCKED_FOUR
            if count == 3: return Score.BLOCKED_THREE
            if count == 2: return Score.BLOCKED_TWO
    # 空位位置为 2
    elif emptyIndex == 2 or emptyIndex == count - 2:
        if count >= 7: return Score.FIVE
        if block == 0:
            if count == 3: return Score.THREE
            if count == 4 or count == 5: return Score.BLOCKED_FOUR
            if count == 6: return Score.FOUR
        if block == 1:
            if count == 3: return Score.BLOCKED_THREE
            if count == 4 or count == 5: return Score.BLOCKED_FOUR
            if count == 5: return Score.FOUR
        if block == 2:
            if count == 4 or count == 5 or count == 6: return Score.BLOCKED_FOUR
    # 空位位置为 3
    elif emptyIndex == 3 or emptyIndex == count - 3:
        if count >= 8: return Score.FIVE
        if block == 0:
            if count == 4 or count == 5: return Score.THREE
            if count == 6: return Score.BLOCKED_FOUR
            if count == 7: return Score.FOUR
        if block == 1:
            if count == 4 or count == 5 or count == 6: return Score.BLOCKED_FOUR
            if count == 7: return Score.FOUR
        if block == 2:
            if count == 4 or count == 5 or count == 6 or count == 7: return Score.BLOCKED_FOUR
    # 空位位置为 4
    elif emptyIndex == 4 or emptyIndex == count - 4:
        if count >= 9: return Score.FIVE
        if block == 0:
            if count == 5 or count == 6 or count == 7 or count == 8: return Score.FOUR
        if block == 1:
            if count == 4 or count == 5 or count == 6 or count == 7: return Score.BLOCKED_FOUR
            if count == 8: return Score.FOUR
        if block == 2:
            if count == 5 or count == 6 or count == 7 or count == 8: return Score.BLOCKED_FOUR
    # 空位位置为 5
    elif emptyIndex == 5 or emptyIndex == count - 5:
        return Score.FIVE
    return 0