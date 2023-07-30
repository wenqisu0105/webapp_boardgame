from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

class GameData(BaseModel):
    gridSize: list
    player1Position: list
    player2Position: list
    sticks: dict

test_sticks = {
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



app = FastAPI()

app.mount("/static", StaticFiles(directory="static",html=True), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open('static/index.html', 'r') as f:
        content = f.read()
    return content

@app.get("/api/game-data")
async def get_game_data():
    return GameData(
        gridSize=[5, 5], 
        player1Position=[0, 0], 
        player2Position=[3, 2], 
        sticks=test_sticks
    )
