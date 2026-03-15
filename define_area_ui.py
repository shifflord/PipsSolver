import curses
import copy





def modify_grid(grid, selection_grid, viewing_grid, cursor_x, cursor_y, char):
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):

            # Change if inside selection block
            if cursor_x <= x < cursor_x + BLOCK_W and cursor_y <= y < cursor_y + BLOCK_H:
                grid[y][x] = char
                viewing_grid[y][x] = char
            if selection_grid[y][x] == True:
                grid[y][x] = char
                viewing_grid[y][x] = char
                selection_grid[y][x] = False
    
    # for y in range(GRID_HEIGHT - 1):
    #     for x in range(GRID_WIDTH - 1):

    #         # Vertical edge
    #         if grid[y][x] != grid[y][x + 1]:

    #             if grid[y][x] == ".":
    #                 viewing_grid[y][x] = "|"
    #             else:
    #                 viewing_grid[y][x+1] = "|"

    #         # Horizontal edge
    #         if grid[y][x] != grid[y + 1][x]:
                
    #             if grid[y][x] == ".":
    #                 viewing_grid[y][x] = "-"
    #             else:
    #                 viewing_grid[y+1][x] = "-"

    #         # No edges
    #         else:

    #             #
    #             viewing_grid[y][x + 1] = grid[y][x + 1]
    #             viewing_grid[y + 1][x] = grid[y + 1][x]


                    




def draw_grid(stdscr, viewing_grid, selection_grid, cursor_x, cursor_y):
    stdscr.clear()

    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):

            char = viewing_grid[y][x]

            # highlight if inside selection block
            if cursor_x <= x < cursor_x + BLOCK_W and cursor_y <= y < cursor_y + BLOCK_H:
                stdscr.addstr(y, x, char, curses.A_REVERSE)
            elif selection_grid[y][x] == True:
                stdscr.addstr(y, x, char, curses.A_REVERSE)
            else:
                stdscr.addstr(y, x, char)

    stdscr.addstr(GRID_HEIGHT + 1, 0, "Arrows move | # Valid area | . empty | h highlight | u unhighlight | return enter configuration | q quit")
    stdscr.refresh()



def GetKeepoutMask(stdscr, game_arr):

    

    curses.curs_set(0)
    stdscr.keypad(True)
    

    grid = [["." for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    selection_grid = [[False for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    viewing_grid = [["." for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

    cursor_x = GRID_BORDER_W
    cursor_y = GRID_BORDER_H


    while True:

        draw_grid(stdscr, viewing_grid, selection_grid, cursor_x, cursor_y)

        key = stdscr.getch()

        if key == curses.KEY_RIGHT:
            cursor_x = min(GRID_WIDTH - BLOCK_W - GRID_BORDER_W, cursor_x + BLOCK_W)
            

        elif key == curses.KEY_LEFT:
            cursor_x = max(GRID_BORDER_W, cursor_x - BLOCK_W)
            

        elif key == curses.KEY_UP:
            cursor_y = max(GRID_BORDER_H, cursor_y - BLOCK_H)
            

        elif key == curses.KEY_DOWN:
            cursor_y = min(GRID_HEIGHT - BLOCK_H - GRID_BORDER_H, cursor_y + BLOCK_H)

        elif key == ord("#"):
            modify_grid(grid, selection_grid, viewing_grid, cursor_x, cursor_y, "#")

        elif key == ord("."):
            modify_grid(grid, selection_grid, viewing_grid, cursor_x, cursor_y, ".")

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
                    
                    if grid[y][x] == '.':
                        game_arr[y//BLOCK_H][x//BLOCK_W] = 7
                        mask.append([y//BLOCK_H, x//BLOCK_W])
            


            return mask

        elif key == ord("q"):
            break

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

mask = curses.wrapper(GetKeepoutMask, game_arr)
print(mask)
print(game_arr)