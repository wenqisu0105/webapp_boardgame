from copy import deepcopy
import numpy as np
import logging

from ai_agent import SmartAgent
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
  "1,1": [],
  "1,2": [],
  "1,3": [],
  "1,4": [],
  "2,0": [],
  "2,1": [],
  "2,2": [],
  "2,3": [],
  "2,4": [],
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


def make_move_on_board(chess_board_store, ai_pos, x, y, pos):
    
    chess_board_store[x, y, pos] = True
    ai_agent = SmartAgent()
    try:
        move, wall = ai_agent.step(chess_board=chess_board_store, my_pos=ai_pos, adv_pos=[x,y], max_step=4)
    except Exception:
        move, wall = random_walk(tuple(ai_pos[0], ai_pos[1]), tuple(x,y))
        
    chess_board_store[move[0], move[1], wall] = True
    return chess_board_store, move[0], move[1], wall


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
    
    ai_pos = [2,2]
    
    return chess_board, ai_pos

def random_walk(self, my_pos, adv_pos):
        """
        Randomly walk to the next position in the board.

        Parameters
        ----------
        my_pos : tuple
            The position of the agent.
        adv_pos : tuple
            The position of the adversary.
        """
        ori_pos = deepcopy(my_pos)
        steps = np.random.randint(0, self.max_step + 1)
        # Random Walk
        for _ in range(steps):
            r, c = my_pos
            dir = np.random.randint(0, 4)
            m_r, m_c = self.moves[dir]
            my_pos = (r + m_r, c + m_c)

            # Special Case enclosed by Adversary
            k = 0
            while self.chess_board[r, c, dir] or my_pos == adv_pos:
                k += 1
                if k > 300:
                    break
                dir = np.random.randint(0, 4)
                m_r, m_c = self.moves[dir]
                my_pos = (r + m_r, c + m_c)

            if k > 300:
                my_pos = ori_pos
                break

        # Put Barrier
        dir = np.random.randint(0, 4)
        r, c = my_pos
        while self.chess_board[r, c, dir]:
            dir = np.random.randint(0, 4)

        return my_pos, dir