from js import document, alert
import copy
import random
import time
import re

TIME_LIMIT_SECONDS = 1

init = document.getElementById("init")
input = document.getElementById("input")
init.innerHTML = "Enter the desired columns and rows!"
input.style.display = ""
wordlist = document.getElementById("word-list").value
table = document.getElementById("tableContainer")


def generate():
    table.innerHTML = ""

    totalRow = document.getElementById("totalRow").value
    totalColumn = document.getElementById("totalColumn").value

    board = generator(int(totalRow), int(totalColumn))

    newtable = '<table>'
    for i in range(len(board)):
        newtable += '<tr>'
        for j in range(len(board[i])):
            cell_value = board[i][j]
            cell_class = "black" if cell_value == "#" else "white"
            newtable += '<td class="' + cell_class + '" style="width:50px;height:50px;" onclick="togglecell(this)">' + cell_value + '</td>'
        newtable += '</tr>'
    newtable += '</table>'
    table.innerHTML = newtable


def solve():
    assignment = {}
    boardstr = html_table_to_list(table.innerHTML)
    words = wordlist.splitlines()
    words = [word.upper() for word in words]

    V = create_variables(boardstr, words)
    S = create_arc(V)

    arc_consistency_3(S)

    V.sort(key=lambda x: len(x.domain))

    backtrack(V, assignment)

    if len(assignment) != len(V):
        alert("No solution found!")
        return

    boardstr = get_final_board(boardstr, assignment)

    newtable = '<table>'
    for i in range(len(boardstr)):
        newtable += '<tr>'
        for j in range(len(boardstr[i])):
            cell_value = boardstr[i][j]
            cell_class = "black" if cell_value == "#" else "white"
            newtable += f'<td class="{cell_class}" style="width:50px;height:50px;" onclick="togglecell(this)">{cell_value}</td>'
        newtable += '</tr>'
    newtable += '</table>'
    table.innerHTML = newtable


class Variable:
    def __init__(self, direction, row, col, length, domain):
        self.word = ""
        self.direction = direction
        self.row = row
        self.col = col
        self.length = length
        self.domain = domain
        self.removed_domain = {}


def html_table_to_list(table_html):
    # Extract rows using regular expression
    rows_match = re.findall(r'<tr>(.*?)</tr>', table_html, re.DOTALL)

    # Extract data from each row
    table_data = ""
    for i in range(len(rows_match)):
        cols_match = re.findall(r'<td(?:\s+.*?)?>(.*?)</td>', rows_match[i], re.DOTALL)
        for col_match in cols_match:
            table_data += col_match
        if i != len(rows_match) - 1:
            table_data += "\n"

    return table_data


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


def elapsed_time(start_time):
    return time.time() - start_time


def select_unassigned_variable(V, assignment):
    unassigned = []
    for v in V:
        if v not in assignment:
            unassigned.append(v)

    unassigned.sort(key=lambda x: len(x.domain))
    return unassigned[0]


def satisfy_constraint(V, assignment, Vx, val):
    for v in V:
        Cxv = create_constraint(Vx, v)
        if v != Vx and v in assignment and Cxv:
            if val[Cxv[0]] != assignment[v][Cxv[1]]:
                return False
    return True


def backtrack_gen(V, assignment, start_time):
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
            result = backtrack_gen(V, assignment, start_time)
            if result:
                return True
        assignment.pop(Vx, None)
    return False


def reduce_domain(V, assignment, Vx, val):
    for v in V:
        Cxv = create_constraint(Vx, v)
        if v != Vx and v not in assignment and Cxv:
            for word in v.domain:
                if val[Cxv[0]] != word[Cxv[1]]:
                    v.domain.remove(word)
                    if v not in Vx.removed_domain:
                        Vx.removed_domain[v] = []
                    Vx.removed_domain[v].append(word)


def restore_domain(V, assignment, Vx, val):
    for v in V:
        Cxv = create_constraint(Vx, v)
        if v != Vx and v not in assignment and Cxv:
            if v in Vx.removed_domain:
                for word in Vx.removed_domain[v]:
                    if val[Cxv[0]] != word[Cxv[1]]:
                        v.domain.append(word)
                        Vx.removed_domain[v].remove(word)


def backtrack(V, assignment):
    if len(assignment) == len(V):
        return True
    Vx = select_unassigned_variable(V, assignment)
    for val in Vx.domain:
        if val in assignment.values():
            continue
        if satisfy_constraint(V, assignment, Vx, val):
            assignment[Vx] = val
            reduce_domain(V, assignment, Vx, val)
            result = backtrack(V, assignment)
            if result:
                return True
        assignment.pop(Vx, None)
        restore_domain(V, assignment, Vx, val)
    return False


def revise(Vx, Vy, Cxy):
    if not Cxy:
        return False
    revised = False
    for x in Vx.domain:
        satisfied = False
        for y in Vy.domain:
            if x[Cxy[0]] == y[Cxy[1]]:
                satisfied = True
                break
            if satisfied:
                break
        if not satisfied:
            Vx.domain.remove(x)
            revised = True
    return revised


def arc_consistency_3(S):
    for s in S:
        X, Y, Cxy = s
        revise(X, Y, Cxy)


def create_constraint(Vx, Vy):
    constraint = ()
    if Vx.direction != Vy.direction:
        if Vx.direction == "horizontal":
            if Vy.col >= Vx.col and Vy.col <= Vx.col + Vx.length - 1:
                if Vx.row >= Vy.row and Vx.row <= Vy.row + Vy.length - 1:
                    constraint = (Vy.col - Vx.col, Vx.row - Vy.row)
        else:
            if Vy.row >= Vx.row and Vy.row <= Vx.row + Vx.length - 1:
                if Vx.col >= Vy.col and Vx.col <= Vy.col + Vy.length - 1:
                    constraint = (Vy.row - Vx.row, Vx.col - Vy.col)
    return constraint


def create_arc(V):
    arcs = []
    for i in range(len(V)):
        for j in range(i + 1, len(V)):
            if i != j:
                Cij = create_constraint(V[i], V[j])
                if len(Cij) > 0:
                    arcs.append((V[i], V[j], Cij))
    return arcs


def create_variables(boardstr, words):
    variables = []
    board = boardstr.split("\n")
    for row in range(len(board)):
        for col in range(len(board[row])):
            if board[row][col] != "#":
                if col == 0 or board[row][col - 1] == "#":
                    length = 0
                    for i in range(col, len(board[row])):
                        if board[row][i] != "#":
                            length += 1
                        else:
                            break
                    if length == 1:
                        cond = True
                        try:
                            if board[row][col + 1] != "#":
                                cond = False
                        except IndexError:
                            pass
                        try:
                            if board[row][col - 1] != "#" and col - 1 >= 0:
                                cond = False
                        except IndexError:
                            pass
                        try:
                            if board[row - 1][col] != "#" and row - 1 >= 0:
                                cond = False
                        except IndexError:
                            pass
                        try:
                            if board[row + 1][col] != "#":
                                cond = False
                        except IndexError:
                            pass
                        if cond:
                            domain = []
                            for word in words:
                                if len(word) == length:
                                    domain.append(word)
                            variables.append(Variable(
                                "horizontal",
                                row,
                                col,
                                length,
                                domain
                            ))

                    if length > 1:
                        domain = []
                        for word in words:
                            if len(word) == length:
                                domain.append(word)
                        variables.append(Variable(
                            "horizontal",
                            row,
                            col,
                            length,
                            domain
                        ))
                if row == 0 or board[row - 1][col] == "#":
                    length = 0
                    for i in range(row, len(board)):
                        if board[i][col] != "#":
                            length += 1
                        else:
                            break
                    if length > 1:
                        domain = []
                        for word in words:
                            if len(word) == length:
                                domain.append(word)
                        variables.append(Variable(
                            "vertical",
                            row,
                            col,
                            length,
                            domain
                        ))
    return variables


def get_temp_board(board):
    temp_board = ""
    for i, row in enumerate(board):
        if i == len(board) - 1:
            temp_board += ''.join(row)
        else:
            temp_board += ''.join(row) + "\n"
    return temp_board


def is_solveable(board, words):
    assignment = {}
    boardstr = get_temp_board(board)
    V = create_variables(boardstr, words)
    S = create_arc(V)

    arc_consistency_3(S)

    V.sort(key=lambda x: len(x.domain))

    start_time = time.time()
    result = backtrack_gen(V, assignment, start_time)

    if result:
        boardstr = get_final_board(boardstr, assignment)
        for row in boardstr:
            if '-' in row:
                return False
        return True
    else:
        return False


def place_word_horizontally(board, length, i, j):
    for k in range(length):
        board[i][j+k] = '-'


def place_word_vertically(board, length, i, j):
    for k in range(length):
        board[i+k][j] = '-'


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


def generate_crossword_board(height, width):
    board = [['#' for _ in range(width)] for _ in range(height)]
    return board


def add_word_to_board(board, length, position):
    max_attempts = 10
    direction = "horizontal" if position % 2 == 0 else "vertical"

    for _ in range(max_attempts):
        i, j = random.choice([(x, y) for x in range(len(board)) for y in range(len(board[0]) - length + 1)]
                             ) if direction == "horizontal" else random.choice([(x, y) for x in range(len(board) - length + 1) for y in range(len(board[0]))])

        if is_valid_placement(board, length, i, j, direction):
            if direction == "horizontal":
                place_word_horizontally(board, length, i, j)
            else:
                place_word_vertically(board, length, i, j)
            break


def generator(height, width):
    print("Generating board...")
    max_attempts = 10

    # #if board height and width is less than 3, then give a board with all -'s
    if height <= 3 and width <= 3:
        board = [['-' for _ in range(width)] for _ in range(height)]
        return board
    
    testing_board = generate_crossword_board(height, width)

    while True:
        word_length = random.randint(1, min(height, width))
        print("Trying to add a word...")
        choice = random.randint(1, 2)  # vertical or horizontal
        final_board = copy.deepcopy(testing_board)
        add_word_to_board(testing_board, word_length, choice)

        if not is_solveable(testing_board, wordlist.splitlines()):
            # try adding the word for 10 times
            for _ in range(max_attempts):
                testing_board = copy.deepcopy(final_board)
                add_word_to_board(testing_board, word_length, choice)
                if is_solveable(testing_board, wordlist.splitlines()):
                    break
            else:
                # Save the board and break the loop if not solveable after 5 attempts
                break

    return final_board
