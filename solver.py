class Variable:
    def __init__(self, direction, row, col, length, domain):
        self.word = ""
        self.direction = direction
        self.row = row
        self.col = col
        self.length = length
        self.domain = domain


def print_board(boardstr, assignment):
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
        print(row)


def satisfy_constraint(V, assignment, Vx, val):
    for v in V:
        if v != Vx and v in assignment:
            Cxv = create_constraint(Vx, v)
            for constraint in Cxv:
                if val[constraint[0]] != assignment[v][constraint[1]]:
                    return False
    return True


def select_unassigned_variable(V, assignment):
    return next(v for v in V if v not in assignment)


def backtrack(V, assignment):
    if len(assignment) == len(V):
        return True
    Vx = select_unassigned_variable(V, assignment)
    for val in Vx.domain:
        if val in assignment.values():
            continue
        if satisfy_constraint(V, assignment, Vx, val):
            assignment[Vx] = val
            result = backtrack(V, assignment)
            if result:
                return True
        assignment.pop(Vx, None)
    return False


def revise(Vx, Vy, Cxy):
    if len(Cxy) == 0:
        return False
    revised = False
    for x in Vx.domain:
        satisfied = False
        for y in Vy.domain:
            for constraint in Cxy:
                if x[constraint[0]] == y[constraint[1]]:
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
    constraints = []
    if Vx.direction != Vy.direction:
        if Vx.direction == "horizontal":
            if Vy.col >= Vx.col and Vy.col <= Vx.col + Vx.length:
                if Vx.row >= Vy.row and Vx.row <= Vy.row + Vy.length:
                    constraint = (Vy.col - Vx.col, Vx.row - Vy.row)
                    constraints.append(constraint)
        else:
            if Vy.row >= Vx.row and Vy.row <= Vx.row + Vx.length:
                if Vx.col >= Vy.col and Vx.col <= Vy.col + Vy.length:
                    constraint = (Vy.row - Vx.row, Vx.col - Vy.col)
                    constraints.append(constraint)

    return constraints


def create_arc(V):
    arcs = []
    for i in range(len(V)):
        for j in range(len(V)):
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
            if board[row][col] == "-":
                if col == 0 or board[row][col - 1] == "#":
                    length = 0
                    for i in range(col, len(board[row])):
                        if board[row][i] == "-":
                            length += 1
                        else:
                            break
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
                        if board[i][col] == "-":
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


def read_file(file_path):
    with open(file_path) as file:
        return file.read()


def main():
    assignment = {}
    boardstr = read_file("crossword.txt")
    words = read_file("words.txt").splitlines()
    V = create_variables(boardstr, words)
    S = create_arc(V)

    arc_consistency_3(S)

    V.sort(key=lambda x: len(x.domain))

    backtrack(V, assignment)

    print_board(boardstr, assignment)


if __name__ == "__main__":
    main()
