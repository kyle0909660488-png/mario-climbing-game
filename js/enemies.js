// 敵人系統
class Enemy {
    constructor(x, y, type) {
        this.x = x;
        this.y = y;
        this.type = type;
        this.width = 24;
        this.height = 24;
        this.health = 30;
        this.speed = 1;
        this.direction = Math.random() > 0.5 ? 1 : -1;
        this.patrolDistance = 100;
        this.startX = x;
    }
    
    update() {
        // 基本巡邏邏輯
        this.x += this.speed * this.direction;
        
        // 巡邏邊界檢查
        if (Math.abs(this.x - this.startX) > this.patrolDistance) {
            this.direction *= -1;
        }
        
        // 畫面邊界檢查
        if (this.x < 0 || this.x > 800 - this.width) {
            this.direction *= -1;
        }
    }
    
    render(ctx) {
        ctx.fillStyle = '#e74c3c';
        ctx.fillRect(this.x, this.y, this.width, this.height);
        
        // 簡單的敵人圖標
        ctx.fillStyle = 'white';
        ctx.font = '16px Arial';
        ctx.textAlign = 'center';
        ctx.fillText('', this.x + this.width/2, this.y + this.height/2 + 5);
    }
    
    takeDamage(damage) {
        this.health -= damage;
        return this.health <= 0;
    }
}

// Boss 類別
class Boss extends Enemy {
    constructor(x, y) {
        super(x, y, 'boss');
        this.width = 64;
        this.height = 64;
        this.health = 200;
        this.maxHealth = 200;
        this.speed = 0.5;
        this.attackCooldown = 0;
        this.phase = 1;
    }
    
    update() {
        super.update();
        
        this.attackCooldown--;
        
        // Boss 攻擊邏輯
        if (this.attackCooldown <= 0) {
            this.attack();
            this.attackCooldown = 120; // 2秒冷卻
        }
        
        // Boss 階段變化
        if (this.health < this.maxHealth * 0.5 && this.phase === 1) {
            this.phase = 2;
            this.speed *= 1.5;
        }
    }
    
    attack() {
        // TODO: 實現 Boss 攻擊邏輯
        console.log('Boss 攻擊！');
    }
    
    render(ctx) {
        ctx.fillStyle = '#8e44ad';
        ctx.fillRect(this.x, this.y, this.width, this.height);
        
        ctx.fillStyle = 'white';
        ctx.font = '32px Arial';
        ctx.textAlign = 'center';
        ctx.fillText('', this.x + this.width/2, this.y + this.height/2 + 10);
        
        // Boss 血量條
        this.renderHealthBar(ctx);
    }
    
    renderHealthBar(ctx) {
        const barWidth = this.width;
        const barHeight = 6;
        const barX = this.x;
        const barY = this.y - 12;
        
        ctx.fillStyle = '#34495e';
        ctx.fillRect(barX, barY, barWidth, barHeight);
        
        ctx.fillStyle = '#e74c3c';
        const healthWidth = (this.health / this.maxHealth) * barWidth;
        ctx.fillRect(barX, barY, healthWidth, barHeight);
    }
}
