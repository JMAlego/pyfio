import math, copy

PLAYER0 = BLANK   = 0
PLAYER1 = PLAYERA = 1
PLAYER2 = PLAYERB = 2

INITIAL_STATES = [[[0,0,0,0,0,0],
                   [0,0,0,0,0,0],
                   [0,0,1,2,0,0],
                   [0,0,2,1,0,0],
                   [0,0,0,0,0,0],
                   [0,0,0,0,0,0] ],
                  [[0,0,0,0,0,0],
                   [0,0,0,0,0,0],
                   [0,0,2,1,0,0],
                   [0,0,1,2,0,0],
                   [0,0,0,0,0,0],
                   [0,0,0,0,0,0] ]]

def otherPlayer(player):
  return 1 + player % 2

class Line:
  start  = None
  end    = None
  middle = []
  length = 0
  full_line = False
  
  def __init__(self):
    self.start  = None
    self.end    = None
    self.middle = []
    self.length = 0
    self.full_line = False
    
  def __str__(self):
    string = "ln:["
    first = True
    for item in self.getFullLine():
      string += ("" if first else ", ") + "(" + str(item[0]) + ", " + str(item[1]) + ")"
      first = False
    string += "]"
    return string
  
  __repr__ = __str__
  
  def getFullLine(self):
    if not self.isValid(): return []
    full = []
    full.append(self.start)
    for item in self.middle: full.append(item)
    full.append(self.end)
    return full
    
  def getWithoutStart(self):
    if not self.isValid(): return []
    full = []
    for item in self.middle: full.append(item)
    full.append(self.end)
    return full
  
  def setStartPoint(self, point):
    self.start = point
    self.length += 1
  
  def setEndPoint(self, point):
    self.end = point
    self.length += 1
    self.full_line = True
  
  def addPoint(self, point):
    self.middle.append(point)
    self.length += 1
    
  def isPointInLine(self, point):
    return point in self.getFullLine()
    
  def isPointStart(self, point):
    return point == self.start
  
  def isPointEnd(self, point):
    return point == self.end
  
  def isPointInMiddle(self, point):
    return point in self.middle
    
  def isValid(self):
    return self.start != None and self.end != None and self.length > 2 and self.full_line == True and len(self.middle) > 0

class Move:
  lines = []
  player = BLANK
  __placed_piece = None
  
  def __init__(self):
    self.lines = []
    self.player = BLANK
    self.__placed_piece = None
    
  def __str__(self):
    string = "mv:{"
    first = True
    for item in self.lines:
      string += ("" if first else ", ") + str(item)
      first = False
    string += "}"
    return string
  
  __repr__ = __str__
    
  def setPlayer(self, in_player):
    self.player = in_player
  
  def addLine(self, line):
    self.lines.append(line)
    
  def getLines(self):
    return self.lines
  
  def getPlacedPiece(self):
    return self.lines[0].end
    
  def getSquares(self):
    squares = []
    for line in self.lines:
      for item in line.getFullLine():
        if item not in squares:
          squares.append(item)
    return squares
    
  def isValid(self):
    end = self.lines[0].end
    for line in self.lines:
      if line.end != end:
        return False
    return True
  
  def getScore(self):
    score = 1
    for line in self.lines:
      score += (line.length - 2)
    return score
    
  def getWeightedScore(self, weighting_matrix):
    squares_counted = []
    score = 1
    for line in self.lines:
      for item in line.getWithoutStart():
        if not item in squares_counted:
          squares_counted.append(item)
          score += weighting_matrix[item[0]][item[1]]
    return score
  

class Board:
  __state = []
  __board_size = 0
  __col_row_size = 0
  __move_masks = [(0,1),(1,0),(0,-1),(-1,0),(1,1),(-1,-1),(1,-1),(-1,1)]
  __move_cache = {}
  __refresh_move_cache = True
  __player_move_cache = BLANK
  
  def __init__(self, board_size = 36, blank = False):
    self.__state = []
    self.__move_cache = {}
    self.__refresh_move_cache = True
    self.__player_move_cache = BLANK
    self.__board_size = board_size
    self.__col_row_size = int(math.sqrt(board_size));
    for x in range(0, self.__col_row_size):
      col = []
      for y in range(0, self.__col_row_size):
        col.append(0)
      self.__state.append(col)
    if not blank:
      counter = 0
      for offx in [-1,0]:
        for offy in [-1,0]:
          counter += 1
          self.__state[int(self.__col_row_size/2)+offx][int(self.__col_row_size/2)+offy] = 4/(counter**2-5*counter+8)
          #Use fancy maths to set the starting pieces 
  
  def getBoardSize(self):
    return self.__board_size
    
  def getColRowSize(self):
    return self.__col_row_size
  
  def getScore(self, player):
    score = 0
    for x in range(0, self.__col_row_size):
      for y in range(0, self.__col_row_size):
        score += player == self.__state[x][y]
    return score
    
  def getMoves(self, player, pattern = 0):
    if self.__can_use_move_cache(player):
      return self.move_cache
    possible_moves = []
    for x, y in self.patternForBoard():
      if self.getSquare((x, y)) == player:
        for mask in self.__move_masks:
          line = Line()
          line.setStartPoint((x, y))
          valid_move = True
          offset = 1
          while True:
            if self.getSquare((x+mask[0]*offset, y+mask[1]*offset)) == otherPlayer(player):
              line.addPoint((x+mask[0]*offset, y+mask[1]*offset))
            else:
              break
            offset += 1
          if self.getSquare((x+mask[0]*offset, y+mask[1]*offset)) == BLANK:
            line.setEndPoint((x+mask[0]*offset, y+mask[1]*offset))
          if line.isValid():
            possible_moves.append(line)
    moves = {}
    for line in possible_moves:
      if not line.end in moves.keys():
        moves[line.end] = Move()
        moves[line.end].setPlayer(player)
      moves[line.end].addLine(line)
    self.__set_move_cache(moves, player)
    return moves
    
  def __set_move_cache(self, moves, player):
    self.move_cache = moves
    self.__refresh_move_cache = False
    self.__player_move_cache = player
    
  def __can_use_move_cache(self, player):
    return not self.__refresh_move_cache and player == self.__player_move_cache
    
  def getSquare(self, square):
    x = square[0]
    y = square[1]
    if x >= 0 and x < len(self.__state) and y >= 0 and y < len(self.__state[x]):
      return self.__state[x][y]
    else:
      return None
  
  def setSquare(self, square, player):
    x = square[0]
    y = square[1]
    if x >= 0 and x < len(self.__state) and y >= 0 and y < len(self.__state[x]) and player in [0,1,2]:
      self.__state[x][y] = player
      self.__refresh_move_cache = True
      return True
    else:
      return False
    
  def applyMove(self, move):
    for line in move.lines:
      if not self.applyLine(line, move.player):
        return False
    return True
    
  def applyLine(self, line, player):
    for square in line.getFullLine():
      if not self.setSquare(square, player):
        return False
    return True
    
  def isBoardFull(self):
    for x, y in self.patternForBoard():
      if self.getSquare((x, y)) == BLANK:
        return False
    return True
    
  def canEitherPlayerMove(self, player):
    player1 = self.getMoves(player)
    player2 = self.getMoves(otherPlayer(player))
    return player1 != {} or player2 != {}
    
  def setBoard(self, board):
    old_board = self.__state
    self.__state = copy.deepcopy(board)
    return old_board
    
  def getBoard(self):
    return copy.deepcopy(self.__state)
    
  def getWinner(self):
    p1_score = self.getScore(PLAYER1)
    p2_score = self.getScore(PLAYER2)
    if p1_score > p2_score:
      return PLAYER1
    elif p2_score > p1_score:
      return PLAYER2
    else:
      return PLAYER0
      
  def getCopy(self):
    return copy.deepcopy(self)
    
  def patternForBoard(self):
    for y in range(0, self.__col_row_size):
      for x in range(0, self.__col_row_size):
        yield (x,y)

  def __str__(self):
    string = ""
    first = True
    for y in range(0, self.getColRowSize()):
      if not first: string += "\r\n"
      first = False
      for x in range(0, self.getColRowSize()):
        string += str(self.getSquare((x,y))) + " "
    return string
  
  __repr__ = __str__
