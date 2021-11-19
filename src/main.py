
import chess
from train_data import *
from model import model
from ui import display_game_view

# TODO:
# [-] minimax algorithm
# [ ] evaluation function - neural net 

board = chess.Board()

def main():
  display_game_view()

if __name__ == "__main__":
  main()