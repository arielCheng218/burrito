
import random
# TODO: get random opening move instead of fixed
import chess
import chess.polyglot as book

def get_eval(pos):
  if not pos.is_game_over():
    material = get_material_points(pos.fen())
    king_safety = get_king_safety(pos)
    center_control = get_center_control(pos)
    return material + king_safety + center_control
  elif pos.is_checkmate():
    print("Search found checkmate")
    if pos.turn == chess.WHITE:
      pos.pop()
      return -100000
    else:
      pos.pop()
      return 100000
  elif pos.is_stalemate():
    return 0

lastMove = ""

def checkOpeningMove(pos):
  with book.open_reader("openings.bin") as reader:
    if len(list(reader.find_all(pos))) == 0:
      return (False, "")
    else:
      return (True, list(reader.find_all(pos))[random.choice(range(0, len(list(reader.find_all(pos)))))].move)

def minimax(pos, depth, isMax, alpha = -100000, beta = 100000):
  global lastMove
  if checkOpeningMove(pos)[0] == True:
    return (str(checkOpeningMove(pos)[1].uci()), 0)
  else:
    if depth == 0: 
      eval = get_eval(pos)
      return (lastMove, eval)
    if isMax:
      # is maximizing player
      maxEval = -100000
      bestMove = ""
      for move in list(pos.legal_moves):
        pos.push_uci(str(move.uci()))
        lastMove = str(move.uci())
        t = minimax(pos, depth - 1, not isMax)
        if t[1] > maxEval:
          maxEval = t[1]
          bestMove = str(move.uci())
        alpha = max(alpha, maxEval)
        if maxEval >= beta:
          break
        pos.pop()
      return (bestMove, maxEval)
    else:
      # is minimizing player
      minEval = 100000
      bestMove = ""
      for move in list(pos.legal_moves):
        pos.push_uci(str(move.uci()))
        lastMove = str(move.uci())
        t = minimax(pos, depth - 1, not isMax)
        if t[1] < minEval:
          minEval = t[1]
          bestMove = str(move.uci())
        beta = min(beta, minEval)
        if minEval <= alpha:
          break
        pos.pop()
      return (bestMove, minEval)

def get_material_points(fen):
  value = 0
  piece_values = {
    "P": 1,
    "N": 3,
    "B": 4,
    "R": 5,
    "Q": 8,
    "p": -1,
    "n": -3,
    "b": -4,
    "r": -5,
    "q": -8,
  }
  for char in fen:
    if char in piece_values.keys():
      value += piece_values[char]
  return value

def get_king_safety(pos):
  if pos.turn == chess.WHITE and pos.is_check():
    return -4
  elif pos.turn == chess.BLACK and pos.is_check():
    return 4
  else:
    return 0

def get_center_control(pos):
  return len(list(pos.legal_moves)) * 0.1