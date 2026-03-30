import curses
from pips_logic import Keepout_Rule, Equals_Rule, Unequal_Rule, Sum_Rule, GreaterThan_Rule, LessThan_Rule
from domino_printing import Domino

           
def modify_grid(grid, rule):
    
    if type(rule) is Keepout_Rule:
            
            temp_str = BLOCK_W*"#"

    elif type(rule) is Equals_Rule:

        temp_str = BLOCK_W*"="
    
    elif type(rule) is Unequal_Rule:

        temp_str = "=" + (BLOCK_W//2)*"!="

    elif type(rule) is Sum_Rule:

        temp_str = str(rule.val)
        if len(temp_str) < 2:
            temp_str = "0" + temp_str
        temp_str = 3*("=" + temp_str) 

    elif type(rule) is GreaterThan_Rule:

        temp_str = str(rule.val)
        if len(temp_str) < 2:
            temp_str = "0" + temp_str
        temp_str = 3*(">" + temp_str)
    
    else:

        temp_str = str(rule.val)
        if len(temp_str) < 2:
            temp_str = "0" + temp_str
        temp_str = 3*("<" + temp_str) 
    
    for y in range(GAME_HEIGHT):
            for x in range(GAME_WIDTH):
                if [y, x] in rule.spaces:
                    
                    for i in range(BLOCK_H):
                        grid[(y*BLOCK_H) + i][(x*BLOCK_W): (x+1)*BLOCK_W] = temp_str
        
                 
def draw_grid(stdscr, grid, selection_grid, cursor_x, cursor_y):
    
    stdscr.clear()
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):

            char = grid[y][x]

            # highlight if inside selection block
            if cursor_x <= x < cursor_x + BLOCK_W and cursor_y <= y < cursor_y + BLOCK_H:
                stdscr.addstr(y, x, char, curses.A_REVERSE)
            elif selection_grid[y][x] == True:
                stdscr.addstr(y, x, char, curses.A_REVERSE)
            else:
                stdscr.addstr(y, x, char)

def draw_dominos(stdscr, dominos, selection_grid, cursor_x, cursor_y):

    stdscr.clear()
    for y in range(DOM_GRID_HEIGHT):
        for x in range(DOM_GRID_WIDTH):

            char = dominos[y][x]

            # highlight if inside selection block
            if cursor_x <= x < cursor_x + (2*BLOCK_W) and cursor_y <= y < cursor_y + BLOCK_H:
                stdscr.addstr(y, x, char, curses.A_REVERSE)
            elif selection_grid[y][x] == True:
                stdscr.addstr(y, x, char, curses.A_REVERSE)
            else:
                stdscr.addstr(y, x, char)

    



def UI(stdscr, game_arr):

    curses.curs_set(0)
    stdscr.keypad(True)
    

    grid = [["." for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    selection_grid = [[False for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

    cursor_x = GRID_BORDER_W
    cursor_y = GRID_BORDER_H

    rules = []


    while True:

        draw_grid(stdscr, grid, selection_grid, cursor_x, cursor_y)
        stdscr.addstr(GRID_HEIGHT + 1, 0, "Define the game board area by highlighting, then pressing enter")
        stdscr.addstr(GRID_HEIGHT + 2, 0, "Arrows move | h - highlight | u - unhighlight | return - enter configuration | q - quit")
        stdscr.refresh()

        key = stdscr.getch()

        if key == curses.KEY_RIGHT:
            cursor_x = min(GRID_WIDTH - BLOCK_W - GRID_BORDER_W, cursor_x + BLOCK_W)
            

        elif key == curses.KEY_LEFT:
            cursor_x = max(GRID_BORDER_W, cursor_x - BLOCK_W)
            

        elif key == curses.KEY_UP:
            cursor_y = max(GRID_BORDER_H, cursor_y - BLOCK_H)
            

        elif key == curses.KEY_DOWN:
            cursor_y = min(GRID_HEIGHT - BLOCK_H - GRID_BORDER_H, cursor_y + BLOCK_H)

        elif key == ord("h"):
            for y in range(GRID_HEIGHT):
                for x in range(GRID_WIDTH):
                    
                    if cursor_x <= x < cursor_x + BLOCK_W and cursor_y <= y < cursor_y + BLOCK_H:
                        selection_grid[y][x] = True
        
        elif key == ord("u"):
            for y in range(GRID_HEIGHT):
                for x in range(GRID_WIDTH):
                    
                    if cursor_x <= x < cursor_x + BLOCK_W and cursor_y <= y < cursor_y + BLOCK_H:
                        selection_grid[y][x] = False

        elif key == ord("\n"):
            spaces = []
            mask = []
            for y in range(0, GRID_HEIGHT, BLOCK_H):
                for x in range(0, GRID_WIDTH, BLOCK_W):
                    
                    if selection_grid[y][x] == True:
                        game_arr[y//BLOCK_H][x//BLOCK_W] = None
                        spaces.append([y//BLOCK_H, x//BLOCK_W])
                        
                    else:
                        mask.append([y//BLOCK_H, x//BLOCK_W])
            
            if len(spaces) % 2 != 0:
                raise ValueError("Impossible number of open spaces")

            for y in range(GRID_HEIGHT):
                for x in range(GRID_WIDTH):
                    selection_grid[y][x] = False

            curr_rule = Keepout_Rule(spaces, mask)
            break

        elif key == ord("q"):
            raise SystemExit("User quit")
            
    rules.append(curr_rule)
    modify_grid(grid, curr_rule)
    curr_rule = None

    while True:

        draw_grid(stdscr, grid, selection_grid, cursor_x, cursor_y)
        stdscr.addstr(GRID_HEIGHT + 1, 0, "Enter the rules of the gameboard by selecting an area, then typing in a rule")
        stdscr.addstr(GRID_HEIGHT + 2, 0, "Arrows move | h - highlight | u - unhighlight | | return - enter configuration | q - quit")
        stdscr.addstr(GRID_HEIGHT + 3, 0, "== - All equal | != - Unequal | +XX - Sum to | <XX - Less Than | >XX - Greater Than")
        stdscr.refresh()

        key1 = stdscr.getch()

        if key1 == curses.KEY_RIGHT:
            cursor_x = min(GRID_WIDTH - BLOCK_W - GRID_BORDER_W, cursor_x + BLOCK_W)
            

        elif key1 == curses.KEY_LEFT:
            cursor_x = max(GRID_BORDER_W, cursor_x - BLOCK_W)
            

        elif key1 == curses.KEY_UP:
            cursor_y = max(GRID_BORDER_H, cursor_y - BLOCK_H)
            

        elif key1 == curses.KEY_DOWN:
            cursor_y = min(GRID_HEIGHT - BLOCK_H - GRID_BORDER_H, cursor_y + BLOCK_H)

        elif key1 == ord("h"):
            for y in range(GRID_HEIGHT):
                for x in range(GRID_WIDTH):
                    if cursor_x <= x < cursor_x + BLOCK_W and cursor_y <= y < cursor_y + BLOCK_H:
                        selection_grid[y][x] = True
        
        elif key1 == ord("u"):
            for y in range(GRID_HEIGHT):
                for x in range(GRID_WIDTH):
                    
                    if cursor_x <= x < cursor_x + BLOCK_W and cursor_y <= y < cursor_y + BLOCK_H:
                        selection_grid[y][x] = False

        elif key1 == ord("="):
            key2 = stdscr.getch()
            if key2 == ord("="):
                spaces = []
                for y in range(0, GRID_HEIGHT, BLOCK_H):
                    for x in range(0, GRID_WIDTH, BLOCK_W):
                        
                        if selection_grid[y][x] == True:
                            spaces.append([y//BLOCK_H, x//BLOCK_W])

                for y in range(GRID_HEIGHT):
                    for x in range(GRID_WIDTH):

                        selection_grid[y][x] = False

                curr_rule = Equals_Rule(spaces)
        
        elif key1 == ord("!"):
            key2 = stdscr.getch()
            if key2 == ord("="):
                spaces = []
                for y in range(0, GRID_HEIGHT, BLOCK_H):
                    for x in range(0, GRID_WIDTH, BLOCK_W):
                        
                        if selection_grid[y][x] == True:
                            spaces.append([y//BLOCK_H, x//BLOCK_W])

                for y in range(GRID_HEIGHT):
                    for x in range(GRID_WIDTH):

                        selection_grid[y][x] = False

                curr_rule = Unequal_Rule(spaces)

        elif key1 == ord("+"):
            key2 = stdscr.getch()
            key3 = stdscr.getch()
            # Safely convert to digits (only accept 0-9)
            if 48 <= key2 <= 57 and 48 <= key3 <= 57:
                val = (key2 - 48) * 10 + (key3 - 48)
                spaces = []
                for y in range(0, GRID_HEIGHT, BLOCK_H):
                    for x in range(0, GRID_WIDTH, BLOCK_W):
                        
                        if selection_grid[y][x] == True:
                            spaces.append([y//BLOCK_H, x//BLOCK_W])

                for y in range(GRID_HEIGHT):
                    for x in range(GRID_WIDTH):

                        selection_grid[y][x] = False

                curr_rule = Sum_Rule(spaces, val)

        
        elif key1 == ord(">"):
            key2 = stdscr.getch()
            key3 = stdscr.getch()
            # Safely convert to digits (only accept 0-9)
            if 48 <= key2 <= 57 and 48 <= key3 <= 57:
                val = (key2 - 48) * 10 + (key3 - 48)
                spaces = []
                for y in range(0, GRID_HEIGHT, BLOCK_H):
                    for x in range(0, GRID_WIDTH, BLOCK_W):
                        
                        if selection_grid[y][x] == True:
                            spaces.append([y//BLOCK_H, x//BLOCK_W])

                for y in range(GRID_HEIGHT):
                    for x in range(GRID_WIDTH):

                        selection_grid[y][x] = False

                curr_rule = GreaterThan_Rule(spaces, val)

            
        elif key1 == ord("<"):
            key2 = stdscr.getch()
            key3 = stdscr.getch()
            # Safely convert to digits (only accept 0-9)
            if 48 <= key2 <= 57 and 48 <= key3 <= 57:
                val = (key2 - 48) * 10 + (key3 - 48)
                spaces = []
                for y in range(0, GRID_HEIGHT, BLOCK_H):
                    for x in range(0, GRID_WIDTH, BLOCK_W):
                        
                        if selection_grid[y][x] == True:
                            spaces.append([y//BLOCK_H, x//BLOCK_W])

                for y in range(GRID_HEIGHT):
                    for x in range(GRID_WIDTH):

                        selection_grid[y][x] = False

                curr_rule = LessThan_Rule(spaces, val)

        elif key1 == ord("\n"):
            break

        elif key1 == ord("q"):
            raise SystemExit("User quit")
        
        if curr_rule != None:
            rules.append(curr_rule)
            modify_grid(grid, curr_rule)
            curr_rule = None
        
    dominos =  [",----------------, ,----------------, ,----------------, ,----------------, ,----------------, ,----------------, ,----------------,",
                "|       |        | |       |        | |       |  .     | |       |  .     | |       |  .   . | |       |  .   . | |       |  . . . |",
                "|       |        | |       |    .   | |       |        | |       |    .   | |       |        | |       |    .   | |       |        |",
                "|       |        | |       |        | |       |      . | |       |      . | |       |  .   . | |       |  .   . | |       |  . . . |",
                "'----------------' '----------------' '----------------' '----------------' '----------------' '----------------' '----------------'",
                ",----------------, ,----------------, ,----------------, ,----------------, ,----------------, ,----------------, ,----------------,",
                "|       |        | |       |        | |       |  .     | |       |  .     | |       |  .   . | |       |  .   . | |       |  . . . |",
                "|   .   |        | |   .   |    .   | |   .   |        | |   .   |    .   | |   .   |        | |   .   |    .   | |   .   |        |",
                "|       |        | |       |        | |       |      . | |       |      . | |       |  .   . | |       |  .   . | |       |  . . . |",
                "'----------------' '----------------' '----------------' '----------------' '----------------' '----------------' '----------------'",
                ",----------------, ,----------------, ,----------------, ,----------------, ,----------------, ,----------------, ,----------------,",
                "| .     |        | | .     |        | | .     |  .     | | .     |  .     | | .     |  .   . | | .     |  .   . | | .     |  . . . |",
                "|       |        | |       |    .   | |       |        | |       |    .   | |       |        | |       |    .   | |       |        |",
                "|     . |        | |     . |        | |     . |      . | |     . |      . | |     . |  .   . | |     . |  .   . | |     . |  . . . |",
                "'----------------' '----------------' '----------------' '----------------' '----------------' '----------------' '----------------'",
                ",----------------, ,----------------, ,----------------, ,----------------, ,----------------, ,----------------, ,----------------,",
                "| .     |        | | .     |        | | .     |  .     | | .     |  .     | | .     |  .   . | | .     |  .   . | | .     |  . . . |",
                "|   .   |        | |   .   |    .   | |   .   |        | |   .   |    .   | |   .   |        | |   .   |    .   | |   .   |        |",
                "|     . |        | |     . |        | |     . |      . | |     . |      . | |     . |  .   . | |     . |  .   . | |     . |  . . . |",
                "'----------------' '----------------' '----------------' '----------------' '----------------' '----------------' '----------------'",
                ",----------------, ,----------------, ,----------------, ,----------------, ,----------------, ,----------------, ,----------------,",
                "| .   . |        | | .   . |        | | .   . |  .     | | .   . |  .     | | .   . |  .   . | | .   . |  .   . | | .   . |  . . . |",
                "|       |        | |       |    .   | |       |        | |       |    .   | |       |        | |       |    .   | |       |        |",
                "| .   . |        | | .   . |        | | .   . |      . | | .   . |      . | | .   . |  .   . | | .   . |  .   . | | .   . |  . . . |",
                "'----------------' '----------------' '----------------' '----------------' '----------------' '----------------' '----------------'",
                ",----------------, ,----------------, ,----------------, ,----------------, ,----------------, ,----------------, ,----------------,",
                "| .   . |        | | .   . |        | | .   . |  .     | | .   . |  .     | | .   . |  .   . | | .   . |  .   . | | .   . |  . . . |",
                "|   .   |        | |   .   |    .   | |   .   |        | |   .   |    .   | |   .   |        | |   .   |    .   | |   .   |        |",
                "| .   . |        | | .   . |        | | .   . |      . | | .   . |      . | | .   . |  .   . | | .   . |  .   . | | .   . |  . . . |",
                "'----------------' '----------------' '----------------' '----------------' '----------------' '----------------' '----------------'",
                ",----------------, ,----------------, ,----------------, ,----------------, ,----------------, ,----------------, ,----------------,",
                "| . . . |        | | . . . |        | | . . . |  .     | | . . . |  .     | | . . . |  .   . | | . . . |  .   . | | . . . |  . . . |",
                "|       |        | |       |    .   | |       |        | |       |    .   | |       |        | |       |    .   | |       |        |",
                "| . . . |        | | . . . |        | | . . . |      . | | . . . |      . | | . . . |  .   . | | . . . |  .   . | | . . . |  . . . |",
                "'----------------' '----------------' '----------------' '----------------' '----------------' '----------------' '----------------'"]

    domino_list = []    

    selection_grid = [[False for _ in range(DOM_GRID_WIDTH)] for _ in range(DOM_GRID_HEIGHT)]

    cursor_x = 0
    cursor_y = 0

        
    while True:
        draw_dominos(stdscr, dominos, selection_grid, cursor_x, cursor_y)
        stdscr.addstr(DOM_GRID_HEIGHT + 1, 0, "Enter your dominos by highlighting, then pressing a to add")
        stdscr.addstr(DOM_GRID_HEIGHT + 2, 0, "Arrows move | h - highlight | u - unhighlight | | return - enter configuration | q - quit")
        stdscr.addstr(DOM_GRID_HEIGHT + 3, 0, "a - Add domino")
        stdscr.addstr(DOM_GRID_HEIGHT + 4, 0, f"Dominos added: {len(domino_list)}")
        stdscr.refresh()
        
        key1 = stdscr.getch()

        if key1 == curses.KEY_RIGHT:
            cursor_x = min(DOM_GRID_WIDTH - (2*BLOCK_W), cursor_x + (2*BLOCK_W) + 1)
            

        elif key1 == curses.KEY_LEFT:
            cursor_x = max(0, cursor_x - (2*BLOCK_W) - 1)
            

        elif key1 == curses.KEY_UP:
            cursor_y = max(0, cursor_y - BLOCK_H)
            

        elif key1 == curses.KEY_DOWN:
            cursor_y = min(DOM_GRID_HEIGHT - BLOCK_H, cursor_y + BLOCK_H)

        elif key1 == ord("h"):
            for y in range(DOM_GRID_HEIGHT):
                for x in range(DOM_GRID_WIDTH):
                    if cursor_x <= x < cursor_x + (BLOCK_W*2) and cursor_y <= y < cursor_y + BLOCK_H:
                        selection_grid[y][x] = True
        
        elif key1 == ord("u"):
            for y in range(DOM_GRID_HEIGHT):
                for x in range(DOM_GRID_WIDTH):
                    
                    if cursor_x <= x < cursor_x + (BLOCK_W*2) and cursor_y <= y < cursor_y + BLOCK_H:
                        selection_grid[y][x] = False

        elif key1 == ord("a"):
            for i in range(DOM_HEIGHT):
                for j in range(DOM_WIDTH):
                
                    if selection_grid[i*BLOCK_H][j*(2*BLOCK_W + 1)] == True:
                        domino_list.append(Domino(i, j, False))
            
            for y in range(DOM_GRID_HEIGHT):
                for x in range(DOM_GRID_WIDTH):
                    
                    selection_grid[y][x] = False
        
        elif key1 == ord("\n"):
            if len(domino_list) == (len(rules[0].spaces)//2):
                break
            else:
                raise ValueError("Number of dominos does not match the number of spaces on the board")

        elif key1 == ord("q"):
            raise SystemExit("User quit")
        
    return rules, domino_list

BLOCK_W = 9
BLOCK_H = 5

GAME_BORDER_W = 1
GAME_BORDER_H = 1

GRID_BORDER_W = GAME_BORDER_W*BLOCK_W
GRID_BORDER_H = GAME_BORDER_H*BLOCK_H

GAME_WIDTH = 6
GAME_HEIGHT = 6

GRID_WIDTH = GAME_WIDTH*BLOCK_W
GRID_HEIGHT = GAME_HEIGHT*BLOCK_H

DOM_WIDTH = 7
DOM_HEIGHT = 7

DOM_GRID_WIDTH = DOM_WIDTH*(2*BLOCK_W + 1) - 1
DOM_GRID_HEIGHT = DOM_HEIGHT*BLOCK_H

game_arr = [[7 for _ in range(GAME_WIDTH)] for _ in range(GAME_HEIGHT)]

try:
    game_rules, game_pieces = curses.wrapper(UI, game_arr)
except ValueError as e:
    print(f"Error: {e}")
except SystemExit as e:
    print(f"Game over: {e}")