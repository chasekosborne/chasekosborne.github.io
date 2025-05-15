class StockSimulator {
    constructor(canvas, depthCanvas) {
        this.canvas = canvas;
        this.depthCanvas = depthCanvas;
        this.ctx = canvas.getContext('2d');
        this.depthCtx = depthCanvas.getContext('2d');
        
        // Simulation parameters
        this.price = 100; // Initial price
        this.volume = 0;
        this.time = 0;
        this.isRunning = false;
        this.orders = [];
        this.depth = { bids: [], asks: [] };
        
        // Chart parameters with increased padding
        this.padding = { 
            top: 40,      // Increased from 30
            right: 60,    // Increased from 40
            bottom: 50,   // Increased from 40
            left: 80      // Increased from 60
        };
        this.priceHistory = [this.price];
        this.volumeHistory = [0];
        this.timeHistory = [0];
        
        // Add spacing for axis labels
        this.labelSpacing = {
            time: 15,      // Space between time axis and numbers
            volume: 15,    // Space between volume axis and numbers
            price: 15      // Space between price axis and numbers
        };
        
        // Modern light mode colors
        this.colors = {
            background: '#ffffff',  // White background
            grid: '#f1f3f5',       // Very light gray grid
            text: '#495057',       // Dark gray text
            price: '#228be6',      // Bright blue for price
            volume: '#1c7ed6',     // Slightly darker blue for volume
            bid: '#37b24d',        // Fresh green for bids
            ask: '#f03e3e',        // Bright red for asks
            axis: '#dee2e6',       // Light gray for axes
            highlight: '#adb5bd'   // Medium gray for highlights
        };
        
        // Font settings (slightly adjusted for light mode)
        this.font = {
            family: '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif',
            size: '12px',
            weight: '500'  // Slightly bolder for better contrast on light background
        };
        
        // Add price range tracking
        this.minVisiblePrice = 90;  // Start with a wider range
        this.maxVisiblePrice = 110;
        
        // Initialize depth chart
        this.initializeDepth();
        
        // Initial draw
        this.draw();
    }

    initializeDepth() {
        this.depth = { bids: [], asks: [] };
        // Initialize order book with some random orders
        for (let i = 0; i < 10; i++) {
            const bidPrice = this.price * (1 - (i + 1) * 0.01);
            const askPrice = this.price * (1 + (i + 1) * 0.01);
            this.depth.bids.push({
                price: bidPrice,
                volume: Math.floor(Math.random() * 1000) + 100
            });
            this.depth.asks.push({
                price: askPrice,
                volume: Math.floor(Math.random() * 1000) + 100
            });
        }
    }

    start() {
        if (!this.isRunning) {
            this.isRunning = true;
            this.simulate();
        }
    }

    stop() {
        this.isRunning = false;
    }

    reset() {
        this.price = 100;
        this.volume = 0;
        this.time = 0;
        this.priceHistory = [this.price];
        this.volumeHistory = [0];
        this.timeHistory = [0];
        this.initializeDepth();
        this.draw();
        
        // Reset price range
        this.minVisiblePrice = 90;
        this.maxVisiblePrice = 110;
    }

    simulate() {
        if (!this.isRunning) return;

        // Generate random price movement with mean reversion
        const change = (Math.random() - 0.5) * 2 + (100 - this.price) * 0.01;
        this.price += change;
        
        // Generate random volume with more realistic fluctuations
        const volumeChange = Math.floor(Math.random() * 2000) - 1000; // Can go up or down
        this.volume = Math.max(0, this.volume + volumeChange); // Ensure volume doesn't go negative
        
        // Update time
        this.time += 1;
        
        // Update order book
        this.updateOrderBook();
        
        // Record history
        this.priceHistory.push(this.price);
        this.volumeHistory.push(this.volume);
        this.timeHistory.push(this.time);
        
        // Draw updates
        this.draw();
        
        // Continue simulation
        requestAnimationFrame(() => this.simulate());
    }

    updateOrderBook() {
        // Randomly add or remove orders
        if (Math.random() < 0.3) {
            const isBid = Math.random() < 0.5;
            const price = isBid ? 
                this.price * (1 - Math.random() * 0.02) :
                this.price * (1 + Math.random() * 0.02);
            const volume = Math.floor(Math.random() * 1000) + 100;
            
            if (isBid) {
                this.depth.bids.push({ price, volume });
                this.depth.bids.sort((a, b) => b.price - a.price);
                // Keep only top 10 bids
                if (this.depth.bids.length > 10) {
                    this.depth.bids = this.depth.bids.slice(0, 10);
                }
            } else {
                this.depth.asks.push({ price, volume });
                this.depth.asks.sort((a, b) => a.price - b.price);
                // Keep only top 10 asks
                if (this.depth.asks.length > 10) {
                    this.depth.asks = this.depth.asks.slice(0, 10);
                }
            }
        }
    }

    draw() {
        // Clear canvases with Bloomberg background
        this.ctx.fillStyle = this.colors.background;
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        this.depthCtx.fillStyle = this.colors.background;
        this.depthCtx.fillRect(0, 0, this.depthCanvas.width, this.depthCanvas.height);
        
        // Draw price and volume chart
        this.drawPriceVolumeChart();
        
        // Draw depth chart
        this.drawDepthChart();
    }

    drawPriceVolumeChart() {
        const width = this.canvas.width - this.padding.left - this.padding.right;
        const height = this.canvas.height - this.padding.top - this.padding.bottom;
        
        // Draw grid
        this.ctx.strokeStyle = this.colors.grid;
        this.ctx.lineWidth = 1;
        for (let i = 0; i <= 5; i++) {
            const y = this.padding.top + (i / 5) * height;
            this.ctx.beginPath();
            this.ctx.moveTo(this.padding.left, y);
            this.ctx.lineTo(this.canvas.width - this.padding.right, y);
            this.ctx.stroke();
        }
        
        // Find price range with some padding
        const minPrice = Math.min(...this.priceHistory) * 0.995;
        const maxPrice = Math.max(...this.priceHistory) * 1.005;
        const priceRange = maxPrice - minPrice;
        
        // Draw price line with gradient
        const gradient = this.ctx.createLinearGradient(0, this.padding.top, 0, this.canvas.height - this.padding.bottom);
        gradient.addColorStop(0, this.colors.price);
        gradient.addColorStop(1, this.colors.volume);
        
        this.ctx.beginPath();
        this.ctx.strokeStyle = gradient;
        this.ctx.lineWidth = 2;
        
        this.priceHistory.forEach((price, i) => {
            const x = this.padding.left + (i / (this.priceHistory.length - 1)) * width;
            const y = this.padding.top + height - ((price - minPrice) / priceRange) * height;
            if (i === 0) {
                this.ctx.moveTo(x, y);
            } else {
                this.ctx.lineTo(x, y);
            }
        });
        this.ctx.stroke();
        
        // Draw volume bars with modern style
        const volumeHeight = height * 0.35; // Increased from 0.3 to show more volume
        const maxVolume = Math.max(...this.volumeHistory) * 1.1; // Add 10% padding to volume
        this.volumeHistory.forEach((volume, i) => {
            const x = this.padding.left + (i / (this.volumeHistory.length - 1)) * width;
            const barHeight = (volume / maxVolume) * volumeHeight;
            this.ctx.fillStyle = this.colors.volume + '20';
            this.ctx.fillRect(x, this.canvas.height - this.padding.bottom - barHeight, 
                            width / this.volumeHistory.length, barHeight);
        });
        
        // Draw axes
        this.ctx.strokeStyle = this.colors.axis;
        this.ctx.lineWidth = 1;
        this.ctx.beginPath();
        this.ctx.moveTo(this.padding.left, this.padding.top);
        this.ctx.lineTo(this.padding.left, this.canvas.height - this.padding.bottom);
        this.ctx.lineTo(this.canvas.width - this.padding.right, this.canvas.height - this.padding.bottom);
        this.ctx.stroke();

        // Draw labels with modern style
        this.ctx.fillStyle = this.colors.text;
        this.ctx.font = `${this.font.weight} ${this.font.size} ${this.font.family}`;
        
        // Price labels (right side)
        this.ctx.textAlign = 'right';
        const priceStep = priceRange / 5;
        for (let i = 0; i <= 5; i++) {
            const price = minPrice + priceStep * i;
            const y = this.padding.top + height - (i / 5) * height;
            this.ctx.fillText(price.toFixed(2), this.padding.left - 10, y + 4);
        }

        // Volume labels (left side)
        this.ctx.textAlign = 'left';
        const volumeStep = maxVolume / 5;
        for (let i = 0; i <= 5; i++) {
            const volume = volumeStep * i;
            const y = this.canvas.height - this.padding.bottom - (i / 5) * volumeHeight;
            this.ctx.fillText(Math.floor(volume).toString(), this.padding.left + 10, y + 4);
        }

        // Time labels
        this.ctx.textAlign = 'center';
        const timeStep = this.timeHistory.length / 5;
        for (let i = 0; i <= 5; i++) {
            const time = Math.floor(i * timeStep);
            const x = this.padding.left + (i / 5) * width;
            this.ctx.fillText(time.toString(), x, this.canvas.height - this.padding.bottom + 25);
        }

        // Axis titles with more spacing
        this.ctx.save();
        this.ctx.translate(this.padding.left - 50, this.canvas.height / 2);
        this.ctx.rotate(-Math.PI / 2);
        this.ctx.textAlign = 'center';
        this.ctx.fillText('PRICE', 0, 0);
        this.ctx.restore();

        this.ctx.save();
        this.ctx.translate(this.padding.left - 50, this.canvas.height - this.padding.bottom / 2);
        this.ctx.rotate(-Math.PI / 2);
        this.ctx.textAlign = 'center';
        this.ctx.fillText('VOLUME', 0, 0);
        this.ctx.restore();

        // Time axis title with spacing
        this.ctx.textAlign = 'center';
        this.ctx.fillText('TIME', this.canvas.width / 2, this.canvas.height - this.padding.bottom + 40);
    }

    drawDepthChart() {
        const width = this.depthCanvas.width - this.padding.left - this.padding.right;
        const height = this.depthCanvas.height - this.padding.top - this.padding.bottom;
        
        // Draw grid
        this.depthCtx.strokeStyle = this.colors.grid;
        this.depthCtx.lineWidth = 1;
        for (let i = 0; i <= 5; i++) {
            const y = this.padding.top + (i / 5) * height;
            this.depthCtx.beginPath();
            this.depthCtx.moveTo(this.padding.left, y);
            this.depthCtx.lineTo(this.depthCanvas.width - this.padding.right, y);
            this.depthCtx.stroke();
        }
        
        // Find price range with some padding, but limit to visible orders
        const visibleBids = this.depth.bids.filter(bid => bid.volume > 0);
        const visibleAsks = this.depth.asks.filter(ask => ask.volume > 0);
        
        if (visibleBids.length > 0 && visibleAsks.length > 0) {
            // Calculate the spread between highest bid and lowest ask
            const highestBid = Math.max(...visibleBids.map(b => b.price));
            const lowestAsk = Math.min(...visibleAsks.map(a => a.price));
            
            // Update visible price range gradually
            const targetMinPrice = Math.min(...visibleBids.map(b => b.price)) * 0.995;
            const targetMaxPrice = Math.max(...visibleAsks.map(a => a.price)) * 1.005;
            
            // Smoothly adjust the visible range
            this.minVisiblePrice = Math.min(this.minVisiblePrice, targetMinPrice);
            this.maxVisiblePrice = Math.max(this.maxVisiblePrice, targetMaxPrice);
            
            // Ensure minimum range
            const minRange = 20; // Minimum price range to display
            if (this.maxVisiblePrice - this.minVisiblePrice < minRange) {
                const center = (this.maxVisiblePrice + this.minVisiblePrice) / 2;
                this.minVisiblePrice = center - minRange / 2;
                this.maxVisiblePrice = center + minRange / 2;
            }
            
            const priceRange = this.maxVisiblePrice - this.minVisiblePrice;
            
            // Draw bids with modern style
            visibleBids.forEach(bid => {
                const x = this.padding.left;
                const y = this.padding.top + height - ((bid.price - this.minVisiblePrice) / priceRange) * height;
                const barWidth = (bid.volume / 1000) * width;
                this.depthCtx.fillStyle = this.colors.bid + '20';
                this.depthCtx.fillRect(x, y, barWidth, 2);
                
                // Draw bid price and volume with more spacing
                this.depthCtx.fillStyle = this.colors.text;
                this.depthCtx.font = `${this.font.weight} ${this.font.size} ${this.font.family}`;
                this.depthCtx.textAlign = 'right';
                this.depthCtx.fillText(bid.price.toFixed(2), this.padding.left - 10, y + 4);
                this.depthCtx.textAlign = 'left';
                this.depthCtx.fillText(bid.volume.toString(), x + barWidth + 10, y + 4);
            });
            
            // Draw asks with modern style
            visibleAsks.forEach(ask => {
                const x = this.padding.left;
                const y = this.padding.top + height - ((ask.price - this.minVisiblePrice) / priceRange) * height;
                const barWidth = (ask.volume / 1000) * width;
                this.depthCtx.fillStyle = this.colors.ask + '20';
                this.depthCtx.fillRect(x, y, barWidth, 2);
                
                // Draw ask price and volume with more spacing
                this.depthCtx.fillStyle = this.colors.text;
                this.depthCtx.font = `${this.font.weight} ${this.font.size} ${this.font.family}`;
                this.depthCtx.textAlign = 'right';
                this.depthCtx.fillText(ask.price.toFixed(2), this.padding.left - 10, y + 4);
                this.depthCtx.textAlign = 'left';
                this.depthCtx.fillText(ask.volume.toString(), x + barWidth + 10, y + 4);
            });
            
            // Draw axes
            this.depthCtx.strokeStyle = this.colors.axis;
            this.depthCtx.lineWidth = 1;
            this.depthCtx.beginPath();
            this.depthCtx.moveTo(this.padding.left, this.padding.top);
            this.depthCtx.lineTo(this.padding.left, this.depthCanvas.height - this.padding.bottom);
            this.depthCtx.lineTo(this.depthCanvas.width - this.padding.right, this.depthCanvas.height - this.padding.bottom);
            this.depthCtx.stroke();

            // Draw labels with modern style
            this.depthCtx.fillStyle = this.colors.text;
            this.depthCtx.font = `${this.font.weight} ${this.font.size} ${this.font.family}`;
            
            // Price labels (right side)
            this.depthCtx.textAlign = 'right';
            const priceStep = priceRange / 5;
            for (let i = 0; i <= 5; i++) {
                const price = this.minVisiblePrice + priceStep * i;
                const y = this.padding.top + height - (i / 5) * height;
                this.depthCtx.fillText(price.toFixed(2), this.padding.left - 10, y + 4);
            }

            // Volume labels (left side) - reduced to 3 labels for better spacing
            this.depthCtx.textAlign = 'left';
            const maxVolume = 1000;
            const volumeStep = maxVolume / 2; // Changed from 5 to 2 for fewer labels
            for (let i = 0; i <= 2; i++) { // Changed from 5 to 2
                const volume = volumeStep * i;
                const x = this.padding.left + (i / 2) * width; // Changed from 5 to 2
                this.depthCtx.fillText(Math.floor(volume).toString(), x, this.depthCanvas.height - this.padding.bottom + 25);
            }

            // Axis titles with more spacing
            this.depthCtx.save();
            this.depthCtx.translate(this.padding.left - 50, this.depthCanvas.height / 2);
            this.depthCtx.rotate(-Math.PI / 2);
            this.depthCtx.textAlign = 'center';
            this.depthCtx.fillText('PRICE', 0, 0);
            this.depthCtx.restore();

            // Volume axis title with spacing
            this.depthCtx.textAlign = 'center';
            this.depthCtx.fillText('VOLUME', this.depthCanvas.width / 2, this.depthCanvas.height - this.padding.bottom + 40);
        }
    }
} 