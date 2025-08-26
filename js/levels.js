// 關卡設計
class Level {
    constructor(levelNumber) {
        this.levelNumber = levelNumber;
        this.platforms = [];
        this.traps = [];
        this.enemies = [];
        this.generateLevel();
    }
    
    generateLevel() {
        // 生成平台
        this.generatePlatforms();
        
        // 生成陷阱
        this.generateTraps();
        
        // 生成敵人
        this.generateEnemies();
    }
    
    generatePlatforms() {
        // 基礎平台佈局
        const platformConfigs = [
            {x: 0, y: 580, width: 200, height: 20},
            {x: 250, y: 520, width: 150, height: 20},
            {x: 450, y: 460, width: 150, height: 20},
            {x: 150, y: 400, width: 120, height: 20},
            {x: 350, y: 340, width: 120, height: 20},
            {x: 550, y: 280, width: 120, height: 20},
            {x: 100, y: 220, width: 120, height: 20},
            {x: 400, y: 160, width: 120, height: 20},
            {x: 200, y: 100, width: 200, height: 20}
        ];
        
        this.platforms = platformConfigs.map(config => new Platform(config));
    }
    
    generateTraps() {
        // 生成陷阱
        this.traps = [
            new Trap(300, 500, 'spike'),
            new Trap(500, 440, 'fire'),
            new Trap(200, 380, 'spike'),
            new Trap(600, 260, 'moving_platform')
        ];
    }
    
    generateEnemies() {
        // 生成敵人
        this.enemies = [
            new Enemy(260, 496, 'basic'),
            new Enemy(460, 436, 'basic'),
            new Enemy(160, 376, 'basic')
        ];
        
        // 如果是Boss關卡
        if (this.levelNumber % 5 === 0) {
            this.enemies.push(new Boss(300, 36));
        }
    }
    
    render(ctx) {
        // 繪製平台
        this.platforms.forEach(platform => platform.render(ctx));
        
        // 繪製陷阱
        this.traps.forEach(trap => trap.render(ctx));
    }
}

// 平台類別
class Platform {
    constructor(config) {
        this.x = config.x;
        this.y = config.y;
        this.width = config.width;
        this.height = config.height;
        this.type = config.type || 'solid';
    }
    
    render(ctx) {
        ctx.fillStyle = '#8b4513';
        ctx.fillRect(this.x, this.y, this.width, this.height);
        
        // 平台邊框
        ctx.strokeStyle = '#654321';
        ctx.lineWidth = 2;
        ctx.strokeRect(this.x, this.y, this.width, this.height);
    }
}

// 陷阱類別
class Trap {
    constructor(x, y, type) {
        this.x = x;
        this.y = y;
        this.type = type;
        this.width = 32;
        this.height = 32;
        this.active = true;
        this.animationFrame = 0;
    }
    
    update() {
        this.animationFrame += 0.1;
        
        // 移動平台特殊邏輯
        if (this.type === 'moving_platform') {
            this.x += Math.sin(this.animationFrame) * 2;
        }
    }
    
    render(ctx) {
        switch(this.type) {
            case 'spike':
                ctx.fillStyle = '#2c3e50';
                ctx.fillRect(this.x, this.y, this.width, this.height);
                ctx.fillStyle = 'white';
                ctx.font = '20px Arial';
                ctx.textAlign = 'center';
                ctx.fillText('', this.x + this.width/2, this.y + this.height/2 + 7);
                break;
                
            case 'fire':
                ctx.fillStyle = '#e74c3c';
                ctx.fillRect(this.x, this.y, this.width, this.height);
                ctx.fillStyle = 'white';
                ctx.font = '20px Arial';
                ctx.textAlign = 'center';
                ctx.fillText('', this.x + this.width/2, this.y + this.height/2 + 7);
                break;
                
            case 'moving_platform':
                ctx.fillStyle = '#3498db';
                ctx.fillRect(this.x, this.y, this.width, this.height);
                ctx.fillStyle = 'white';
                ctx.font = '16px Arial';
                ctx.textAlign = 'center';
                ctx.fillText('', this.x + this.width/2, this.y + this.height/2 + 5);
                break;
        }
    }
}
