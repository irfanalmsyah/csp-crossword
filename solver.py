class Variable:
    def __init__(self, direction, row, col, length, domain):
        self.word = ""
        self.direction = direction
        self.row = row
        self.col = col
        self.length = length
        self.domain = set(domain)
        self.removed_domain = {}


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
        Cxv = create_constraint(Vx, v)
        if v != Vx and v in assignment and Cxv:
            if val[Cxv[0]] != assignment[v][Cxv[1]]:
                return False
    return True


def select_unassigned_variable(V, assignment):
    unassigned = []
    for v in V:
        if v not in assignment:
            unassigned.append(v)

    unassigned.sort(key=lambda x: len(x.domain))
    return unassigned[0]


def reduce_domain(V, assignment, Vx, val):
    for v in V:
        Cxv = create_constraint(Vx, v)
        if v != Vx and v not in assignment and Cxv:
            elements_to_remove = set()
            for word in v.domain:
                if val[Cxv[0]] != word[Cxv[1]]:
                    elements_to_remove.add(word)
            v.domain.difference_update(elements_to_remove)
            if v not in Vx.removed_domain:
                Vx.removed_domain[v] = []
            Vx.removed_domain[v].extend(elements_to_remove)


def restore_domain(V, assignment, Vx, val):
    for v in V:
        Cxv = create_constraint(Vx, v)
        if v != Vx and v not in assignment and Cxv:
            if v in Vx.removed_domain:
                for word in Vx.removed_domain[v]:
                    if val[Cxv[0]] != word[Cxv[1]]:
                        v.domain.add(word)
                Vx.removed_domain[v] = []


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
    elements_to_remove = set()

    for x in Vx.domain:
        satisfied = False
        for y in Vy.domain:
            if x[Cxy[0]] == y[Cxy[1]]:
                satisfied = True
                break
        if not satisfied:
            elements_to_remove.add(x)
            revised = True

    Vx.domain.difference_update(elements_to_remove)
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
            if board[row][col] == "-":
                if col == 0 or board[row][col - 1] == "#":
                    length = 0
                    for i in range(col, len(board[row])):
                        if board[row][i] == "-":
                            length += 1
                        else:
                            break
                    if length == 1:
                        cond = True
                        try:
                            if board[row][col + 1] == "-":
                                cond = False
                        except IndexError:
                            pass
                        try:
                            if board[row][col - 1] == "-" and col - 1 >= 0:
                                cond = False
                        except IndexError:
                            pass
                        try:
                            if board[row - 1][col] == "-" and row - 1 >= 0:
                                cond = False
                        except IndexError:
                            pass
                        try:
                            if board[row + 1][col] == "-":
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
    words = [word.upper() for word in words]

    V = create_variables(boardstr, words)
    S = create_arc(V)

    arc_consistency_3(S)

    V.sort(key=lambda x: len(x.domain))

    backtrack(V, assignment)

    print_board(boardstr, assignment)


if __name__ == "__main__":
    main()
