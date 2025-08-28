######################載入套件######################
import pygame
import math
import random
from typing import Tuple, Optional
from abc import ABC, abstractmethod


######################敵人基礎抽象類別######################
class BaseEnemy(ABC):
    """
    所有敵人的基礎抽象類別\n
    \n
    定義敵人的共通介面和基本行為：\n
    1. 敵人的基本屬性（位置、血量、攻擊力）\n
    2. AI 行為模式（巡邏、追蹤、攻擊）\n
    3. 狀態管理（存活、受傷、攻擊狀態）\n
    4. 抽象方法強制子類別實作特定行為\n
    \n
    屬性:\n
    x, y (float): 敵人當前位置\n
    health (int): 當前血量\n
    max_health (int): 最大血量\n
    attack_damage (int): 攻擊傷害\n
    speed (float): 移動速度\n
    ai_state (str): 當前 AI 狀態\n
    \n
    子類別需要實作:\n
    - update_ai(): AI 行為邏輯\n
    - render(): 繪製敵人外觀\n
    - attack_player(): 攻擊玩家的行為\n
    """

    def __init__(
        self,
        x: float,
        y: float,
        health: int = 50,
        attack_damage: int = 15,
        speed: float = 1.0,
    ):
        """
        初始化基礎敵人\n
        \n
        設定敵人的基本屬性和狀態\n
        \n
        參數:\n
        x (float): 敵人起始 X 座標\n
        y (float): 敵人起始 Y 座標\n
        health (int): 敵人血量\n
        attack_damage (int): 敵人攻擊傷害\n
        speed (float): 敵人移動速度\n
        """
        # 基本位置和物理屬性
        self.x = float(x)
        self.y = float(y)
        self.start_x = float(x)  # 記住起始位置
        self.start_y = float(y)

        # 戰鬥屬性
        self.health = health
        self.max_health = health
        self.attack_damage = attack_damage
        self.speed = speed

        # 碰撞和尺寸
        self.width = 25
        self.height = 30

        # AI 狀態機
        self.ai_state = "patrol"  # 'patrol', 'chase', 'attack', 'dead'
        self.target_player = None
        self.last_known_player_pos = None

        # 移動和物理
        self.velocity_x = 0.0
        self.velocity_y = 0.0
        self.is_on_ground = False
        self.facing_direction = 1  # 1: 向右, -1: 向左

        # 巡邏行為
        self.patrol_center_x = x
        self.patrol_range = 100  # 巡邏範圍
        self.patrol_direction = 1

        # 戰鬥狀態
        self.attack_cooldown = 0
        self.max_attack_cooldown = 60  # 1秒攻擊間隔
        self.detection_range = 120  # 偵測玩家的距離
        self.attack_range = 40  # 攻擊距離

        # 受傷和死亡效果
        self.damage_flash_timer = 0
        self.is_dead = False
        self.death_timer = 0

        # 燃燒狀態效果
        self.is_burning = False
        self.burn_timer = 0  # 燃燒剩餘時間
        self.burn_damage_timer = 0  # 燃燒傷害計時器
        self.burn_damage_interval = 60  # 燃燒傷害間隔（1秒 = 60幀）
        self.burn_particle_timer = 0  # 燃燒粒子效果計時器

        # 視覺效果
        self.animation_frame = 0
        self.sprite_flip = False

    @abstractmethod
    def update_ai(self, player):
        """
        更新 AI 行為（抽象方法）\n
        \n
        子類別必須實作此方法，定義敵人的智能行為\n
        \n
        參數:\n
        player: 玩家物件\n
        """
        pass

    @abstractmethod
    def render(self, screen: pygame.Surface, camera_y: float):
        """
        繪製敵人（抽象方法）\n
        \n
        子類別必須實作此方法，定義敵人的外觀\n
        \n
        參數:\n
        screen (pygame.Surface): 螢幕表面\n
        camera_y (float): 攝影機偏移\n
        """
        pass

    @abstractmethod
    def attack_player(self, player) -> dict:
        """
        攻擊玩家（抽象方法）\n
        \n
        子類別必須實作此方法，定義攻擊行為\n
        \n
        參數:\n
        player: 玩家物件\n
        \n
        回傳:\n
        dict: 攻擊結果資訊\n
        """
        pass

    def update(self, player):
        """
        更新敵人狀態\n
        \n
        每幀更新敵人的所有狀態和行為\n
        \n
        參數:\n
        player: 玩家物件\n
        """
        if self.is_dead:
            self._update_death_animation()
            return

        # 更新基本屬性
        self._update_base_properties()

        # 更新 AI 行為
        self.update_ai(player)

        # 應用物理效果
        self._apply_physics()

        # 更新動畫
        self._update_animation()

    def _update_base_properties(self):
        """
        更新基礎屬性\n
        \n
        處理所有敵人共通的狀態更新\n
        """
        # 更新攻擊冷卻
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        # 更新受傷閃爍效果
        if self.damage_flash_timer > 0:
            self.damage_flash_timer -= 1

        # 更新燃燒狀態
        self._update_burn_effect()

        # 更新動畫幀
        self.animation_frame += 1
        if self.animation_frame >= 1000:
            self.animation_frame = 0

    def _apply_physics(self):
        """
        應用物理效果\n
        \n
        處理重力、移動和基本物理運算\n
        """
        # 簡化的重力系統
        if not self.is_on_ground:
            self.velocity_y += 0.5  # 重力加速度

        # 限制下墜速度
        if self.velocity_y > 10:
            self.velocity_y = 10

        # 應用速度到位置
        self.x += self.velocity_x
        self.y += self.velocity_y

        # 簡單的地面檢測（假設敵人都在地面上）
        # 實際遊戲中應該與平台系統整合
        if self.y > self.start_y:
            self.y = self.start_y
            self.velocity_y = 0
            self.is_on_ground = True
        else:
            self.is_on_ground = False

    def _update_animation(self):
        """
        更新動畫狀態\n
        \n
        根據移動方向和狀態更新動畫\n
        """
        # 根據移動方向更新面向
        if self.velocity_x > 0:
            self.facing_direction = 1
            self.sprite_flip = False
        elif self.velocity_x < 0:
            self.facing_direction = -1
            self.sprite_flip = True

    def _update_burn_effect(self):
        """
        更新燃燒狀態效果\n
        \n
        處理敵人燃燒時的持續傷害和視覺效果\n
        """
        if not self.is_burning or self.is_dead:
            return

        # 減少燃燒剩餘時間
        if self.burn_timer > 0:
            self.burn_timer -= 1

            # 更新燃燒傷害計時器
            self.burn_damage_timer += 1

            # 每隔一定時間造成燃燒傷害
            if self.burn_damage_timer >= self.burn_damage_interval:
                # 造成燃燒傷害（不會觸發額外的受傷效果）
                self._apply_burn_damage()
                self.burn_damage_timer = 0  # 重置傷害計時器

            # 更新燃燒粒子效果計時器
            self.burn_particle_timer += 1
        else:
            # 燃燒時間結束，移除燃燒狀態
            self.is_burning = False
            self.burn_damage_timer = 0
            self.burn_particle_timer = 0

    def _apply_burn_damage(self):
        """
        施加燃燒傷害\n
        \n
        對敵人造成燃燒的持續傷害，不觸發額外效果\n
        """
        burn_damage = 3  # 每次燃燒傷害

        # 直接減少血量，不觸發 take_damage 的額外效果
        self.health -= burn_damage

        # 血量不能低於 0
        if self.health <= 0:
            self.health = 0
            self.is_dead = True
            self.ai_state = "dead"
            self.is_burning = False  # 死亡時移除燃燒狀態

        # 輕微的視覺反饋（較短的閃爍）
        self.damage_flash_timer = 5  # 燃燒傷害的閃爍時間較短
        """
        更新死亡動畫\n
        \n
        處理敵人死亡後的視覺效果\n
        """
        self.death_timer += 1

    def _update_death_animation(self):
        """
        更新死亡動畫\n
        \n
        處理敵人死亡後的視覺效果\n
        """
        self.death_timer += 1

        # 死亡後逐漸消失
        if self.death_timer > 120:  # 2秒後完全消失
            # 這裡可以標記為可以從遊戲中移除
            pass

    def get_collision_rect(self) -> pygame.Rect:
        """
        取得敵人的碰撞矩形\n
        \n
        回傳:\n
        pygame.Rect: 用於碰撞檢測的矩形\n
        """
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def get_distance_to_player(self, player) -> float:
        """
        計算到玩家的距離\n
        \n
        參數:\n
        player: 玩家物件\n
        \n
        回傳:\n
        float: 到玩家的直線距離\n
        """
        dx = player.x - self.x
        dy = player.y - self.y
        return math.sqrt(dx * dx + dy * dy)

    def can_see_player(self, player) -> bool:
        """
        檢查是否能看見玩家\n
        \n
        簡化的視線檢查，實際遊戲可能需要射線檢測\n
        \n
        參數:\n
        player: 玩家物件\n
        \n
        回傳:\n
        bool: 是否在視線範圍內\n
        """
        distance = self.get_distance_to_player(player)
        return distance <= self.detection_range

    def can_attack_player(self, player) -> bool:
        """
        檢查是否能攻擊玩家\n
        \n
        參數:\n
        player: 玩家物件\n
        \n
        回傳:\n
        bool: 是否在攻擊範圍內且冷卻結束\n
        """
        if self.attack_cooldown > 0:
            return False

        distance = self.get_distance_to_player(player)
        return distance <= self.attack_range

    def take_damage(self, damage: int):
        """
        受到傷害\n
        \n
        處理敵人受傷邏輯\n
        \n
        參數:\n
        damage (int): 受到的傷害數值\n
        """
        self.health -= damage
        self.damage_flash_timer = 10  # 受傷閃爍 10 幀

        # 血量不能低於 0
        if self.health <= 0:
            self.health = 0
            self.is_dead = True
            self.ai_state = "dead"

        # 受傷時切換到追蹤狀態（如果不是死亡）
        if not self.is_dead and self.ai_state == "patrol":
            self.ai_state = "chase"

    def move_towards_player(self, player):
        """
        朝玩家方向移動\n
        \n
        計算並設定朝向玩家的移動速度\n
        \n
        參數:\n
        player: 玩家物件\n
        """
        dx = player.x - self.x

        # 只考慮水平移動（簡化處理）
        if abs(dx) > 5:  # 避免過度微調
            if dx > 0:
                self.velocity_x = self.speed
            else:
                self.velocity_x = -self.speed
        else:
            self.velocity_x = 0

    def patrol_movement(self):
        """
        巡邏移動邏輯\n
        \n
        在指定範圍內來回移動\n
        """
        # 到達巡邏邊界時轉向
        if self.x <= self.patrol_center_x - self.patrol_range:
            self.patrol_direction = 1
        elif self.x >= self.patrol_center_x + self.patrol_range:
            self.patrol_direction = -1

        # 設定巡邏速度
        self.velocity_x = self.patrol_direction * self.speed * 0.5  # 巡邏時慢一些

    def reset(self):
        """
        重置敵人狀態\n
        \n
        將敵人恢復到初始狀態，用於關卡重置\n
        """
        self.x = self.start_x
        self.y = self.start_y
        self.health = self.max_health
        self.is_dead = False
        self.ai_state = "patrol"
        self.velocity_x = 0
        self.velocity_y = 0
        self.attack_cooldown = 0
        self.damage_flash_timer = 0
        self.death_timer = 0
        self.animation_frame = 0
        self.facing_direction = 1
        self.patrol_direction = 1

        # 重置燃燒狀態
        self.is_burning = False
        self.burn_timer = 0
        self.burn_damage_timer = 0
        self.burn_particle_timer = 0

    def is_in_screen_bounds(self, screen: pygame.Surface, camera_y: float) -> bool:
        """
        檢查敵人是否在螢幕可見範圍內\n
        \n
        用於優化渲染效能\n
        \n
        參數:\n
        screen (pygame.Surface): 螢幕表面\n
        camera_y (float): 攝影機偏移\n
        \n
        回傳:\n
        bool: 是否在可見範圍內\n
        """
        screen_y = self.y - camera_y + screen.get_height() // 2

        return (
            -self.height < screen_y < screen.get_height() + self.height
            and -self.width < self.x < screen.get_width() + self.width
        )
