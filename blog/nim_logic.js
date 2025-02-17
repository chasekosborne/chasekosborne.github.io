function xorSum(piles) {
    return piles.reduce((a, b) => a ^ b, 0);
}

function bestMove(piles) {
    let sum = xorSum(piles);
    if (sum === 0) return null; // AI loses

    for (let i = 0; i < piles.length; i++) {
        let target = piles[i] ^ sum;
        if (target < piles[i]) {
            return [i, piles[i] - target];
        }
    }
    return null;
}

function updateGame() {
    let gameBoard = document.getElementById("game-board");
    gameBoard.innerHTML = "";
    for (let i = 0; i < piles.length; i++) {
        let row = document.createElement("div");
        row.innerHTML = `Row ${i + 1}: ` + "🪨".repeat(piles[i]);
        gameBoard.appendChild(row);
    }
}

let piles = [3, 5, 7];

function playerMove(row, remove) {
    if (piles[row] >= remove) {
        piles[row] -= remove;
        updateGame();
        setTimeout(aiMove, 500);
    }
}

function aiMove() {
    let move = bestMove(piles);
    if (move) {
        alert(`AI removes ${move[1]} from row ${move[0] + 1}`);
        piles[move[0]] -= move[1];
        updateGame();
        if (piles.every(x => x === 0)) {
            alert("AI wins!");
        }
    } else {
        alert("You win!");
    }
}

document.addEventListener("DOMContentLoaded", () => {
    updateGame();
});