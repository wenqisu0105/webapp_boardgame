import json
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import redis
from utils import get_initial_board, make_move_on_board, initial_board_dataframe
import logging
import numpy as np
from copy import deepcopy
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class GameData(BaseModel):
    gridSize: list
    player1Position: list
    player2Position: list
    sticks: dict


app = FastAPI()

app.mount("/static", StaticFiles(directory="static",html=True), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open('static/index.html', 'r') as f:
        content = f.read()
    return content

@app.get("/api/game-data")
async def get_game_data():
    chess_board = get_initial_board() 
    chess_board_store, ai_pos = initial_board_dataframe(chess_board)
    r.set('chess_board', json.dumps(chess_board_store.tolist()))
    r.set('ai_xy', json.dumps(ai_pos))
    return GameData(
        gridSize=[5, 5], 
        player1Position=[0, 0], 
        player2Position=ai_pos, 
        sticks=chess_board
    )



class Move(BaseModel):
    x: int
    y: int
    pos: int

class MakeMoveResponse(BaseModel):
    x: int
    y: int
    pos: int


# Connect to Redis
r = redis.Redis(host='localhost', port=6379, db=0)

@app.post("/api/make-move")
async def ai_move(move:Move):
    logging.info("AI is making a move")
    logger.info(f"player's move is {move.x, move.y, move.pos}")
    chess_board_store = r.get('chess_board')
    ai_location_bytes = r.get('ai_xy')
    ai_location_str = ai_location_bytes.decode('utf-8')  # Decoding the bytes to a string
    ai_location = json.loads(ai_location_str)
    ai_x, ai_y = ai_location[0], ai_location[1]

    
    if chess_board_store is None:
        raise HTTPException(status_code=400, detail="Game not started")
    chess_board_store = np.array(json.loads(chess_board_store))

    #update the chessboard
    chess_board_store = place_barrier(move.x, move.y, move.pos,chess_board_store)

    # Update the chess board based on the move
    try:
        chess_board_store, ai_move_x, ai_move_y, wall = make_move_on_board(chess_board_store=chess_board_store, ai_pos=[ai_x, ai_y], x=move.x, y=move.y, pos=move.pos,)  
        # Replace with your function to make a move
    except:
        chess_board_store, ai_move_x, ai_move_y, wall = random_step(chess_board_store, my_pos=(ai_x, ai_y), adv_pos=(move.x, move.y),max_step=2)

   
    chess_board_store = place_barrier(ai_move_x, ai_move_y, wall,chess_board_store)
    r.set('chess_board', json.dumps(chess_board_store.tolist()))
    r.set('ai_xy', json.dumps([int(ai_move_x), int(ai_move_y)]))
    return {"x": int(ai_move_x), "y": int(ai_move_y), "pos": int(wall)}

def random_step(chess_board, my_pos, adv_pos, max_step):
        # Moves (Up, Right, Down, Left)
        ori_pos = deepcopy(my_pos)
        moves = ((-1, 0), (0, 1), (1, 0), (0, -1))
        steps = np.random.randint(0, max_step + 1)

        # Random Walk
        for _ in range(steps):
            r, c = my_pos
            dir = np.random.randint(0, 4)
            m_r, m_c = moves[dir]
            my_pos = (r + m_r, c + m_c)

            # Special Case enclosed by Adversary
            k = 0
            while chess_board[r, c, dir] or my_pos == adv_pos:
                k += 1
                if k > 300:
                    break
                dir = np.random.randint(0, 4)
                m_r, m_c = moves[dir]
                my_pos = (r + m_r, c + m_c)

            if k > 300:
                my_pos = ori_pos
                break

        # Put Barrier
        dir = np.random.randint(0, 4)
        r, c = my_pos
        while chess_board[r, c, dir]:
            dir = np.random.randint(0, 4)

        return chess_board, my_pos[0], my_pos[1], dir


@app.post("/api/validate_move")
async def user_move(move:Move):
    logging.info("validating the move")
    chess_board_store = r.get('chess_board')
    chess_board_store = np.array(json.loads(chess_board_store))
    ai_location_bytes = r.get('ai_xy')
    ai_location_str = ai_location_bytes.decode('utf-8')  # Decoding the bytes to a string
    ai_location = json.loads(ai_location_str)
    ai_x, ai_y = ai_location[0], ai_location[1]

    if ai_x==move.x and ai_y==move.y:
        return {"validate":False}
    if chess_board_store[move.x, move.y, move.pos]==True:
        return {"validate":False}
    return {"validate":True}

@app.post("/api/check_endgame")
async def check_end_game(move:Move):
    logging.info("checking if the game ends")
    chess_board_store = r.get('chess_board')
    chess_board_store = np.array(json.loads(chess_board_store))
    ai_location_bytes = r.get('ai_xy')
    ai_location_str = ai_location_bytes.decode('utf-8')  # Decoding the bytes to a string
    ai_location = json.loads(ai_location_str)
    ai_x, ai_y = ai_location[0], ai_location[1]

    human_x, human_y = move.x, move.y

    over, s1, s2 = check_endgame(chess_board_store, [human_x, human_y], [ai_x, ai_y])
    if not over:
        return 0
    if s1 > s2:
        return 1
    return 2




def check_endgame(board, my_pos, adv_pos):
        
        moves = ((-1, 0), (0, 1), (1, 0), (0, -1))
        size = len(board)
        father = dict()
        for r in range(size):
            for c in range(size):
                father[(r, c)] = (r, c)
        def find(pos):
            if father[pos] != pos:
                father[pos] = find(father[pos])
            return father[pos]
        def union(pos1, pos2):
            father[pos1] = pos2
        for r in range(size):
            for c in range(size):
                for dir, move in enumerate(
                    moves[1:3]
                ):  
                    if board[r,c,dir + 1]:
                        continue
                    pos_a = find((r, c))
                    pos_b = find((r + move[0], c + move[1]))
                    if pos_a != pos_b:
                        union(pos_a, pos_b)
        for r in range(size):
            for c in range(size):
                find((r, c))
        p0_r = find(tuple(my_pos))
        p1_r = find(tuple(adv_pos))
        p0_score = list(father.values()).count(p0_r)
        p1_score = list(father.values()).count(p1_r)
        if p0_r == p1_r:
            return False, p0_score, p1_score
        return True, p0_score, p1_score



def place_barrier(x, y, wall, board):
    rows = len(board)
    cols = len(board[0])

    if wall == 0 and x > 0:
        board[x][y][0] = True
        board[x - 1][y][2] = True
    if wall == 2 and x < rows - 1:
        board[x][y][2] = True
        board[x + 1][y][0] = True
    if wall == 3 and y > 0:
        board[x][y][3] = True
        board[x][y - 1][1] = True
    if wall == 1 and y < cols - 1:
        board[x][y][1] = True
        board[x][y + 1][3] = True

    return board

