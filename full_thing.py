import curses
import pulp
import sys
from typing import List, Tuple, Dict, Any

# ====================== RULE CLASSES ======================
class Keepout_Rule:
    def __init__(self, spaces: List[List[int]], mask: List[List[int]]):
        self.spaces = spaces
        self.mask = mask

class Equals_Rule:
    def __init__(self, spaces: List[List[int]]):
        self.spaces = spaces
        self.type = "="

class Unequal_Rule:
    def __init__(self, spaces: List[List[int]]):
        self.spaces = spaces
        self.type = "!="

class Sum_Rule:
    def __init__(self, spaces: List[List[int]], val: int):
        self.spaces = spaces
        self.type = "sum"
        self.val = val

class GreaterThan_Rule:
    def __init__(self, spaces: List[List[int]], val: int):
        self.spaces = spaces
        self.type = ">"
        self.val = val

class LessThan_Rule:
    def __init__(self, spaces: List[List[int]], val: int):
        self.spaces = spaces
        self.type = "<"
        self.val = val


# ====================== YOUR DOMINO PRINTING CODE (exactly as provided) ======================
nil = "XXXXXXXXX"
blank = "|       |"
dot_l = "| .     |"
dot_m = "|   .   |"
dot_r = "|     . |"
dots2 = "| .   . |"
dots3 = "| . . . |"
v_top = ",-------,"
v_middle = "|_______|"
v_bottom = "'-------'"
h_top_l = ",--------"
h_top_r = "--------,"
h_bottom_l = "'--------"
h_bottom_r = "--------'"

vertical_numbers = [
    [blank, blank, blank],
    [blank, dot_m, blank],
    [dot_r, blank, dot_l],
    [dot_r, dot_m, dot_l],
    [dots2, blank, dots2],
    [dots2, dot_m, dots2],
    [dots2, dots2, dots2]
]

horizontal_numbers = [
    [blank, blank, blank],
    [blank, dot_m, blank],
    [dot_l, blank, dot_r],
    [dot_l, dot_m, dot_r],
    [dots2, blank, dots2],
    [dots2, dot_m, dots2],
    [dots3, blank, dots3]
]

class Domino:
    def __init__(self, p1: int, p2: int, vertical: bool = False):
        self.p1 = p1
        self.p2 = p2
        self.vertical = vertical

class FinalBoardSpace:
    def __init__(self):
        self.num_pips = None
        self.orientation = None

class FinalBoard:
    def __init__(self, width: int, height: int):
        self.grid = [[FinalBoardSpace() for _ in range(width)] for _ in range(height)]
        self.width = width
        self.height = height

    def add_domino(self, x: int, y: int, domino: Domino):
        if domino.vertical:
            if y + 1 < self.height:
                self.grid[y][x].num_pips = domino.p1
                self.grid[y][x].orientation = "D"
                self.grid[y + 1][x].num_pips = domino.p2
                self.grid[y + 1][x].orientation = "U"
        else:
            if x + 1 < self.width:
                self.grid[y][x].num_pips = domino.p1
                self.grid[y][x].orientation = "R"
                self.grid[y][x + 1].num_pips = domino.p2
                self.grid[y][x + 1].orientation = "L"

    def print_grid(self):
        screen = [""] * (self.height * 5)
        for i in range(self.height):
            for j in range(self.width):
                offset = i * 5
                cell = self.grid[i][j]
                if cell.orientation is None:
                    for k in range(5):
                        screen[offset + k] += nil
                elif cell.orientation == "D":
                    screen[offset] += v_top
                    offset += 1
                    for k in range(3):
                        screen[offset + k] += vertical_numbers[cell.num_pips][k]
                    offset += 3
                    screen[offset] += v_middle
                elif cell.orientation == "U":
                    screen[offset] += blank
                    offset += 1
                    for k in range(3):
                        screen[offset + k] += vertical_numbers[cell.num_pips][k]
                    offset += 3
                    screen[offset] += v_bottom
                elif cell.orientation == "R":
                    screen[offset] += h_top_l
                    offset += 1
                    for k in range(3):
                        screen[offset + k] += horizontal_numbers[cell.num_pips][k][:8] + "|"
                    offset += 3
                    screen[offset] += h_bottom_l
                else:  # "L"
                    screen[offset] += h_top_r
                    offset += 1
                    for k in range(3):
                        screen[offset + k] += " " + horizontal_numbers[cell.num_pips][k][1:]
                    offset += 3
                    screen[offset] += h_bottom_r
        for line in screen:
            print(line)


# ====================== MIP SOLVER ======================
def solve_pips_mip(domino_list: List[Tuple[int, int]],
                   S_list: List[Tuple[int, int]],
                   regions: List[Dict[str, Any]],
                   game_width: int = None,
                   game_height: int = None,
                   mask: List[List[int]] = None) -> None:
    if 2 * len(domino_list) != len(S_list):
        print("Error: 2 * number of dominoes must equal number of tiles")
        return

    S_set = set(S_list)
    R = [0, 1, 2, 3]

    def get_partner(k: int, l: int, r: int) -> Tuple[int, int] | None:
        if r == 0: return (k, l + 1)
        if r == 1: return (k + 1, l)
        if r == 2: return (k, l - 1)
        if r == 3: return (k - 1, l)
        return None

    prob = pulp.LpProblem("NYT_Pips_MIP", pulp.LpMinimize)
    prob += 0

    # Variables
    x = {}
    for i in range(len(domino_list)):
        x[i] = {}
        for r in R:
            x[i][r] = {}
            for pos in S_list:
                partner = get_partner(*pos, r)
                if partner and partner in S_set:
                    x[i][r][pos] = pulp.LpVariable(f"x_{i}_{r}_{pos[0]}_{pos[1]}", cat="Binary")

    y = {pos: pulp.LpVariable(f"y_{pos[0]}_{pos[1]}", lowBound=0, upBound=6, cat="Integer")
         for pos in S_list}

    z = {pos: {j: pulp.LpVariable(f"z_{pos[0]}_{pos[1]}_{j}", cat="Binary") for j in range(7)}
         for pos in S_list}

    # A1: Each domino placed exactly once
    for i in range(len(domino_list)):
        prob += pulp.lpSum(x[i][r].values() for r in R) == 1

    # A2 + A3: Coverage + y values
    coverage = {pos: 0 for pos in S_list}
    y_expr = {pos: 0 for pos in S_list}
    for i, (d1, d2) in enumerate(domino_list):
        for r in R:
            for pos in list(x[i][r].keys()):
                var = x[i][r][pos]
                partner = get_partner(*pos, r)
                coverage[pos] += var
                coverage[partner] += var
                y_expr[pos] += d1 * var
                y_expr[partner] += d2 * var

    for pos in S_list:
        prob += coverage[pos] == 1
        prob += y[pos] == y_expr[pos]

    # A4: z indicators
    for pos in S_list:
        prob += y[pos] == pulp.lpSum(j * z[pos][j] for j in range(7))
        prob += pulp.lpSum(z[pos].values()) == 1

    # A5: Regional constraints
    for region in regions:
        tiles = region["tiles"]
        ctype = region["type"]
        N = region.get("N")
        if ctype == "=" and len(tiles) >= 2:
            base = tiles[0]
            for t in tiles[1:]:
                prob += y[base] == y[t]
        elif ctype == "sum":
            prob += pulp.lpSum(y[t] for t in tiles) == N
        elif ctype == "!=":
            for j in range(7):
                prob += pulp.lpSum(z[t][j] for t in tiles) <= 1
        elif ctype == "<":
            prob += pulp.lpSum(y[t] for t in tiles) <= N - 1
        elif ctype == ">":
            prob += pulp.lpSum(y[t] for t in tiles) >= N + 1

    # Solve
    try:
        status = prob.solve(pulp.HiGHS_CMD(msg=False))
    except:
        status = prob.solve(pulp.PULP_CBC_CMD(msg=False))

    if pulp.LpStatus[status] != "Optimal":
        print("No solution found.")
        return

    print("\n=== SOLUTION FOUND ===\n")

    # Build visual board with full original dimensions
    if game_width is None or game_height is None:
        max_row = max(k for k, l in S_list) if S_list else 0
        max_col = max(l for k, l in S_list) if S_list else 0
        board_width = max_col + 1
        board_height = max_row + 1
    else:
        board_width = game_width
        board_height = game_height

    board = FinalBoard(board_width, board_height)

    # Mark non-playable areas if mask is provided
    if mask:
        for mask_pos in mask:
            # Mark these areas in the board (they remain empty/unset)
            pass

    for i, (d1, d2) in enumerate(domino_list):
        for r in R:
            for pos in x[i][r]:
                if pulp.value(x[i][r][pos]) > 0.5:
                    k, l = pos
                    if r == 0:   board.add_domino(l, k, Domino(d1, d2, False))
                    elif r == 2: board.add_domino(l - 1, k, Domino(d2, d1, False))
                    elif r == 1: board.add_domino(l, k, Domino(d1, d2, True))
                    elif r == 3: board.add_domino(l, k - 1, Domino(d2, d1, True))
                    break

    board.print_grid()

    print("\nTile numbers (for reference):")
    for pos in sorted(S_list):
        print(f"  {pos}: {int(pulp.value(y[pos]))}")


def is_tile_selected(selection_grid: List[List[bool]], ty: int, tx: int, BLOCK_W: int, BLOCK_H: int) -> bool:
    """Check if any part of a tile is selected."""
    for dy in range(BLOCK_H):
        for dx in range(BLOCK_W):
            if selection_grid[ty * BLOCK_H + dy][tx * BLOCK_W + dx]:
                return True
    return False


def cursor_is_visible(start_time: float, last_action_time: float = None, idle_threshold: float = 0.3, blink_period: float = 0.5) -> bool:
    """Check if cursor should be visible, considering both blink and idle time.
    
    Args:
        start_time: When blinking started
        last_action_time: When user last moved/highlighted (None = always blink)
        idle_threshold: Seconds of inactivity before blinking starts (0.3s)
        blink_period: Length of each blink cycle (0.5s = 0.5s on, 0.5s off)
    """
    # If last action is recent, keep cursor solid (visible)
    if last_action_time is not None:
        idle_time = time.time() - last_action_time
        if idle_time < idle_threshold:
            return True
    
    # Otherwise blink normally
    elapsed = time.time() - start_time
def is_on_highlighted_border(selection_grid: List[List[bool]], y: int, x: int, tile_width: int, tile_height: int) -> bool:
    """Check if a cell is on the border of a highlighted tile."""
    ty = y // tile_height
    tx = x // tile_width
    
    # Check if tile is selected (any cell in tile is True)
    tile_selected = False
    for dy in range(tile_height):
        for dx in range(tile_width):
            yy = ty * tile_height + dy
            xx = tx * tile_width + dx
            if yy < len(selection_grid) and xx < len(selection_grid[yy]) and selection_grid[yy][xx]:
                tile_selected = True
                break
        if tile_selected:
            break
    
    if not tile_selected:
        return False
    
    # Check if (y,x) is on the border of this tile
    local_y = y % tile_height
    local_x = x % tile_width
    return local_y == 0 or local_y == tile_height - 1 or local_x == 0 or local_x == tile_width - 1


def draw_dominos(stdscr, dominos: List[str], selection_grid: List[List[bool]], cursor_x: int, cursor_y: int, DOM_GRID_WIDTH: int, DOM_GRID_HEIGHT: int, BLOCK_W: int, BLOCK_H: int, cursor_blink_time: float = None, last_action_time: float = None) -> None:
    """Draw the domino selection grid with highlighting."""
    stdscr.clear()
    max_y, max_x = stdscr.getmaxyx()
    show_cursor = True
    
    for y in range(min(DOM_GRID_HEIGHT, max_y)):
        line = []
        for x in range(min(DOM_GRID_WIDTH, max_x)):
            if y < len(dominos) and x < len(dominos[y]):
                char = dominos[y][x]
            else:
                char = " "

            # Check if on cursor border (only edges, not interior)
            on_cursor_border = (cursor_x <= x < cursor_x + (2 * BLOCK_W) and cursor_y <= y < cursor_y + BLOCK_H) and \
                               (x == cursor_x or x == cursor_x + (2 * BLOCK_W) - 1 or y == cursor_y or y == cursor_y + BLOCK_H - 1)
            is_highlighted = y < len(selection_grid) and x < len(selection_grid[y]) and selection_grid[y][x]
            is_highlighted_border = is_on_highlighted_border(selection_grid, y, x, 2 * BLOCK_W + 1, BLOCK_H)
            
            # Cursor always visible on border, blinks even over highlighted spaces
            if on_cursor_border:
                attr = curses.A_REVERSE if show_cursor else curses.A_BOLD
            elif is_highlighted and not is_highlighted_border:
                attr = curses.A_REVERSE  # Only highlight interior of selected spaces
            else:
                attr = 0
            
            line.append((char, attr))
        
        # Group consecutive same attr
        i = 0
        while i < len(line):
            j = i
            while j < len(line) and line[j][1] == line[i][1]:
                j += 1
            chs = ''.join(c for c, a in line[i:j])
            try:
                if line[i][1]:
                    stdscr.addstr(y, i, chs, line[i][1])
                else:
                    stdscr.addstr(y, i, chs)
            except curses.error:
                pass
            i = j


# ====================== GRID MODIFIER FUNCTION ======================
def modify_grid(grid: List[List[str]], rule: Any, BLOCK_W: int, BLOCK_H: int, GAME_WIDTH: int, GAME_HEIGHT: int) -> None:
    """Modify grid display to show rule borders and bottom-right labels."""

    # Draw only border for rule regions; leave interior blank.
    if isinstance(rule, Keepout_Rule):
        description = None
    elif isinstance(rule, Equals_Rule):
        description = "="
    elif isinstance(rule, Unequal_Rule):
        description = "!="
    elif isinstance(rule, Sum_Rule):
        description = f"{rule.val}"
    elif isinstance(rule, GreaterThan_Rule):
        description = f">{rule.val}"
    elif isinstance(rule, LessThan_Rule):
        description = f"<{rule.val}"
    else:
        description = "?"
    rule_spaces_set = set((ty, tx) for ty, tx in rule.spaces)

    # For bottom-right description location (favor bottom, then rightmost in that row)
    max_ty = max(ty for ty, tx in rule.spaces)
    max_tx = max(tx for ty, tx in rule.spaces if ty == max_ty)
    desc_y = max_ty * BLOCK_H + BLOCK_H - 2
    desc_x = max_tx * BLOCK_W + BLOCK_W - len(description) - 1 if description else None

    hborder = [[False] * len(grid[0]) for _ in range(len(grid))]
    vborder = [[False] * len(grid[0]) for _ in range(len(grid))]

    for ty, tx in rule.spaces:
        grid_y = ty * BLOCK_H
        grid_x = tx * BLOCK_W

        has_up = (ty - 1, tx) in rule_spaces_set
        has_down = (ty + 1, tx) in rule_spaces_set
        has_left = (ty, tx - 1) in rule_spaces_set
        has_right = (ty, tx + 1) in rule_spaces_set

        for dy in range(BLOCK_H):
            for dx in range(BLOCK_W):
                y = grid_y + dy
                x = grid_x + dx
                if y >= len(grid) or x >= len(grid[0]):
                    continue

                # Clear interior to space
                grid[y][x] = " "

                is_top = dy == 0
                is_bottom = dy == BLOCK_H - 1
                is_left = dx == 0
                is_right = dx == BLOCK_W - 1

                if is_top and not has_up:
                    hborder[y][x] = True
                if is_bottom and not has_down:
                    hborder[y][x] = True
                if is_left and not has_left:
                    vborder[y][x] = True
                if is_right and not has_right:
                    vborder[y][x] = True

    # Now stamp final border chars
    for y in range(len(grid)):
        for x in range(len(grid[0])):
            if hborder[y][x] and vborder[y][x]:
                grid[y][x] = "+"
            elif hborder[y][x]:
                grid[y][x] = "-"
            elif vborder[y][x]:
                grid[y][x] = "|"
            else:
                # retain spaces or previous char
                grid[y][x] = grid[y][x]

    # Place description text in bottom-right of region (rule only)
    if description is not None:
        if desc_y < len(grid):
            for i, ch in enumerate(description):
                px = desc_x + i
                if 0 <= px < len(grid[0]):
                    grid[desc_y][px] = ch


# ====================== CURSES UI (fixed + dynamic size + selection cleared) ======================
def UI(stdscr, game_arr: List[List[int]]) -> Tuple[List[Any], List]:
    curses.curs_set(0)
    stdscr.keypad(True)

    BLOCK_W = 9
    BLOCK_H = 5

    GAME_HEIGHT = len(game_arr)
    GAME_WIDTH = len(game_arr[0]) if game_arr else 0
    GRID_WIDTH = GAME_WIDTH * BLOCK_W
    GRID_HEIGHT = GAME_HEIGHT * BLOCK_H

    grid = [["." for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    selection_grid = [[False] * GRID_WIDTH for _ in range(GRID_HEIGHT)]
    cursor_x = 0
    cursor_y = 0
    rules: List[Any] = []

    # Step 1: Define playable board area
    while True:
        stdscr.clear()
        show_cursor = True
        
        max_y, max_x = stdscr.getmaxyx()
        for y in range(min(GRID_HEIGHT, max_y)):
            line = []
            for x in range(min(GRID_WIDTH, max_x)):
                ch = grid[y][x]
                # Check if on cursor border (only edges, not interior)
                on_cursor_border = (cursor_x <= x < cursor_x + BLOCK_W and cursor_y <= y < cursor_y + BLOCK_H) and \
                                   (x == cursor_x or x == cursor_x + BLOCK_W - 1 or y == cursor_y or y == cursor_y + BLOCK_H - 1)
                is_highlighted = selection_grid[y][x]
                is_highlighted_border = is_on_highlighted_border(selection_grid, y, x, BLOCK_W, BLOCK_H)
                
                # Cursor always visible on border, blinks even over highlighted spaces
                if on_cursor_border:
                    attr = curses.A_REVERSE if show_cursor else curses.A_BOLD
                elif is_highlighted and not is_highlighted_border:
                    attr = curses.A_REVERSE  # Only highlight interior of selected spaces
                else:
                    attr = curses.A_BOLD if ch in "-|+" else 0
                
                line.append((ch, attr))
            
            # Group consecutive same attr
            i = 0
            while i < len(line):
                j = i
                while j < len(line) and line[j][1] == line[i][1]:
                    j += 1
                chs = ''.join(c for c, a in line[i:j])
                if line[i][1]:
                    stdscr.addstr(y, i, chs, line[i][1])
                else:
                    stdscr.addstr(y, i, chs)
                i = j
        
        stdscr.addstr(GRID_HEIGHT + 1, 0, "Step 1: Highlight playable area → press ENTER")
        stdscr.addstr(GRID_HEIGHT + 2, 0, "Arrows | h=highlight | u=unhighlight | ENTER=confirm | q=quit")
        stdscr.refresh()

        key = stdscr.getch()
        if key == curses.KEY_RIGHT:
            cursor_x = min(GRID_WIDTH - BLOCK_W, cursor_x + BLOCK_W)
        elif key == curses.KEY_LEFT:
            cursor_x = max(0, cursor_x - BLOCK_W)
        elif key == curses.KEY_UP:
            cursor_y = max(0, cursor_y - BLOCK_H)
        elif key == curses.KEY_DOWN:
            cursor_y = min(GRID_HEIGHT - BLOCK_H, cursor_y + BLOCK_H)
        elif key == ord("h"):
            for y in range(cursor_y, cursor_y + BLOCK_H):
                for x in range(cursor_x, cursor_x + BLOCK_W):
                    selection_grid[y][x] = True
        elif key == ord("u"):
            for y in range(cursor_y, cursor_y + BLOCK_H):
                for x in range(cursor_x, cursor_x + BLOCK_W):
                    selection_grid[y][x] = False
        elif key == ord("\n"):
            spaces = []
            mask = []
            for ty in range(GAME_HEIGHT):
                for tx in range(GAME_WIDTH):
                    if selection_grid[ty * BLOCK_H][tx * BLOCK_W]:
                        game_arr[ty][tx] = None
                        spaces.append([ty, tx])
                    else:
                        mask.append([ty, tx])
            if len(spaces) % 2 != 0:
                raise ValueError("Playable spaces must be even")
            keepout_rule = Keepout_Rule(spaces, mask)
            rules.append(keepout_rule)
            modify_grid(grid, keepout_rule, BLOCK_W, BLOCK_H, GAME_WIDTH, GAME_HEIGHT)
            selection_grid = [[False] * GRID_WIDTH for _ in range(GRID_HEIGHT)]  # cleared
            break
        elif key == ord("q"):
            raise SystemExit("User quit")

    # Step 2: Add regional rules
    playable_spaces = set((ty, tx) for ty, tx in rules[0].spaces)
    ruled_spaces = set()  # Track spaces already covered by rules
    last_message = ""
    
    while True:
        stdscr.clear()
        show_cursor = True
        
        max_y, max_x = stdscr.getmaxyx()
        for y in range(min(GRID_HEIGHT, max_y)):
            line = []
            for x in range(min(GRID_WIDTH, max_x)):
                ch = grid[y][x]
                # Check if on cursor border (only edges, not interior)
                on_cursor_border = (cursor_x <= x < cursor_x + BLOCK_W and cursor_y <= y < cursor_y + BLOCK_H) and \
                                   (x == cursor_x or x == cursor_x + BLOCK_W - 1 or y == cursor_y or y == cursor_y + BLOCK_H - 1)
                is_highlighted = selection_grid[y][x]
                is_highlighted_border = is_on_highlighted_border(selection_grid, y, x, BLOCK_W, BLOCK_H)
                
                # Cursor always visible on border, blinks even over highlighted spaces
                if on_cursor_border:
                    attr = curses.A_REVERSE if show_cursor else curses.A_BOLD
                elif is_highlighted and not is_highlighted_border:
                    attr = curses.A_REVERSE  # Only highlight interior of selected spaces
                else:
                    attr = curses.A_BOLD if ch in "-|+" else 0
                
                line.append((ch, attr))
            
            # Group consecutive same attr
            i = 0
            while i < len(line):
                j = i
                while j < len(line) and line[j][1] == line[i][1]:
                    j += 1
                chs = ''.join(c for c, a in line[i:j])
                if line[i][1]:
                    stdscr.addstr(y, i, chs, line[i][1])
                else:
                    stdscr.addstr(y, i, chs)
                i = j
        
        stdscr.addstr(GRID_HEIGHT + 1, 0, "Step 2: Highlight region → type rule")
        stdscr.addstr(GRID_HEIGHT + 2, 0, "== Equals  != Unequal  +XX Sum  >XX Greater  <XX Less")
        stdscr.addstr(GRID_HEIGHT + 3, 0, "ENTER = finish rules | q = quit")
        if last_message:
            stdscr.addstr(GRID_HEIGHT + 4, 0, last_message)
        stdscr.refresh()

        key = stdscr.getch()
        if key == curses.KEY_RIGHT:
            cursor_x = min(GRID_WIDTH - BLOCK_W, cursor_x + BLOCK_W)
        elif key == curses.KEY_LEFT:
            cursor_x = max(0, cursor_x - BLOCK_W)
        elif key == curses.KEY_UP:
            cursor_y = max(0, cursor_y - BLOCK_H)
        elif key == curses.KEY_DOWN:
            cursor_y = min(GRID_HEIGHT - BLOCK_H, cursor_y + BLOCK_H)
        elif key == ord("h"):
            for y in range(cursor_y, cursor_y + BLOCK_H):
                for x in range(cursor_x, cursor_x + BLOCK_W):
                    # Only allow highlights in playable area and not already ruled
                    ty, tx = y // BLOCK_H, x // BLOCK_W
                    if (ty, tx) in playable_spaces and (ty, tx) not in ruled_spaces:
                        selection_grid[y][x] = True
        elif key == ord("u"):
            for y in range(cursor_y, cursor_y + BLOCK_H):
                for x in range(cursor_x, cursor_x + BLOCK_W):
                    selection_grid[y][x] = False
        elif key == ord("="):
            if stdscr.getch() == ord("="):
                spaces = [[ty, tx] for ty in range(GAME_HEIGHT) for tx in range(GAME_WIDTH)
                          if is_tile_selected(selection_grid, ty, tx, BLOCK_W, BLOCK_H)]
                if spaces:  # Only add if something selected
                    rule = Equals_Rule(spaces)
                    rules.append(rule)
                    for space in spaces:
                        ruled_spaces.add((space[0], space[1]))
                    modify_grid(grid, rule, BLOCK_W, BLOCK_H, GAME_WIDTH, GAME_HEIGHT)
                    last_message = f"Added == rule to {len(spaces)} tiles"
                else:
                    last_message = "No tiles selected for rule"
                selection_grid = [[False] * GRID_WIDTH for _ in range(GRID_HEIGHT)]
        elif key == ord("!"):
            if stdscr.getch() == ord("="):
                spaces = [[ty, tx] for ty in range(GAME_HEIGHT) for tx in range(GAME_WIDTH)
                          if is_tile_selected(selection_grid, ty, tx, BLOCK_W, BLOCK_H)]
                if spaces:
                    rule = Unequal_Rule(spaces)
                    rules.append(rule)
                    for space in spaces:
                        ruled_spaces.add((space[0], space[1]))
                    modify_grid(grid, rule, BLOCK_W, BLOCK_H, GAME_WIDTH, GAME_HEIGHT)
                    last_message = f"Added != rule to {len(spaces)} tiles"
                else:
                    last_message = "No tiles selected for rule"
                selection_grid = [[False] * GRID_WIDTH for _ in range(GRID_HEIGHT)]
        elif key == ord("+"):
            k2 = stdscr.getch()
            k3 = stdscr.getch()
            if 48 <= k2 <= 57 and 48 <= k3 <= 57:
                val = (k2 - 48) * 10 + (k3 - 48)
                spaces = [[ty, tx] for ty in range(GAME_HEIGHT) for tx in range(GAME_WIDTH)
                          if is_tile_selected(selection_grid, ty, tx, BLOCK_W, BLOCK_H)]
                if spaces:
                    rule = Sum_Rule(spaces, val)
                    rules.append(rule)
                    for space in spaces:
                        ruled_spaces.add((space[0], space[1]))
                    modify_grid(grid, rule, BLOCK_W, BLOCK_H, GAME_WIDTH, GAME_HEIGHT)
                    last_message = f"Added +{val} rule to {len(spaces)} tiles"
                else:
                    last_message = "No tiles selected for rule"
                selection_grid = [[False] * GRID_WIDTH for _ in range(GRID_HEIGHT)]
        elif key == ord(">"):
            k2 = stdscr.getch()
            k3 = stdscr.getch()
            if 48 <= k2 <= 57 and 48 <= k3 <= 57:
                val = (k2 - 48) * 10 + (k3 - 48)
                spaces = [[ty, tx] for ty in range(GAME_HEIGHT) for tx in range(GAME_WIDTH)
                          if is_tile_selected(selection_grid, ty, tx, BLOCK_W, BLOCK_H)]
                if spaces:
                    rule = GreaterThan_Rule(spaces, val)
                    rules.append(rule)
                    for space in spaces:
                        ruled_spaces.add((space[0], space[1]))
                    modify_grid(grid, rule, BLOCK_W, BLOCK_H, GAME_WIDTH, GAME_HEIGHT)
                    last_message = f"Added >{val} rule to {len(spaces)} tiles"
                else:
                    last_message = "No tiles selected for rule"
                selection_grid = [[False] * GRID_WIDTH for _ in range(GRID_HEIGHT)]
        elif key == ord("<"):
            k2 = stdscr.getch()
            k3 = stdscr.getch()
            if 48 <= k2 <= 57 and 48 <= k3 <= 57:
                val = (k2 - 48) * 10 + (k3 - 48)
                spaces = [[ty, tx] for ty in range(GAME_HEIGHT) for tx in range(GAME_WIDTH)
                          if is_tile_selected(selection_grid, ty, tx, BLOCK_W, BLOCK_H)]
                if spaces:
                    rule = LessThan_Rule(spaces, val)
                    rules.append(rule)
                    for space in spaces:
                        ruled_spaces.add((space[0], space[1]))
                    modify_grid(grid, rule, BLOCK_W, BLOCK_H, GAME_WIDTH, GAME_HEIGHT)
                    last_message = f"Added <{val} rule to {len(spaces)} tiles"
                else:
                    last_message = "No tiles selected for rule"
                selection_grid = [[False] * GRID_WIDTH for _ in range(GRID_HEIGHT)]
        elif key == ord("\n"):
            break
        elif key == ord("q"):
            raise SystemExit("User quit")

    # Step 3: Domino selection
    DOM_WIDTH = 7
    DOM_HEIGHT = 7
    DOM_GRID_WIDTH = DOM_WIDTH * (2 * BLOCK_W + 1) - 1
    DOM_GRID_HEIGHT = DOM_HEIGHT * BLOCK_H
    
    dominos = [",----------------, ,----------------, ,----------------, ,----------------, ,----------------, ,----------------, ,----------------,",
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
    selection_grid_dominos = [[False for _ in range(DOM_GRID_WIDTH)] for _ in range(DOM_GRID_HEIGHT)]
    cursor_x = 0
    cursor_y = 0

    while True:
        draw_dominos(stdscr, dominos, selection_grid_dominos, cursor_x, cursor_y, DOM_GRID_WIDTH, DOM_GRID_HEIGHT, BLOCK_W, BLOCK_H, None, None)
        stdscr.addstr(DOM_GRID_HEIGHT + 1, 0, "Step 3: Select dominos → press 'a' to add")
        stdscr.addstr(DOM_GRID_HEIGHT + 2, 0, "Arrows move | h=highlight | u=unhighlight | a=add | ENTER=finish | q=quit")
        stdscr.addstr(DOM_GRID_HEIGHT + 3, 0, f"Dominos added: {len(domino_list)} / {len(rules[0].spaces) // 2}")
        stdscr.refresh()

        key = stdscr.getch()
        if key == curses.KEY_RIGHT:
            cursor_x = min(DOM_GRID_WIDTH - (2 * BLOCK_W), cursor_x + (2 * BLOCK_W) + 1)
        elif key == curses.KEY_LEFT:
            cursor_x = max(0, cursor_x - (2 * BLOCK_W) - 1)
        elif key == curses.KEY_UP:
            cursor_y = max(0, cursor_y - BLOCK_H)
        elif key == curses.KEY_DOWN:
            cursor_y = min(DOM_GRID_HEIGHT - BLOCK_H, cursor_y + BLOCK_H)
        elif key == ord("h"):
            for y in range(cursor_y, min(cursor_y + BLOCK_H, DOM_GRID_HEIGHT)):
                for x in range(cursor_x, min(cursor_x + (2 * BLOCK_W), DOM_GRID_WIDTH)):
                    selection_grid_dominos[y][x] = True
        elif key == ord("u"):
            for y in range(cursor_y, min(cursor_y + BLOCK_H, DOM_GRID_HEIGHT)):
                for x in range(cursor_x, min(cursor_x + (2 * BLOCK_W), DOM_GRID_WIDTH)):
                    selection_grid_dominos[y][x] = False
        elif key == ord("a"):
            # Detect which domino was selected based on highlighted area
            for i in range(DOM_HEIGHT):
                for j in range(DOM_WIDTH):
                    # Check if this domino tile is highlighted
                    grid_y = i * BLOCK_H
                    grid_x = j * (2 * BLOCK_W + 1)
                    if grid_y < DOM_GRID_HEIGHT and grid_x < DOM_GRID_WIDTH:
                        if selection_grid_dominos[grid_y][grid_x]:
                            domino_list.append(Domino(i, j, False))
            
            # Clear selection
            selection_grid_dominos = [[False for _ in range(DOM_GRID_WIDTH)] for _ in range(DOM_GRID_HEIGHT)]
        elif key == ord("\n"):
            expected = len(rules[0].spaces) // 2
            if len(domino_list) == expected:
                break
            else:
                raise ValueError(f"Added {len(domino_list)} dominos, but need {expected}")
        elif key == ord("q"):
            raise SystemExit("User quit")

    return rules, domino_list


# ====================== MAIN ======================
if __name__ == "__main__":
    # Change these numbers if you want a different board size
    GAME_WIDTH = 10
    GAME_HEIGHT = 8
    game_arr = [[7 for _ in range(GAME_WIDTH)] for _ in range(GAME_HEIGHT)]

    try:
        rules, domino_objects = curses.wrapper(UI, game_arr)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except SystemExit as e:
        print(e)
        sys.exit(0)

    # Convert UI output to MIP input
    S_list = [tuple(tile) for tile in rules[0].spaces]
    domino_list = [(d.p1, d.p2) for d in domino_objects] if domino_objects else []

    regions = []
    for rule in rules[1:]:
        tiles = [tuple(t) for t in rule.spaces]
        if isinstance(rule, Equals_Rule):
            regions.append({"tiles": tiles, "type": "="})
        elif isinstance(rule, Unequal_Rule):
            regions.append({"tiles": tiles, "type": "!="})
        elif isinstance(rule, Sum_Rule):
            regions.append({"tiles": tiles, "type": "sum", "N": rule.val})
        elif isinstance(rule, GreaterThan_Rule):
            regions.append({"tiles": tiles, "type": ">", "N": rule.val})
        elif isinstance(rule, LessThan_Rule):
            regions.append({"tiles": tiles, "type": "<", "N": rule.val})

    print("\nSolving puzzle with MIP solver...")
    solve_pips_mip(domino_list, S_list, regions, GAME_WIDTH, GAME_HEIGHT, rules[0].mask)

    print("\nDone! The ASCII art above is your solved Pips puzzle.")