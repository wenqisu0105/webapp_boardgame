
const board = document.getElementById('board');

function createCellElement(i, j, sticks, player1Position, player2Position) {
  const cell = document.createElement('li');
  cell.className = 'cell';
  cell.id = `cell${i},${j}`

  const inner = document.createElement('div');
  inner.id = `inner${i},${j}`;
  inner.className = 'inner';
  cell.appendChild(inner);

  if (sticks.includes(0)) cell.classList.add('red-stick-top');
  if (sticks.includes(2)) cell.classList.add('red-stick-bottom');
  if (sticks.includes(3)) inner.classList.add('red-stick-left');
  if (sticks.includes(1)) inner.classList.add('red-stick-right');

  if (player1Position[0] === i && player1Position[1] === j) {
    inner.classList.add('player1');
    inner.textContent = 'A';
  } else if (player2Position[0] === i && player2Position[1] === j) {
    inner.classList.add('player2');
    inner.textContent = 'B';
  }

  return cell;
}

async function initializeBoard() {
  const response = await fetch('/api/game-data');
  const gameData = await response.json();

  for (let i = 0; i < gameData.gridSize[0]; i++) {
    for (let j = 0; j < gameData.gridSize[1]; j++) {
      const coord = `${i},${j}`;
      const cell = createCellElement(i, j, gameData.sticks[coord], gameData.player1Position, gameData.player2Position);
      board.appendChild(cell);
    }
  }
}


document.addEventListener('DOMContentLoaded', async (event) => {
  const form = document.getElementById('userInputForm');
  const errorMessageElement = document.getElementById('error_message');

  form.addEventListener('submit', async (event) => {
    event.preventDefault();

    const x = document.getElementById('x').value;
    const y = document.getElementById('y').value;
    const pos = document.getElementById('pos').value;

    const check_wall = `${x}-${y}-${pos}`
    const myArray = ['0-0-left', '0-0-top', '1-0-left','2-0-left','3-0-left','4-0-left',
    '4-0-bottom','0-1-top','0-2-top','0-3-top','0-4-top','1-4-right', '2-4-right','3-4-right',
    '4-4-right','4-4-bottom', '4-3-bottom','4-2-bottom','4-1-bottom']

    console.log('check wall is ', check_wall)

    if (myArray.includes(check_wall)){
      errorMessageElement.innerText = 'You are putting the wall in a boundary!!';
      return;
    } else {
      errorMessageElement.innerText = '';
    }
    const Mapping1 = {
      'top': 0,
      'bottom': 2,
      'left': 3,
      'right': 1
    };
   
    
    const validate = await fetch('/api/validate_move', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ x: x, y: y, pos: Mapping1[pos]})
    });

    if (!validate.ok) {
      console.error('There was an error sending the request', validate);
    } else {
      const validate_pass = await validate.json();// parse the response body as JSON
      console.log(validate_pass.validate)
      if (validate_pass.validate){
        updateCell(x, y, pos, 'player1', 'A')

        const check_end_game_1 = await fetch('/api/check_endgame', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ x: x, y: y, pos: Mapping1[pos] })
        });
        if (!check_end_game_1.ok) {
          console.error('There was an error checking whether the game ends:', response);
        }
        else {
          result = await check_end_game_1.json();
          if (result==1){
            console.log('A wins')
            errorMessageElement.innerText = 'YOU WIN!'
          }
          if (result==2){
            console.log('B wins')
            errorMessageElement.innerText = 'YOU LOSE!'
          }
        }
        
        
        
        const response = await fetch('/api/make-move', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ x: x, y: y, pos: Mapping1[pos] })
        });

        if (!response.ok) {
          console.error('There was an error making the move:', response);
        } else {
          const responseBody = await response.json(); // parse the response body as JSON
    
          // log the x, y, pos values
          console.log(responseBody.x, responseBody.y, responseBody.pos);
          let { x: ai_x, y: ai_y, pos: ai_pos } = responseBody;
          const posMapping = {
            0:'top',
            2:'bottom',
            3:'left',
            1:'right'
          };
          updateCell(ai_x, ai_y, posMapping[ai_pos], 'player2', 'B');

          const check_end_game = await fetch('/api/check_endgame', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({ x: x, y: y, pos: Mapping1[pos] })
          });
          if (!check_end_game.ok) {
            console.error('There was an error checking whether the game ends:', response);
          }
          else {
            result = await check_end_game.json();
            if (result==1){
              console.log('A wins')
              errorMessageElement.innerText = 'YOU WIN!'
            }
            if (result==2){
              console.log('B wins')
              errorMessageElement.innerText = 'YOU LOSE!'
            }
          }
          
        }}
      else{
        errorMessageElement.innerText = 'Not a valid move!!'
      }} 

    

    

      
  });

  await initializeBoard();
});


function updateCell(x, y, pos, playerClass, playerSymbol) {
  const cellId = `cell${x},${y}`;
  const innerId = `inner${x},${y}`;
  console.log("cellID is", cellId)
  const cell = document.getElementById(cellId);
  const inner = document.getElementById(innerId);
  let dir_map = 0;

  if (pos == 'top') {
    cell.classList.add('red-stick-top');
    dir_map = 0;
  }
  if (pos == 'bottom') {
    cell.classList.add('red-stick-bottom');
    dir_map = 2;
  }
  if (pos == 'left') {
    inner.classList.add('red-stick-left');
    dir_map = 3;
  }
  if (pos == 'right') {
    inner.classList.add('red-stick-right');
    dir_map = 1;
  }

  const existingPlayerCell = document.querySelector(`.${playerClass}`);
  if (existingPlayerCell) {
    existingPlayerCell.classList.remove(playerClass);
    existingPlayerCell.textContent = '';
  }
  inner.classList.add(playerClass);
  inner.textContent = playerSymbol;
}



