// 套裝與道具系統
class PowerUp {
    constructor(x, y, type) {
        this.x = x;
        this.y = y;
        this.type = type;
        this.width = 24;
        this.height = 24;
        this.collected = false;
        this.animationFrame = 0;
    }
    
    update() {
        if (!this.collected) {
            this.animationFrame += 0.1;
            this.y += Math.sin(this.animationFrame) * 0.5; // 浮動效果
        }
    }
    
    render(ctx) {
        if (this.collected) return;
        
        ctx.fillStyle = this.getPowerUpColor();
        ctx.fillRect(this.x, this.y, this.width, this.height);
        
        ctx.fillStyle = 'white';
        ctx.font = '16px Arial';
        ctx.textAlign = 'center';
        const icon = this.getPowerUpIcon();
        ctx.fillText(icon, this.x + this.width/2, this.y + this.height/2 + 5);
    }
    
    getPowerUpColor() {
        switch(this.type) {
            case 'health': return '#e74c3c';
            case 'speed': return '#3498db';
            case 'jump': return '#2ecc71';
            case 'fire_suit': return '#e67e22';
            case 'ice_suit': return '#74b9ff';
            case 'shadow_suit': return '#2d3436';
            case 'tank_suit': return '#6c5ce7';
            default: return '#95a5a6';
        }
    }
    
    getPowerUpIcon() {
        switch(this.type) {
            case 'health': return '';
            case 'speed': return '';
            case 'jump': return '';
            case 'fire_suit': return '';
            case 'ice_suit': return '';
            case 'shadow_suit': return '';
            case 'tank_suit': return '';
            default: return '';
        }
    }
    
    collect(player) {
        if (this.collected) return false;
        
        this.collected = true;
        this.applyEffect(player);
        return true;
    }
    
    applyEffect(player) {
        switch(this.type) {
            case 'health':
                player.health = Math.min(player.maxHealth, player.health + 50);
                break;
                
            case 'speed':
                player.speed += 2;
                setTimeout(() => player.speed -= 2, 10000); // 10秒效果
                break;
                
            case 'jump':
                player.jumpPower += 5;
                setTimeout(() => player.jumpPower -= 5, 10000); // 10秒效果
                break;
                
            case 'fire_suit':
                player.currentSuit = 'fire';
                player.suitDuration = 30000; // 30秒
                break;
                
            case 'ice_suit':
                player.currentSuit = 'ice';
                player.suitDuration = 30000; // 30秒
                break;
                
            case 'shadow_suit':
                player.currentSuit = 'shadow';
                player.suitDuration = 15000; // 15秒
                break;
                
            case 'tank_suit':
                player.currentSuit = 'tank';
                player.suitDuration = 45000; // 45秒
                player.maxHealth += 50;
                player.health += 50;
                break;
        }
        
        console.log(收集到道具: );
    }
}

// 套裝效果管理
class SuitManager {
    static updateSuitEffects(player) {
        if (!player.currentSuit) return;
        
        player.suitDuration -= 16.67; // 假設60fps
        
        if (player.suitDuration <= 0) {
            this.removeSuitEffect(player);
        }
    }
    
    static removeSuitEffect(player) {
        switch(player.currentSuit) {
            case 'tank':
                player.maxHealth -= 50;
                player.health = Math.min(player.health, player.maxHealth);
                break;
        }
        
        player.currentSuit = null;
        player.suitDuration = 0;
        console.log('套裝效果結束');
    }
    
    static getSuitAbility(player) {
        switch(player.currentSuit) {
            case 'fire':
                return {
                    type: 'projectile',
                    damage: 30,
                    speed: 8,
                    icon: ''
                };
                
            case 'ice':
                return {
                    type: 'slow',
                    duration: 3000,
                    slowFactor: 0.5,
                    icon: ''
                };
                
            case 'shadow':
                return {
                    type: 'invisibility',
                    duration: 2000,
                    icon: ''
                };
                
            case 'tank':
                return {
                    type: 'damage_reduction',
                    reduction: 0.5,
                    icon: ''
                };
                
            default:
                return null;
        }
    }
}

// 投射物類別 (火球等)
class Projectile {
    constructor(x, y, direction, type) {
        this.x = x;
        this.y = y;
        this.width = 16;
        this.height = 16;
        this.velocityX = direction * 8;
        this.velocityY = 0;
        this.type = type;
        this.damage = 30;
        this.active = true;
    }
    
    update() {
        if (!this.active) return;
        
        this.x += this.velocityX;
        this.y += this.velocityY;
        
        // 邊界檢查
        if (this.x < 0 || this.x > 800 || this.y < 0 || this.y > 600) {
            this.active = false;
        }
    }
    
    render(ctx) {
        if (!this.active) return;
        
        ctx.fillStyle = this.type === 'fire' ? '#e74c3c' : '#3498db';
        ctx.fillRect(this.x, this.y, this.width, this.height);
        
        ctx.fillStyle = 'white';
        ctx.font = '12px Arial';
        ctx.textAlign = 'center';
        const icon = this.type === 'fire' ? '' : '';
        ctx.fillText(icon, this.x + this.width/2, this.y + this.height/2 + 4);
    }
}
