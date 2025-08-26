// 主遊戲邏輯
class Game {
    constructor() {
        this.canvas = document.getElementById('gameCanvas');
        this.ctx = this.canvas.getContext('2d');
        this.score = 0;
        this.lives = 3;
        this.level = 1;
        this.gameState = 'start'; // start, playing, gameOver
        this.selectedCharacter = null;
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.updateUI();
        this.gameLoop();
    }
    
    setupEventListeners() {
        // 角色選擇
        document.querySelectorAll('.character').forEach(char => {
            char.addEventListener('click', () => {
                document.querySelectorAll('.character').forEach(c => c.classList.remove('selected'));
                char.classList.add('selected');
                this.selectedCharacter = char.dataset.character;
            });
        });
        
        // 開始遊戲按鈕
        document.getElementById('startButton').addEventListener('click', () => {
            if (this.selectedCharacter) {
                this.startGame();
            } else {
                alert('請選擇一個角色！');
            }
        });
        
        // 重新開始按鈕
        document.getElementById('restartButton').addEventListener('click', () => {
            this.resetGame();
        });
        
        // 鍵盤控制
        document.addEventListener('keydown', (e) => {
            if (this.gameState === 'playing') {
                this.handleInput(e.key.toLowerCase());
            }
        });
    }
    
    startGame() {
        this.gameState = 'playing';
        document.getElementById('startScreen').classList.add('hidden');
        
        // 初始化玩家
        this.player = new Player(400, 500, this.selectedCharacter);
        this.enemies = [];
        this.powerups = [];
        this.currentLevel = new Level(this.level);
        
        console.log(遊戲開始！選擇角色: );
    }
    
    handleInput(key) {
        switch(key) {
            case 'w':
                this.player.jump();
                break;
            case 'a':
                this.player.moveLeft();
                break;
            case 's':
                this.player.crouch();
                break;
            case 'd':
                this.player.moveRight();
                break;
        }
    }
    
    update() {
        if (this.gameState !== 'playing') return;
        
        // 更新遊戲物件
        if (this.player) {
            this.player.update();
        }
        
        // 更新敵人
        this.enemies.forEach(enemy => enemy.update());
        
        // 碰撞檢測
        this.checkCollisions();
        
        // 檢查遊戲結束條件
        this.checkGameOver();
    }
    
    render() {
        // 清除畫布
        this.ctx.fillStyle = '#87CEEB';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        if (this.gameState === 'playing') {
            // 繪製關卡
            if (this.currentLevel) {
                this.currentLevel.render(this.ctx);
            }
            
            // 繪製玩家
            if (this.player) {
                this.player.render(this.ctx);
            }
            
            // 繪製敵人
            this.enemies.forEach(enemy => enemy.render(this.ctx));
            
            // 繪製道具
            this.powerups.forEach(powerup => powerup.render(this.ctx));
        }
    }
    
    checkCollisions() {
        // TODO: 實現碰撞檢測邏輯
    }
    
    checkGameOver() {
        if (this.lives <= 0) {
            this.gameOver();
        }
    }
    
    gameOver() {
        this.gameState = 'gameOver';
        document.getElementById('finalScore').textContent = 最終分數: ;
        document.getElementById('gameOverScreen').classList.remove('hidden');
    }
    
    resetGame() {
        this.score = 0;
        this.lives = 3;
        this.level = 1;
        this.gameState = 'start';
        this.selectedCharacter = null;
        
        document.getElementById('gameOverScreen').classList.add('hidden');
        document.getElementById('startScreen').classList.remove('hidden');
        document.querySelectorAll('.character').forEach(c => c.classList.remove('selected'));
        
        this.updateUI();
    }
    
    updateUI() {
        document.getElementById('score').textContent = 分數: ;
        document.getElementById('lives').textContent = 生命: ;
        document.getElementById('level').textContent = 關卡: ;
    }
    
    gameLoop() {
        this.update();
        this.render();
        requestAnimationFrame(() => this.gameLoop());
    }
}

// 啟動遊戲
const game = new Game();
