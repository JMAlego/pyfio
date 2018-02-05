import random, sys
from multiprocessing import Pool

def otherPlayer(player):
  return 1 + player % 2

class RandomAI:
  def pickMove(self, board, player):
    moves = board.getMoves(player)
    if moves == {}: return None
    return random.choice(moves.values())
    
class WeightedAI:
  weighting = [ [2.0, 1.5, 1.5, 1.5, 1.5, 2.0],
                [1.5, 0.7, 0.7, 0.7, 0.7, 1.5],
                [1.5, 0.7, 1.0, 1.0, 0.7, 1.5],
                [1.5, 0.7, 1.0, 1.0, 0.7, 1.5],
                [1.5, 0.7, 0.7, 0.7, 0.7, 1.5],
                [2.0, 1.5, 1.5, 1.5, 1.5, 2.0] ]
  
  def pickMove(self, board, player):
    moves = board.getMoves(player)
    if moves == {}: return None
    best_move = (0, None)
    for piece, move in moves.items():
      x = piece[0]
      y = piece[1]
      score = self.weighting[x][y] * move.getScore()
      if best_move[0] < score:
        best_move = (score, move)
      elif best_move[0] == score and bool(random.getrandbits(1)):
        best_move = (score, move)
      elif best_move[0] == 0:
        best_move = (score, move)
    return best_move[1]

class WeightedV2AI:
  weighting = [ [ 4.0, -0.7, 3.3, 3.3, -0.7,  4.0],
                [-0.7, -0.7, 0.2, 0.2, -0.7, -0.7],
                [ 3.3,  0.2, 1.0, 1.0,  0.2,  3.3],
                [ 3.3,  0.2, 1.0, 1.0,  0.2,  3.3],
                [-0.7, -0.7, 0.2, 0.2, -0.7, -0.7],
                [ 4.0, -0.7, 3.3, 3.3, -0.7,  4.0] ]
  
  def pickMove(self, board, player):
    moves = board.getMoves(player)
    if moves == {}: return None
    best_move = (0, None)
    for piece, move in moves.items():
      x = piece[0]
      y = piece[1]
      score = self.weighting[x][y] * move.getScore()
      if best_move[0] < score:
        best_move = (score, move)
      elif best_move[0] == score and bool(random.getrandbits(1)):
        best_move = (score, move)
      elif best_move[0] == 0:
        best_move = (score, move)
    return best_move[1]
    
class RecursiveAI:
  def __init__(self, number_of_moves = 2, max_depth = 6):
    self.number_of_moves = number_of_moves
    self.max_depth = max_depth
  
  def recur(self, board, player, depth = 0, number_of_moves = 4, max_depth = 3):
    if max_depth == depth:
      return [board]
    moves = board.getMoves(player)
    if moves == {}: return None
    scored_moves = {}
    for key, move in moves.items():
      score = move.getScore()
      if not score in scored_moves.keys():
        scored_moves[score] = []
      scored_moves[score].append(move)
    best_moves = []
    for score in sorted(scored_moves.keys(), reverse = True):
      for move in scored_moves[score]:
        if len(best_moves) < number_of_moves:
          best_moves.append(move)
        else:
          break
      if len(best_moves) >= number_of_moves:
        break
    player = otherPlayer(player)
    results = []
    for move in best_moves:
      new_board = board.getCopy()
      new_board.applyMove(move)
      if depth == 0:
        result = self.recur(new_board, player, depth+1, number_of_moves, max_depth)
        if result != None and result != []:
          for item in result:
            if item != None:
              results.append((move, item))
      else:
        result = self.recur(new_board, player, depth+1, number_of_moves, max_depth)
        if result != None and result != []:
          for item in result:
            if item != None:
              results.append(item)
    return results
  
  def pickMove(self, board, player):
    moves = board.getMoves(player)
    if moves == {}: return None
    elif len(moves) == 1:
      return moves.values()[0]
    moves = self.recur(board.getCopy(), player, number_of_moves = self.number_of_moves, max_depth = self.max_depth)
    if moves == [] or moves == {} or moves == None:
      ai = WeightedV2AI()
      return ai.pickMove(board, player)
    best_move = (0, None)
    for move, pos_board in moves:
      score = pos_board.getScore(player)
      if best_move[0] < score:
        best_move = (score, move)
      elif best_move[0] == score and bool(random.getrandbits(1)):
        best_move = (score, move)
      elif best_move[0] == 0:
        best_move = (score, move)
    return best_move[1]
    
class WeightedRecursiveAI:           
  weighting = [ [ 4.0, -0.7, 3.3, 3.3, -0.7,  4.0],
                [-0.7, -0.7, 0.2, 0.2, -0.7, -0.7],
                [ 3.3,  0.2, 1.0, 1.0,  0.2,  3.3],
                [ 3.3,  0.2, 1.0, 1.0,  0.2,  3.3],
                [-0.7, -0.7, 0.2, 0.2, -0.7, -0.7],
                [ 4.0, -0.7, 3.3, 3.3, -0.7,  4.0] ]
                
  def __init__(self, number_of_moves = 2, max_depth = 6):
    self.number_of_moves = number_of_moves
    self.max_depth = max_depth

  def recur(self, board, player, depth = 0, number_of_moves = 4, max_depth = 3):
    if max_depth == depth:
      return [board]
    moves = board.getMoves(player)
    if moves == {}: return None
    scored_moves = {}
    for key, move in moves.items():
      score = move.getWeightedScore(self.weighting)
      if not score in scored_moves.keys():
        scored_moves[score] = []
      scored_moves[score].append(move)
    best_moves = []
    for score in sorted(scored_moves.keys(), reverse = True):
      for move in scored_moves[score]:
        if len(best_moves) < number_of_moves:
          best_moves.append(move)
        else:
          break
      if len(best_moves) >= number_of_moves:
        break
    player = otherPlayer(player)
    results = []
    for move in best_moves:
      new_board = board.getCopy()
      new_board.applyMove(move)
      if depth == 0:
        result = self.recur(new_board, player, depth+1, number_of_moves, max_depth)
        if result != None and result != []:
          for item in result:
            if item != None:
              results.append((move, item))
      else:
        result = self.recur(new_board, player, depth+1, number_of_moves, max_depth)
        if result != None and result != []:
          for item in result:
            if item != None:
              results.append(item)
    return results
  
  def pickMove(self, board, player):
    moves = board.getMoves(player)
    if moves == {}: return None
    elif len(moves) == 1:
      return moves.values()[0]
    moves = self.recur(board.getCopy(), player, number_of_moves = self.number_of_moves, max_depth = self.max_depth)
    if moves == [] or moves == {} or moves == None:
      ai = WeightedV2AI()
      return ai.pickMove(board, player)
    best_move = (0, None)
    for move, pos_board in moves:
      x, y = move.getPlacedPiece()
      score = pos_board.getScore(player) * self.weighting[x][y]
      if best_move[0] < score:
        best_move = (score, move)
      elif best_move[0] == score and bool(random.getrandbits(1)):
        best_move = (score, move)
      elif best_move[0] == 0:
        best_move = (score, move)
    return best_move[1]