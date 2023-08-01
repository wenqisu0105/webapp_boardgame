import json
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
# from .ai_agent import SmartAgent
import redis
from utils import get_initial_board, make_move_on_board, initial_board_dataframe
import logging
import numpy as np
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
    chess_board_store = initial_board_dataframe(chess_board)
    r.set('chess_board', json.dumps(chess_board_store.tolist()))
    return GameData(
        gridSize=[5, 5], 
        player1Position=[0, 0], 
        player2Position=[3, 2], 
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
    logger.info(f"player's move is {move.x, move.y, move.pos}")
    chess_board_store = r.get('chess_board')
    if chess_board_store is None:
        raise HTTPException(status_code=400, detail="Game not started")
    chess_board_store = np.array(json.loads(chess_board_store))

    # Update the chess board based on the move
    
    chess_board_store = make_move_on_board(chess_board_store, move.x, move.y, move.pos)  # Replace with your function to make a move
    r.set('chess_board', json.dumps(chess_board_store.tolist()))
    logger.info(f"new chess baord has data frame {chess_board_store}")
    
    return {"x": move.x, "y": move.y, "pos": move.pos}




