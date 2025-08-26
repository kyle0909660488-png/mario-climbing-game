// 玩家角色類別
class Player {
    constructor(x, y, characterType) {
        this.x = x;
        this.y = y;
        this.width = 32;
        this.height = 32;
        this.velocityX = 0;
        this.velocityY = 0;
        this.onGround = false;
        this.characterType = characterType;
        
        // 基礎屬性
        this.maxHealth = 100;
        this.health = this.maxHealth;
        this.speed = 5;
        this.jumpPower = 12;
        
        // 根據角色類型設定特殊屬性
        this.setCharacterStats();
        
        // 動畫相關
        this.animationFrame = 0;
        this.direction = 'right';
        this.isMoving = false;
        this.isCrouching = false;
        
        // 技能冷卻
        this.doubleJumpUsed = false;
        this.healCooldown = 0;
    }
    
    setCharacterStats() {
        switch(this.characterType) {
            case 'speed':
                this.speed = 8;
                this.jumpPower = 10;
                this.specialAbility = 'speed_boost';
                break;
            case 'jumper':
                this.speed = 4;
                this.jumpPower = 15;
                this.specialAbility = 'double_jump';
                this.canDoubleJump = true;
                break;
            case 'healer':
                this.speed = 4;
                this.jumpPower = 10;
                this.maxHealth = 150;
                this.health = this.maxHealth;
                this.specialAbility = 'auto_heal';
                this.healRate = 1; // 每秒回血量
                break;
            case 'warrior':
                this.speed = 3;
                this.jumpPower = 10;
                this.maxHealth = 120;
                this.health = this.maxHealth;
                this.specialAbility = 'melee_attack';
                this.attackDamage = 50;
                break;
        }
    }
    
    update() {
        // 重力
        this.velocityY += 0.8;
        
        // 位置更新
        this.x += this.velocityX;
        this.y += this.velocityY;
        
        // 摩擦力
        this.velocityX *= 0.8;
        
        // 邊界檢測
        if (this.x < 0) this.x = 0;
        if (this.x > 800 - this.width) this.x = 800 - this.width;
        
        // 地面檢測 (暫時設為畫布底部)
        if (this.y > 600 - this.height) {
            this.y = 600 - this.height;
            this.velocityY = 0;
            this.onGround = true;
            this.doubleJumpUsed = false;
        }
        
        // 特殊能力更新
        this.updateSpecialAbilities();
        
        // 動畫更新
        if (Math.abs(this.velocityX) > 0.1) {
            this.isMoving = true;
            this.animationFrame += 0.2;
        } else {
            this.isMoving = false;
            this.animationFrame = 0;
        }
    }
    
    updateSpecialAbilities() {
        // 治療型角色自動回血
        if (this.characterType === 'healer' && this.health < this.maxHealth) {
            this.healCooldown--;
            if (this.healCooldown <= 0) {
                this.health = Math.min(this.maxHealth, this.health + this.healRate);
                this.healCooldown = 60; // 1秒間隔 (假設60fps)
            }
        }
    }
    
    moveLeft() {
        this.velocityX = -this.speed;
        this.direction = 'left';
    }
    
    moveRight() {
        this.velocityX = this.speed;
        this.direction = 'right';
    }
    
    jump() {
        if (this.onGround) {
            this.velocityY = -this.jumpPower;
            this.onGround = false;
        } else if (this.canDoubleJump && !this.doubleJumpUsed && this.characterType === 'jumper') {
            this.velocityY = -this.jumpPower * 0.8;
            this.doubleJumpUsed = true;
        }
    }
    
    crouch() {
        this.isCrouching = true;
        // 蹲下可以讓角色更小，避開某些攻擊
        this.height = 24;
    }
    
    attack() {
        if (this.characterType === 'warrior') {
            // TODO: 實現近戰攻擊邏輯
            return {
                x: this.direction === 'right' ? this.x + this.width : this.x - 20,
                y: this.y,
                width: 20,
                height: this.height,
                damage: this.attackDamage
            };
        }
        return null;
    }
    
    takeDamage(damage) {
        this.health -= damage;
        if (this.health <= 0) {
            this.health = 0;
            return true; // 返回true表示角色死亡
        }
        return false;
    }
    
    render(ctx) {
        // 繪製角色 (簡單的矩形，可以之後替換成精靈圖)
        ctx.fillStyle = this.getCharacterColor();
        ctx.fillRect(this.x, this.y, this.width, this.height);
        
        // 繪製角色圖標
        ctx.fillStyle = 'white';
        ctx.font = '20px Arial';
        ctx.textAlign = 'center';
        const icon = this.getCharacterIcon();
        ctx.fillText(icon, this.x + this.width/2, this.y + this.height/2 + 7);
        
        // 繪製血量條
        this.renderHealthBar(ctx);
        
        // 重置蹲下狀態
        if (this.isCrouching) {
            this.height = 32;
            this.isCrouching = false;
        }
    }
    
    getCharacterColor() {
        switch(this.characterType) {
            case 'speed': return '#3498db';    // 藍色
            case 'jumper': return '#2ecc71';   // 綠色
            case 'healer': return '#e74c3c';   // 紅色
            case 'warrior': return '#f39c12';  // 橙色
            default: return '#95a5a6';         // 灰色
        }
    }
    
    getCharacterIcon() {
        switch(this.characterType) {
            case 'speed': return '';
            case 'jumper': return '';
            case 'healer': return '';
            case 'warrior': return '';
            default: return '';
        }
    }
    
    renderHealthBar(ctx) {
        const barWidth = this.width;
        const barHeight = 4;
        const barX = this.x;
        const barY = this.y - 8;
        
        // 血量條背景
        ctx.fillStyle = '#34495e';
        ctx.fillRect(barX, barY, barWidth, barHeight);
        
        // 血量條
        ctx.fillStyle = this.health > this.maxHealth * 0.3 ? '#2ecc71' : '#e74c3c';
        const healthWidth = (this.health / this.maxHealth) * barWidth;
        ctx.fillRect(barX, barY, healthWidth, barHeight);
    }
}
