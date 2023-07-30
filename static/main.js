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
          
          if (sticks.includes(1)) {
            cell.classList.add('red-stick-bottom');
        }
          
          if (sticks.includes(2)) {
            inner.classList.add('red-stick-left');
      }

          if (sticks.includes(3)) {
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

  form.addEventListener('submit', (event) => {
    event.preventDefault();
    
    const x = document.getElementById('x').value;
    const y = document.getElementById('y').value;
    const pos = document.getElementById('pos').value;

    const cellId = `cell${x},${y}`;
    const innerId = `inner${x},${y}`;

    const cell = document.getElementById(cellId);
    const inner = document.getElementById(innerId);

    if (pos=='top'){
      cell.classList.add('red-stick-top');
    }
    if (pos=='bottom') {
      cell.classList.add('red-stick-bottom');
    }
    console.log("id looking at is", innerId)
    if (pos=='left') {
      inner.classList.add('red-stick-left');
    }

    if (pos=='right') {
      inner.classList.add('red-stick-right');
    }

  });
  
  await initializeBoard();
});
