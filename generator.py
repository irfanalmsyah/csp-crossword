import random
import time
import copy
from solver import create_variables, create_arc, arc_consistency_3, select_unassigned_variable, satisfy_constraint, read_file

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
    count = 0
    for row in board:
        for col in row:
            if col == "-":
                count += 1
    return count / (len(board) * len(board[0]))


def most_common_char_length(words):
    char_length = {}

    for word in words:
        length = len(word)
        char_length[length] = char_length.get(length, 0) + 1

    return sorted(char_length, key=char_length.get, reverse=True)


if __name__ == "__main__":
    height = 15
    width = 15
    max_attempts = 10
    words = read_file("words.txt").splitlines()
    mylist = most_common_char_length(words)
    total_elements = len(mylist)
    probabilities = [1 / (i + 1) for i in range(total_elements)]
    sum_probabilities = sum(probabilities)
    normalized_probabilities = [
        prob / sum_probabilities for prob in probabilities
    ]
    time_start = time.time()
    testing_board = generate_crossword_board(height, width)

    if height <= 3 and width <= 3:
        for i in range(height):
            for j in range(width):
                testing_board[i][j] = '-'
        save_board(testing_board)
        exit()

    while True:
        word_length = random.choices(
            mylist, weights=normalized_probabilities, k=1
        )[0]
        choice = random.randint(1, 2)  # vertical or horizontal
        backup_board = copy.deepcopy(testing_board)
        add_word_to_board(testing_board, word_length, choice)

        if is_solveable(testing_board, words):
            final_board = copy.deepcopy(testing_board)
            print(occupancy(final_board))
        else:
            testing_board = copy.deepcopy(backup_board)

        if occupancy(final_board) > 0.3:
            save_board(final_board)
            break

    print("Time taken: {} seconds".format(elapsed_time(time_start)))
    print("Final board:")
    print_crossword_board(final_board)
    print("Occupancy: {}%".format(occupancy(final_board) * 100))
