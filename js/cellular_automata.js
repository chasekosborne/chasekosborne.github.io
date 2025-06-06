class CellularAutomata {
    constructor(canvas, cellSize = 30) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
        this.cellSize = cellSize;
        
        // Calculate grid dimensions
        this.cols = Math.floor(canvas.width / cellSize);
        this.rows = Math.floor(canvas.height / cellSize);
        
        // Initialize grid
        this.grid = this.createEmptyGrid();
        this.addGlider();
        
        // Animation control
        this.isRunning = false;
        this.animationId = null;
        
        // Bind methods
        this.draw = this.draw.bind(this);
        this.update = this.update.bind(this);
        this.handleClick = this.handleClick.bind(this);
        
        // Add event listeners
        this.canvas.addEventListener('click', this.handleClick);
        // Add touch support for mobile
        this.canvas.addEventListener('touchstart', this.handleTouch.bind(this));
    }

    createEmptyGrid() {
        return Array(this.rows).fill().map(() => Array(this.cols).fill(0));
    }

    addGlider() {
        // Calculate center position
        const centerRow = Math.floor(this.rows / 2);
        const centerCol = Math.floor(this.cols / 2);
        
        // Glider pattern
        const glider = [
            [0, 1, 0],
            [0, 0, 1],
            [1, 1, 1]
        ];
        
        // Place glider in center
        for (let i = 0; i < 3; i++) {
            for (let j = 0; j < 3; j++) {
                this.grid[centerRow + i - 1][centerCol + j - 1] = glider[i][j];
            }
        }
    }

    draw() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        for (let i = 0; i < this.rows; i++) {
            for (let j = 0; j < this.cols; j++) {
                if (this.grid[i][j]) {
                    this.ctx.fillStyle = '#4CAF50';
                    this.ctx.fillRect(
                        j * this.cellSize,
                        i * this.cellSize,
                        this.cellSize - 1,
                        this.cellSize - 1
                    );
                }
            }
        }
    }

    countNeighbors(row, col) {
        let count = 0;
        for (let i = -1; i <= 1; i++) {
            for (let j = -1; j <= 1; j++) {
                if (i === 0 && j === 0) continue;
                
                const newRow = (row + i + this.rows) % this.rows;
                const newCol = (col + j + this.cols) % this.cols;
                
                count += this.grid[newRow][newCol];
            }
        }
        return count;
    }

    update() {
        const newGrid = this.grid.map(row => [...row]);
        
        for (let i = 0; i < this.rows; i++) {
            for (let j = 0; j < this.cols; j++) {
                const neighbors = this.countNeighbors(i, j);
                const cell = this.grid[i][j];
                
                // Conway's Game of Life rules
                if (cell === 1 && (neighbors < 2 || neighbors > 3)) {
                    newGrid[i][j] = 0;
                } else if (cell === 0 && neighbors === 3) {
                    newGrid[i][j] = 1;
                }
            }
        }
        
        this.grid = newGrid;
    }

    handleClick(event) {
        const rect = this.canvas.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;
        
        const col = Math.floor(x / this.cellSize);
        const row = Math.floor(y / this.cellSize);
        
        if (row >= 0 && row < this.rows && col >= 0 && col < this.cols) {
            this.grid[row][col] = this.grid[row][col] ? 0 : 1;
            this.draw();
        }
    }

    handleTouch(event) {
        event.preventDefault(); // Prevent scrolling when touching the canvas
        const touch = event.touches[0];
        const rect = this.canvas.getBoundingClientRect();
        const x = touch.clientX - rect.left;
        const y = touch.clientY - rect.top;
        
        const col = Math.floor(x / this.cellSize);
        const row = Math.floor(y / this.cellSize);
        
        if (row >= 0 && row < this.rows && col >= 0 && col < this.cols) {
            this.grid[row][col] = this.grid[row][col] ? 0 : 1;
            this.draw();
        }
    }

    start() {
        if (!this.isRunning) {
            this.isRunning = true;
            this.animate();
        }
    }

    stop() {
        this.isRunning = false;
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
            this.animationId = null;
        }
    }

    reset() {
        this.grid = this.createEmptyGrid();
        this.addGlider();
        this.draw();
    }

    animate() {
        if (!this.isRunning) return;
        
        this.update();
        this.draw();
        this.animationId = requestAnimationFrame(() => this.animate());
    }
} 