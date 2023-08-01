const board = document.getElementById('board');
async function initializeBoard() {
  const response = await fetch('/api/game-data');
  const gameData = await response.json();



  for (let i = 0; i < gameData.gridSize[0]; i++) {
      for (let j = 0; j < gameData.gridSize[1]; j++) {
          const cell = document.createElement('li');
          cell.className = 'cell';
          cell.id = `cell${i},${j}`

          const inner = document.createElement('div');
          const coord = `${i},${j}`
          inner.id = `inner${i},${j}`
          inner.className = 'inner';
          cell.appendChild(inner);

          const sticks = gameData.sticks[coord];


          if (sticks.includes(0)) {
            cell.classList.add('red-stick-top');
        }
          
          if (sticks.includes(2)) {
            cell.classList.add('red-stick-bottom');
        }
          
          if (sticks.includes(3)) {
            inner.classList.add('red-stick-left');
      }

          if (sticks.includes(1)) {
            inner.classList.add('red-stick-right');
        }

          // check for player positions and add player class
          if (gameData.player1Position[0] === i && gameData.player1Position[1] === j) {
            inner.classList.add('player1');
            inner.textContent = 'A';
          } else if (gameData.player2Position[0] === i && gameData.player2Position[1] === j) {
            inner.classList.add('player2');
            inner.textContent = 'B';
          }

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

    

    const cellId = `cell${x},${y}`;
    const innerId = `inner${x},${y}`;

    const cell = document.getElementById(cellId);
    const inner = document.getElementById(innerId);
    let dir_map = 0;

    if (pos=='top'){
      cell.classList.add('red-stick-top');
      dir_map = 0;
    }
    if (pos=='bottom') {
      cell.classList.add('red-stick-bottom');
      dir_map = 2;
    }
    if (pos=='left') {
      inner.classList.add('red-stick-left');
      dir_map = 3;
    }

    if (pos=='right') {
      inner.classList.add('red-stick-right');
      dir_map = 1;
    }
    
    const response = await fetch('/api/make-move', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ x: 1, y: 2, pos: 3 })
    });
    if (!response.ok) {
      console.error('There was an error making the move:', response);
    } else {
      const responseBody = await response.json(); // parse the response body as JSON

      // log the x, y, pos values
      console.log(responseBody.x, responseBody.y, responseBody.pos);}

  });

  await initializeBoard();
});
