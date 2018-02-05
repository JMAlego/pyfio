#!/usr/bin/env python
# -*- coding: utf-8 -*-

import threading, time, gobject, gtk, monitor, state, ai, copy

PLAYER0 = BLANK   = BLUE  = 0
PLAYER1 = PLAYERA = RED   = 1
PLAYER2 = PLAYERB = WHITE = 2

gobject.threads_init()

class GameThread(threading.Thread):

  def __init__(self, game_board, board_size, state_label, board_containers):
    super(GameThread, self).__init__()
    self.game_board = game_board
    self.board_size = board_size
    self.board_state = state.Board(blank = True)
    self.state_label = state_label
    self.board_containers = board_containers
    self.highlight = {"green":[],"orange":[]}
    self.label_text = ""
    self.cap = monitor.Capture(brightness = (128.0/255.0), contrast = (91.0/255.0), exposure = (2343.0/18750.0)) 
    self.quit = False

  def update_labels(self, counter):
    self.state_label.set_markup("<span size='36000'>"+self.label_text+"</span>")
    mirror_x = False
    mirror_y = True
    flip = True
    rotate = True
    for x in range(0, self.board_size):
      for y in range(0, self.board_size):
        u_x = x
        u_y = y
        if rotate:
          u_x, u_y = u_y, u_x
        if flip:
          u_x = (self.board_size-1) - u_x
          u_y = (self.board_size-1) - u_y
        if mirror_x:
          u_x = (self.board_size-1) - u_x
        if mirror_y:
          u_y = (self.board_size-1) - u_y
        if self.board_state.getSquare((x, y)) == 1:
          self.game_board[u_x][u_y].modify_fg(gtk.STATE_NORMAL, gtk.gdk.color_parse("red"))
        elif self.board_state.getSquare((x, y)) == 2:
          self.game_board[u_x][u_y].modify_fg(gtk.STATE_NORMAL, gtk.gdk.color_parse("white"))
        else:
          self.game_board[u_x][u_y].modify_fg(gtk.STATE_NORMAL, gtk.gdk.color_parse("blue"))
        if (x, y) in self.highlight["green"]:
          self.board_containers[u_x][u_y].modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("green"))
        elif (x, y) in self.highlight["orange"]:
          self.board_containers[u_x][u_y].modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("orange"))
        else:
          self.board_containers[u_x][u_y].modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("blue"))
    return False

  def run(self):
    counter = 0
    first = True
    found_initial_state = False
    player = PLAYER1
    last_steady_state = None
    ai_made_move = False
    ai_move = None
    ai_new_board_state = state.Board()
    ai_player = ai.RecursiveAI()
    game_done = False
    valid_player_moves = None
    complete_board = state.Board()
    while not self.quit and not game_done:
      if first:
        self.label_text = "Initialising..."
        gobject.idle_add(self.update_labels, counter)
        first = False
      else:
        counter += 1
        new_state = None
        gobject.idle_add(self.update_labels, counter)
        while new_state == None and not self.quit:
          new_state = self.cap.getBoard()
        self.board_state.setBoard(new_state)
        if (new_state == state.INITIAL_STATES[0] or new_state == state.INITIAL_STATES[1]) and not found_initial_state:
          found_initial_state = True
          print "Found initial state."
          last_steady_state = copy.deepcopy(new_state)
          valid_player_moves = self.board_state.getMoves(player)
        #Actual Logic
        if found_initial_state:
          #If no change
          if last_steady_state == new_state:
            if self.board_state.isBoardFull() and found_initial_state:
              complete_board.setBoard(self.board_state.getBoard())
              game_done = True
              print "test1"
              break
            elif not self.board_state.canEitherPlayerMove(player) and found_initial_state:
              complete_board.setBoard(self.board_state.getBoard())
              game_done = True
              print "test2"
              break
            print "Same"
            if player == PLAYER1:
              self.label_text = "Waiting for your move (you are red)..."
            else:
              if ai_made_move:
                self.label_text = "Please complete my move."
              else:
                self.label_text = "Please complete my move."
                ai_new_board_state.setBoard(self.board_state.getBoard())
                picked_move = ai_player.pickMove(ai_new_board_state, PLAYER2)
                if picked_move != None:
                  ai_new_board_state.applyMove(picked_move)
                  self.highlight["orange"] = picked_move.getSquares()
                  ai_made_move = True
                else:
                  self.label_text = "Skipping Move."
                  gobject.idle_add(self.update_labels, counter)
                  time.sleep(1)
                  player = state.otherPlayer(player)
                  ai_made_move = True
          else:
            print "Different"
            if player == PLAYER2:
              print "P2 Start"
              if ai_made_move:
                if ai_new_board_state.getBoard() == self.board_state.getBoard():
                  player = state.otherPlayer(player)
                  ai_made_move = False
                  last_steady_state = ai_new_board_state.getBoard()
                  valid_player_moves = ai_new_board_state.getMoves(player)
                  self.highlight["orange"] = []
                  self.label_text = "Waiting for your move (you are red)..."
                  print "Made AI move"
            else:
              print "P1 Start"
              if valid_player_moves == {}:
                player = state.otherPlayer(player)
                self.label_text = "You can't move so I'll skip your turn."
                gobject.idle_add(self.update_labels, counter)
                time.sleep(1)
                break
              for square, move in valid_player_moves.items():
                actual_move = state.Move()
                actual_move.setPlayer(player)
                if self.board_state.getSquare(square) == player:
                  print square, last_steady_state[square[0]][square[1]]
                  print self.board_state.getBoard(), last_steady_state
                if self.board_state.getSquare(square) == player and last_steady_state[square[0]][square[1]] == BLANK:
                  anyline = False
                  for line in move.lines:
                    all_placed = True
                    for place in line.getFullLine():
                      if self.board_state.getSquare(place) != player:
                        print "Line part not found"
                        all_placed = False
                    if all_placed:
                      actual_move.addLine(line)
                      anyline = True
                  if anyline and len(move.lines) == len(actual_move.lines):
                    print "Detected move...",
                    if actual_move.isValid():
                      print "and it's valid."
                      player = state.otherPlayer(player)
                      new_steady_state = state.Board()
                      new_steady_state.setBoard(last_steady_state)
                      print new_steady_state.applyMove(actual_move)
                      last_steady_state = new_steady_state.getBoard()
                      print last_steady_state, actual_move
                      self.label_text = "Player move made."
                      ai_made_move = False
                      break
                    else:
                      print "but it's not valid."
            
        gobject.idle_add(self.update_labels, counter)
      
    player1_score = complete_board.getScore(PLAYER1)
    player2_score = complete_board.getScore(PLAYER2)
    if player1_score == player2_score:
      self.label_text = "Game Complete! The game is a draw."
    elif player1_score > player2_score:
      self.label_text = "Game Complete! Player 1 is the winner"
    elif player2_score > player1_score:
      self.label_text = "Game Complete! Player 1 is the winner"
    gobject.idle_add(self.update_labels, counter)
          

def main(board_size = 6):
  main_window = gtk.Window()
  main_window.set_default_size(800,500)
  state_label = gtk.Label()
  state_label.set_use_markup(gtk.TRUE)
  
  container = gtk.Table(4, 2, False)
  
  container.attach(state_label, 1, 2, 0, 1)
  
  board_labels = []
  board_containers = []
  for x in range(0, board_size):
    col = []
    col2 = []
    for y in range(0, board_size):
      col.append(gtk.Label())
      col2.append("")
    board_labels.append(col)
    board_containers.append(col2)
  board_container = gtk.EventBox()
  
  game_board = gtk.Table(board_size, board_size, True)
  game_board.set_size_request(500,500)
  game_board.set_col_spacings(2)
  game_board.set_row_spacings(2)
  
  
  for x in range(0, board_size):
    for y in range(0, board_size):
      cont = gtk.EventBox()
      cont.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("blue"))
      board_labels[x][y].set_use_markup(gtk.TRUE)
      board_labels[x][y].set_markup("<span size='60000'>●</span>")
      board_labels[x][y].modify_fg(gtk.STATE_NORMAL, gtk.gdk.color_parse("blue"))
      cont.add(board_labels[x][y])
      board_containers[x][y] = cont
      game_board.attach(cont, x, x+1, y, y+1)
  
  board_container.add(game_board)
  container.attach(board_container, 0, 1, 0, 4)
  
  main_window.add(container)
  
  main_window.show_all()
  main_window.connect("destroy", lambda _: gtk.main_quit())
  
  game_thread = GameThread(board_labels, board_size, state_label, board_containers)
  game_thread.start()
  
  gtk.main()
  
  game_thread.quit = True

if __name__ == "__main__":
  main()
