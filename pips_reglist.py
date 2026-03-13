import random

nil        = "........."
blank      = "|       |"
dot_l      = "| .     |"
dot_m      = "|   .   |"
dot_r      = "|     . |"
dots2      = "| .   . |"
dots3      = "| . . . |"
v_top      = ",-------," 
v_middle   = "|_______|"
v_bottom   = "'-------'"
h_top_l    = ",--------"
h_top_r    = "--------,"
h_bottom_l = "'--------"
h_bottom_r = "--------'"

vertical_numbers = [[blank, blank, blank],
                    [blank, dot_m, blank],
                    [dot_r, blank, dot_l],
                    [dot_r, dot_m, dot_l],
                    [dots2, blank, dots2],
                    [dots2, dot_m, dots2],
                    [dots2, dots2, dots2]]

horizontal_numbers = [[blank, blank, blank],
                      [blank, dot_m, blank],
                      [dot_l, blank, dot_r],
                      [dot_l, dot_m, dot_r],
                      [dots2, blank, dots2],
                      [dots2, dot_m, dots2],
                      [dots3, blank, dots3]]


class PipPlace:
    def __init__(self, num_pips=None, orientation=None):
        
        self.num_pips = num_pips
        self.orientation = orientation

class Domino:
    def __init__(self, p1=None, p2=None, vertical=None):
        
        if p1 is None:
            self.p1 = random.randint(0, 6)
        else:
            self.p1 = p1
        if p2 is None:
            self.p2 = random.randint(0, 6)
        else:
            self.p2 = p2

        if vertical is None:
            self.vertical = random.choice([True, False])
        else:
            self.vertical = vertical

class PipGrid:
    def __init__(self, width, height):
        self.grid = [[PipPlace() for _ in range(width)] for _ in range(height)]
        self.width = width
        self.height = height

    def add_domino(self, x, y, domino=None):
        if domino is None:
            domino = Domino()
        else:
            domino = domino
        if domino.vertical:
            if y + 1 < self.height:
                self.grid[y][x].num_pips = domino.p1
                self.grid[y][x].orientation = "D"
                self.grid[y + 1][x].num_pips = domino.p2
                self.grid[y + 1][x].orientation = "U"
            else:
                raise ValueError("Domino does not fit vertically at this position.")
        else:
            if x + 1 < self.width:
                self.grid[y][x].num_pips = domino.p1
                self.grid[y][x].orientation = "R"
                self.grid[y][x + 1].num_pips = domino.p2
                self.grid[y][x + 1].orientation = "L"
            else:
                raise ValueError("Domino does not fit horizontally at this position.")
    
    def print_grid(self):
        screen = [""]*self.height*5
        for i in range(self.height):
            for j in range(self.width):
                offset = i*5
                if self.grid[i][j].orientation == None:
                    for k in range(5):
                        screen[offset + k] += nil

                elif self.grid[i][j].orientation == "D":
                    screen[offset] += v_top
                    offset += 1
                    for k in range(3):
                        screen[offset + k] += vertical_numbers[self.grid[i][j].num_pips][k]
                    offset += 3
                    screen[offset] += v_middle

                elif self.grid[i][j].orientation == "U":
                    screen[offset] += blank
                    offset += 1
                    for k in range(3):
                        screen[offset + k] += vertical_numbers[self.grid[i][j].num_pips][k]
                    offset += 3
                    screen[offset] += v_bottom

                elif self.grid[i][j].orientation == "R":
                    screen[offset] += h_top_l
                    offset += 1
                    for k in range(3):
                        screen[offset + k] += horizontal_numbers[self.grid[i][j].num_pips][k][:8] + "|"
                    offset += 3
                    screen[offset] += h_bottom_l

                else:
                    screen[offset] += h_top_r
                    offset += 1
                    for k in range(3):
                        screen[offset + k] += " " + horizontal_numbers[self.grid[i][j].num_pips][k][1:]
                    offset += 3
                    screen[offset] += h_bottom_r
        for line in screen:
            print(line)   
        
    def print_grid_debug(self):
        for row in self.grid:
            print([f"{cell.num_pips}({cell.orientation})" for cell in row])




new_game = PipGrid(3, 3)
new_game.add_domino(2, 0, Domino(3, 5, True))
new_game.add_domino(1, 0, Domino(2, 6, True))
new_game.add_domino(0, 2, Domino(1, 6, False))
new_game.print_grid()