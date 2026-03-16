import curses
from pips_logic import Keepout_Rule, Equals_Rule, Sum_Rule, GreaterThan_Rule, LessThan_Rule
import copy





def modify_grid(grid, rules):
    print("Imhere")
    # new_grid = copy.deepcopy(grid)
    for rule in rules:
        if type(rule) is Keepout_Rule:
            
            for y in range(GAME_HEIGHT):
                for x in range(GAME_WIDTH):
                    if [y, x] not in rule.mask:
                        
                        for i in range(BLOCK_H):
                            for j in range(BLOCK_W):
                                grid[(y*BLOCK_H) + i][(x*BLOCK_W) + j] = "#"

        elif type(rule) is Equals_Rule:

            for y in range(GAME_HEIGHT):
                for x in range(GAME_WIDTH):
                    if [y, x] in rule.spaces:
                        
                        for i in range(BLOCK_H):
                            for j in range(BLOCK_W):
                                grid[(y*BLOCK_H) + i][(x*BLOCK_W) + j] = "="

        elif type(rule) is Sum_Rule:

            val_as_str = str(rule.val)
            if len(val_as_str) < 2:
                val_as_str = "0" + val_as_str
            val_as_str = "=" + 3*(val_as_str + "=") 
            for y in range(GAME_HEIGHT):
                for x in range(GAME_WIDTH):
                    if [y, x] in rule.spaces:
                        
                        for i in range(BLOCK_H):
                            for j in range(BLOCK_W):
                                grid[(y*BLOCK_H) + i][(x*BLOCK_W) + j] = val_as_str[j]

        elif type(rule) is GreaterThan_Rule:

            val_as_str = str(rule.val)
            if len(val_as_str) < 2:
                val_as_str = "0" + val_as_str
            val_as_str = ">" + 3*(val_as_str + ">") 
            for y in range(GAME_HEIGHT):
                for x in range(GAME_WIDTH):
                    if [y, x] in rule.spaces:
                        
                        for i in range(BLOCK_H):
                            for j in range(BLOCK_W):
                                grid[(y*BLOCK_H) + i][(x*BLOCK_W) + j] = val_as_str[j]
        
        else:

            val_as_str = str(rule.val)
            if len(val_as_str) < 2:
                val_as_str = "0" + val_as_str
            val_as_str = "<" + 3*(val_as_str + "<") 
            for y in range(GAME_HEIGHT):
                for x in range(GAME_WIDTH):
                    if [y, x] in rule.spaces:
                        
                        for i in range(BLOCK_H):
                            for j in range(BLOCK_W):
                                grid[(y*BLOCK_H) + i][(x*BLOCK_W) + j] = val_as_str[j]



                    




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
        stdscr.addstr(GRID_HEIGHT + 1, 0, "Arrows move | h highlight | u unhighlight | return enter configuration | q quit")
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
            mask = []

            for y in range(0, GRID_HEIGHT, BLOCK_H):
                for x in range(0, GRID_WIDTH, BLOCK_W):
                    
                    if selection_grid[y][x] == False:
                        game_arr[y//BLOCK_H][x//BLOCK_W] = 7
                        mask.append([y//BLOCK_H, x//BLOCK_W])

            for y in range(GRID_HEIGHT):
                for x in range(GRID_WIDTH):

                    selection_grid[y][x] = False
            
            border = Keepout_Rule(mask)
            rules.append(border)
            break

        elif key == ord("q"):
            return "User Quit"
            
    modify_grid(grid, rules)
    
    while True:

        draw_grid(stdscr, grid, selection_grid, cursor_x, cursor_y)
        stdscr.addstr(GRID_HEIGHT + 1, 0, "Arrows move | ^ Add rule | == All equal | +XX Sum to | <XX Less Than | >XX Greater Than | return enter configuration | q quit")
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

                rules.append(Equals_Rule(spaces))
                modify_grid(grid, rules)

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

                rules.append(Sum_Rule(spaces, val))
                modify_grid(grid, rules)

        
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

                rules.append(GreaterThan_Rule(spaces, val))
                modify_grid(grid, rules)

            
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

                rules.append(LessThan_Rule(spaces, val))
                modify_grid(grid, rules)

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

        elif key1 == ord("\n"):
            return rules

        elif key1 == ord("q"):
            return "User Quit"
        

        


BLOCK_W = 10
BLOCK_H = 5

GAME_BORDER_W = 1
GAME_BORDER_H = 1

GRID_BORDER_W = GAME_BORDER_W*BLOCK_W
GRID_BORDER_H = GAME_BORDER_H*BLOCK_H

GAME_WIDTH = 6
GAME_HEIGHT = 6

GRID_WIDTH = GAME_WIDTH*BLOCK_W
GRID_HEIGHT = GAME_HEIGHT*BLOCK_H

game_arr = [[None for _ in range(GAME_WIDTH)] for _ in range(GAME_HEIGHT)]

curses.wrapper(UI, game_arr)