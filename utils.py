import numpy as np
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

BOARD_SIZE = 5

def get_initial_board():
    board = {
  "0,0": [],
  "0,1": [],
  "0,2": [],
  "0,3": [],
  "0,4": [],
  "1,0": [],
  "1,1": [0,1,2,3],
  "1,2": [0,1,2,3],
  "1,3": [],
  "1,4": [],
  "2,0": [0,1,2,3],
  "2,1": [],
  "2,2": [],
  "2,3": [],
  "2,4": [0,1,2,3],
  "3,0": [],
  "3,1": [],
  "3,2": [],
  "3,3": [],
  "3,4": [],
  "4,0": [],
  "4,1": [],
  "4,2": [],
  "4,3": [],
  "4,4": []
}
    return board


def make_move_on_board(chess_board_store, x, y, pos):
    logging.info(f"{chess_board_store, x, y, pos}")
    chess_board_store[x, y, pos] = True
    return chess_board_store


def initial_board_dataframe(client_board):
    chess_board = np.zeros((BOARD_SIZE, BOARD_SIZE, 4), dtype=bool)
    
    # Index in dim2 represents [Up, Right, Down, Left] respectively
    # Set borders
    chess_board[0, :, 0] = True
    chess_board[:, 0, 3] = True
    chess_board[-1, :, 2] = True
    chess_board[:, -1, 1] = True

    for coord, sticks in client_board.items():
        x = int(coord[0])
        y = int(coord[-1])
        for wall in sticks:
            chess_board[x,y,wall] = True
    
    return chess_board
