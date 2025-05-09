function xorSum(piles) {
    return piles.reduce((a, b) => a ^ b, 0);
}

function bestMove(piles) {
    let sum = xorSum(piles);
    
    // First try to find a winning move
    if (sum !== 0) {
        for (let i = 0; i < piles.length; i++) {
            let target = piles[i] ^ sum;
            if (target < piles[i]) {
                return [i, piles[i] - target];
            }
        }
    }
    
    // If no winning move, take one stone from the largest pile
    let maxPileIndex = piles.indexOf(Math.max(...piles));
    return [maxPileIndex, 1];
}

function updateGame() {
    let gameBoard = document.getElementById("game-board");
    gameBoard.innerHTML = "";
    
    for (let i = 0; i < piles.length; i++) {
        let row = document.createElement("div");
        row.className = "pile-row";
        row.innerHTML = `<span class="row-label">Row ${i + 1} </span><span class="stones-container"></span>`;
        
        let container = row.querySelector('.stones-container');
        for (let j = 0; j < piles[i]; j++) {
            let stone = document.createElement("span");
            stone.className = "stone";
            stone.dataset.row = i;
            stone.dataset.position = j;
            stone.textContent = "🪨";
            container.appendChild(stone);
        }
        
        // Add invisible stones to maintain spacing
        for (let j = piles[i]; j < maxPileSize; j++) {
            let spacer = document.createElement("span");
            spacer.className = "stone-spacer";
            container.appendChild(spacer);
        }
        
        gameBoard.appendChild(row);
    }
    
    document.querySelectorAll('.stone').forEach(stone => {
        stone.addEventListener('click', handleStoneClick);
    });
    
    if (piles.every(x => x === 0)) {
        setTimeout(() => {
            alert(piles === originalPiles ? "Game ready!" : 
                  lastMover === 'ai' ? "AI wins! Click Restart to play again." : 
                  "You win! Click Restart to play again.");
        }, 100);
    }
}

function handleStoneClick(event) {
    const row = parseInt(event.target.dataset.row);
    const position = parseInt(event.target.dataset.position);
    const stonesToRemove = piles[row] - position;
    
    if (stonesToRemove > 0 && stonesToRemove <= piles[row]) {
        lastMover = 'player';
        piles[row] -= stonesToRemove;
        updateGame();
        
        if (!piles.every(x => x === 0)) {
            setTimeout(aiMove, 500);
        }
    }
}

function aiMove() {
    let move = bestMove(piles);
    if (move) {
        lastMover = 'ai';
        piles[move[0]] -= move[1];
        updateGame();
    }
}

function restartGame() {
    originalPiles = generateInitialPiles();
    piles = [...originalPiles];
    maxPileSize = Math.max(...originalPiles);
    lastMover = null;
    updateGame();
}

function generateInitialPiles() {
    let piles;
    do {
        piles = Array(4).fill(0).map(() => Math.floor(Math.random() * 8)); // 0 to 87 inclusive
    } while (xorSum(piles) === 0 || piles.every(x => x === 0));
    return piles;
}

// Game state
let originalPiles = generateInitialPiles();
let piles = [...originalPiles];
let maxPileSize = Math.max(...originalPiles);
let lastMover = null;

document.addEventListener("DOMContentLoaded", () => {
    updateGame();
    document.getElementById('restart-button').addEventListener('click', restartGame);
    
    let style = document.createElement("style");
    style.textContent = `
        #nim-game {
            font-family: Arial, sans-serif;
            max-width: 500px;
            margin: 0 auto;
            text-align: center;
        }
        #game-board {
            margin: 20px 0;
        }
        .pile-row {
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
        }
        .row-label {
            width: 80px;
            display: inline-block;
            text-align: right;
            margin-right: 10px;
            font-size: 12px;

        }
        .stones-container {
            display: inline-flex;
        }
        .stone {
            cursor: pointer;
            margin: 0 3px;
            transition: all 0.2s;
            width: 24px;
            display: inline-block;
            text-align: center;
        }
        .stone-spacer {
            width: 24px;
            margin: 0 3px;
            visibility: hidden;
        }
        .stone:hover {
            transform: translateY(-3px);
            opacity: 0.8;
        }
        #restart-button {
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
        }
        #restart-button:hover {
            background-color: #45a049;
        }
    `;
    document.head.appendChild(style);
});