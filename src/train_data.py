import chess
import random
from algorithm import *

board = chess.Board()

def char_value(c):
  if c.isupper():
    return 1
  else:
    return -1

def fen_to_input(fen):
  piece_mask = []
  k_mask = []
  q_mask = []
  r_mask = []
  b_mask = []
  n_mask = []
  p_mask = []
  for char in fen:
    if char == " ":
      break
    if char != "/":
      piece_mask.append(char_value(char))
      if char == "k" or char == "K":
        k_mask.append(char_value(char))
      elif char == "q" or char == "Q":
        q_mask.append(char_value(char))
      elif char == "r" or char == "R":
        r_mask.append(char_value(char))
      elif char == "b" or char == "B":
        b_mask.append(char_value(char))
      elif char == "n" or char == "N":
        n_mask.append(char_value(char))
      elif char == "p" or char == "P":
        p_mask.append(char_value(char))
      else:
        for list in [piece_mask, k_mask, q_mask, r_mask, b_mask, n_mask, p_mask]:
          for _ in range(int(char)):
            list.append(0)
  return piece_mask + k_mask + q_mask + r_mask + b_mask + n_mask + p_mask 

# training data (positions from self play)
positions = []

def play_game():
  global positions
  while not board.is_game_over():
    search_depth = random.randint(1, 3)
    t = minimax(board, search_depth, board.turn == chess.WHITE)
    board.push_uci(t[0])
    print("\n", board, "\n", t[0])
    input = fen_to_input(board.fen())
    positions.append(input)
  positions = []

def process_data():
  print("game")
  new_X = []
  new_y = []
  outcome = 0
  if board.outcome == board.is_checkmate():
    if board.turn == chess.WHITE:
      outcome = 1
    else:
      outcome = -1
  for pos in positions:
    new_X.append(pos)
    new_y.append(outcome)
  return new_X, new_y

def get_training_data():
  X = []
  y = []
  play_game()
  print("game finished")
  X, y = process_data()
  for i in range(100):
    play_game()
    new_X, new_y = process_data()
    X += new_X
    y += new_y
  return X, y