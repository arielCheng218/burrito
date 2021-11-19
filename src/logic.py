import chess
import random

board = chess.Board()

def get_legal_squares_for_square(square):
    legal_squares_for_square = []
    for legal_move in list(board.legal_moves):
        if str(legal_move.uci())[:2] == square[:2]:
            legal_squares_for_square.append(str(legal_move.uci())[2:4])
    return legal_squares_for_square

def make_move(move):
    board.push_uci(move)

def make_random_move():
    legal_moves = []
    for move in list(board.legal_moves):
        legal_moves.append(str(move.uci()))
    if len(legal_moves) != 0:
        random_move = random.choice(legal_moves)
        board.push_uci(random_move)
        return random_move
    return None

def check_en_passant(move):
    for legal_move in list(board.legal_moves):
        if str(legal_move.uci()) == move and board.is_en_passant(legal_move):
            return True
    return False

def game_has_ended():
    return board.is_game_over()