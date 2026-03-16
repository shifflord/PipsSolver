# Expects an n x 2 array of coordinates on the board which tiles may not be places on
class Keepout_Rule:
    def __init__(self, mask):
        self.mask = mask
    
    def check_rule(self, board):

        # Invalid placement locations are stored in gameboard array as 7
        for coord in self.mask: 
            if board[coord[0],coord[1]] != 7:
                return False
        return True

# Expects an n x 2 array of coordinates on the board where pips must be equal to one another 
# Assumes None type (unplaced) are valid 
class Equals_Rule:
    def __init__(self, spaces):
        self.spaces = spaces
    
    def check_rule(self, board):
        temp_arr = [0]*len(self.spaces)
        for i in range(len(self.spaces)): 
            temp_arr[i] = board[self.spaces[i][0], self.spaces[i][1]]
        for num in temp_arr:
            if num is not None:

                # Is there more than one number in these spaces?
                return all(x == None or x == num for x in temp_arr)
            
        # All spaces empty
        return True

# Check if all pips sum, or can sum, to a value
class Sum_Rule:
    def __init__(self, spaces, val):
        self.spaces = spaces
        self.val = val
    
    def check_rule(self, board):
        temp_arr = [0]*len(self.spaces)
        for i in range(len(self.spaces)): 
            temp_arr[i] = board[self.spaces[i][0], self.spaces[i][1]]
        
        curr_sum = 0
        nan_ct = 0
        for num in temp_arr:
            if num is None:
                nan_ct += 1
            else:
                curr_sum += num
        
        # All spaces empty (since this is a likely case it should be checked first)
        if nan_ct == len(self.spaces):
            return True

        # Too many pips, pips can't be subtracted!
        if curr_sum > self.val:
            return False
        
        # Too few pips, can never be fixed by adding more
        if (self.val - curr_sum) > (nan_ct * 6):
            return False
        
        # All spaces are filled to no avail
        if (nan_ct == 0) & curr_sum != self.val:
            return False

        # It's possible!
        return True
    
# Check if all pips are less than a value
class LessThan_Rule:
    def __init__(self, spaces, val):
        self.spaces = spaces
        self.val = val
    
    def check_rule(self, board):
        temp_arr = [0]*len(self.spaces)
        for i in range(len(self.spaces)): 
            temp_arr[i] = board[self.spaces[i][0], self.spaces[i][1]]
        
        curr_sum = 0
        for num in temp_arr:
            if num is not None:
                curr_sum += num
        
        if curr_sum >= self.val:
            # Too many pips, pips can't be subtracted!
            return False
        else:
            # It's possible!
            return True
        
# Check if all pips sum, or can sum, to a value greater than
class GreaterThan_Rule:
    def __init__(self, spaces, val):
        self.spaces = spaces
        self.val = val
    
    def check_rule(self, board):
        temp_arr = [0]*len(self.spaces)
        for i in range(len(self.spaces)): 
            temp_arr[i] = board[self.spaces[i][0], self.spaces[i][1]]
        
        curr_sum = 0
        nan_ct = 0
        for num in temp_arr:
            if num is None:
                nan_ct += 1
            else:
                curr_sum += num
        
        # All spaces empty (since this is a likely case it should be checked first)
        if nan_ct == len(self.spaces):
            return True
        
        
        if (self.val - curr_sum) >= (nan_ct * 6):
            # Too few pips, can never be fixed by adding more
            return False
        else:
            # It's possible!
            return True
        