import random
import time
import copy
from solver import create_variables
from solver import create_arc
from solver import arc_consistency_3
from solver import select_unassigned_variable
from solver import satisfy_constraint
from solver import read_file
TIME_LIMIT_SECONDS = 1


def elapsed_time(start_time):
    return time.time() - start_time


def backtrack(V, assignment, start_time):
    if elapsed_time(start_time) >= TIME_LIMIT_SECONDS:
        return False
    if len(assignment) == len(V):
        return True
    Vx = select_unassigned_variable(V, assignment)
    for val in Vx.domain:
        if val in assignment.values():
            continue
        if satisfy_constraint(V, assignment, Vx, val):
            assignment[Vx] = val
            result = backtrack(V, assignment, start_time)
            if result:
                return True
        assignment.pop(Vx, None)
    return False


def generate_crossword_board(height, width):
    board = [['#' for _ in range(width)] for _ in range(height)]
    return board


def place_word_horizontally(board, length, i, j):
    for k in range(length):
        board[i][j+k] = '-'


def place_word_vertically(board, length, i, j):
    for k in range(length):
        board[i+k][j] = '-'


def print_crossword_board(board):
    for row in board:
        print(''.join(row))


def get_final_board(boardstr, assignment):
    final_board = []
    board = boardstr.split("\n")
    board = [list(row) for row in board]
    for v in assignment:
        val = assignment[v]
        if v.direction == "horizontal":
            for i in range(v.length):
                board[v.row][v.col + i] = val[i]
        else:
            for i in range(v.length):
                board[v.row + i][v.col] = val[i]
    for row in board:
        final_board.append(''.join(row))
    return final_board


def get_temp_board(board):
    temp_board = ""
    for i, row in enumerate(board):
        if i == len(board) - 1:
            temp_board += ''.join(row)
        else:
            temp_board += ''.join(row) + "\n"
    return temp_board


def has_consecutive_chars(lst, char, consecutive_count):
    count = 0
    for c in lst:
        if c == char:
            count += 1
            if count >= consecutive_count:
                return True
        else:
            count = 0
    return False


def is_valid_placement(board, length, i, j, direction):
    if direction == "horizontal":
        return not has_consecutive_chars(board[i], '-', length)
    elif direction == "vertical":
        column = [board[x][j] for x in range(i, i + length)]
        return not has_consecutive_chars(column, '-', length)


def is_solveable(board, words):
    assignment = {}
    boardstr = get_temp_board(board)
    V = create_variables(boardstr, words)
    S = create_arc(V)

    arc_consistency_3(S)

    V.sort(key=lambda x: len(x.domain))

    start_time = time.time()
    result = backtrack(V, assignment, start_time)

    if result:
        boardstr = get_final_board(boardstr, assignment)
        for row in boardstr:
            if '-' in row:
                return False
        return True
    else:
        return False


def add_word_to_board(board, length, position):
    max_attempts = 10
    direction = "horizontal" if position % 2 == 0 else "vertical"

    for _ in range(max_attempts):
        if direction == "horizontal":
            choices = [
                (x, y)
                for x in range(len(board))
                for y in range(len(board[0]) - length + 1)
            ]
        else:
            choices = [
                (x, y)
                for x in range(len(board) - length + 1)
                for y in range(len(board[0]))
            ]
        i, j = random.choice(choices)

        if is_valid_placement(board, length, i, j, direction):
            if direction == "horizontal":
                place_word_horizontally(board, length, i, j)
            else:
                place_word_vertically(board, length, i, j)
            break


def save_board(board):
    with open("crossword.txt", "w") as file:
        for i, row in enumerate(board):
            file.write("".join(row))
            if i < len(board) - 1:
                file.write("\n")


def occupancy(board):
    white = 0
    black = 0
    for row in board:
        for c in row:
            if c == '-':
                white += 1
            else:
                black += 1
    return white / (white + black)


if __name__ == "__main__":
    height = 15
    width = 15
    max_attempts = 10
    words = read_file("words.txt").splitlines()

    time_start = time.time()

    testing_board = generate_crossword_board(height, width)

    if height <= 3 and width <= 3:
        for i in range(height):
            for j in range(width):
                testing_board[i][j] = '-'
        save_board(testing_board)
        exit()

    while True:
        word_length = random.randint(1, min(height, width))
        choice = random.randint(1, 2)  # vertical or horizontal
        final_board = copy.deepcopy(testing_board)
        add_word_to_board(testing_board, word_length, choice)

        if not is_solveable(testing_board, words):
            for _ in range(max_attempts):
                testing_board = copy.deepcopy(final_board)
                add_word_to_board(testing_board, word_length, choice)
                if is_solveable(testing_board, words):
                    break
            else:
                if occupancy(final_board) < 0.5:
                    testing_board = generate_crossword_board(height, width)
                    continue
                save_board(final_board)
                break

    print("Time taken: {} seconds".format(elapsed_time(time_start)))
    print("Final board:")
    print_crossword_board(final_board)
