######################載入套件######################
import pygame
import math
import random
from typing import Tuple
from src.enemies.base_enemy import BaseEnemy


######################基本敵人類別######################
class BasicEnemy(BaseEnemy):
    """
    基本敵人類別\n
    \n
    最簡單的敵人類型，具有基本的 AI 行為：\n
    1. 在固定範圍內巡邏\n
    2. 發現玩家時會追蹤\n
    3. 接近玩家時進行近戰攻擊\n
    4. 失去目標後返回巡邏\n
    \n
    特性:\n
    - 中等血量和攻擊力\n
    - 簡單但有效的 AI\n
    - 適合作為關卡的基礎威脅\n
    - 可以成群出現增加挑戰\n
    """

    def __init__(self, x: float, y: float, patrol_range: int = 100):
        """
        初始化基本敵人\n
        \n
        參數:\n
        x (float): 敵人起始 X 座標\n
        y (float): 敵人起始 Y 座標\n
        patrol_range (int): 巡邏範圍，敵人會在起始點左右這個距離內移動\n
        """
        # 設定基本敵人的屬性
        super().__init__(x, y, health=60, attack_damage=18, speed=1.5)

        # 基本敵人的特殊屬性
        self.patrol_range = patrol_range
        self.patrol_center_x = x

        # 外觀設定
        self.enemy_color = (150, 50, 50)  # 深紅色
        self.damaged_color = (255, 100, 100)  # 受傷時的淺紅色
        self.dead_color = (80, 30, 30)  # 死亡時的暗紅色

        # AI 特殊狀態
        self.chase_timer = 0  # 追蹤狀態計時器
        self.lose_target_timer = 300  # 5秒後失去目標返回巡邏
        self.aggressive_mode = False  # 是否進入激進模式

        # 攻擊相關
        self.attack_windup = 0  # 攻擊前搖時間
        self.attack_active = 0  # 攻擊判定持續時間

    def update_ai(self, player):
        """
        更新基本敵人的 AI 行為\n
        \n
        實現狀態機邏輯：巡邏 → 追蹤 → 攻擊 → 返回巡邏\n
        \n
        參數:\n
        player: 玩家物件\n
        """
        if self.is_dead:
            return

        # 更新狀態計時器
        if self.ai_state == "chase":
            self.chase_timer += 1

        # 狀態機邏輯
        if self.ai_state == "patrol":
            self._handle_patrol_state(player)
        elif self.ai_state == "chase":
            self._handle_chase_state(player)
        elif self.ai_state == "attack":
            self._handle_attack_state(player)

    def _handle_patrol_state(self, player):
        """
        處理巡邏狀態\n
        \n
        在巡邏範圍內移動，同時檢查是否發現玩家\n
        \n
        參數:\n
        player: 玩家物件\n
        """
        # 執行巡邏移動
        self.patrol_movement()

        # 檢查是否發現玩家
        if self.can_see_player(player):
            self.ai_state = "chase"
            self.target_player = player
            self.last_known_player_pos = (player.x, player.y)
            self.chase_timer = 0
            # 發現玩家時稍微加速
            self.speed *= 1.2

    def _handle_chase_state(self, player):
        """
        處理追蹤狀態\n
        \n
        朝玩家方向移動，檢查攻擊時機或失去目標\n
        \n
        參數:\n
        player: 玩家物件\n
        """
        # 檢查是否能攻擊
        if self.can_attack_player(player):
            self.ai_state = "attack"
            self.attack_windup = 30  # 30幀的攻擊前搖
            self.velocity_x = 0  # 攻擊時停止移動
            return

        # 檢查是否還能看見玩家
        if self.can_see_player(player):
            # 更新最後已知位置
            self.last_known_player_pos = (player.x, player.y)
            self.chase_timer = 0

            # 朝玩家移動
            self.move_towards_player(player)

            # 如果追蹤太久，進入激進模式（速度更快）
            if not self.aggressive_mode and self.chase_timer > 180:  # 3秒後
                self.aggressive_mode = True
                self.speed *= 1.3
                self.attack_range *= 1.2  # 攻擊距離也增加
        else:
            # 看不見玩家，朝最後已知位置移動
            if self.last_known_player_pos:
                dx = self.last_known_player_pos[0] - self.x
                if abs(dx) > 10:
                    self.velocity_x = self.speed if dx > 0 else -self.speed
                else:
                    # 到達最後已知位置，開始失去目標計時
                    self.last_known_player_pos = None

            self.chase_timer += 1

        # 追蹤太久就返回巡邏
        if self.chase_timer > self.lose_target_timer:
            self._return_to_patrol()

    def _handle_attack_state(self, player):
        """
        處理攻擊狀態\n
        \n
        執行攻擊動作和後續處理\n
        \n
        參數:\n
        player: 玩家物件\n
        """
        if self.attack_windup > 0:
            # 攻擊前搖階段
            self.attack_windup -= 1
            self.velocity_x = 0  # 攻擊準備時不移動

            # 稍微後退蓄力
            if self.attack_windup > 15:
                self.velocity_x = -self.facing_direction * 0.5

        elif self.attack_active > 0:
            # 攻擊判定階段
            self.attack_active -= 1

            # 攻擊判定（只在第一幀執行）
            if self.attack_active == 9:  # 攻擊持續10幀，第一幀執行傷害
                attack_result = self.attack_player(player)

                # 攻擊時向前衝刺
                self.velocity_x = self.facing_direction * self.speed * 2

        else:
            # 開始攻擊判定
            if self.attack_windup == 0 and self.attack_active == 0:
                self.attack_active = 10  # 10幀的攻擊判定時間
            else:
                # 攻擊結束，設定冷卻時間
                self.attack_cooldown = self.max_attack_cooldown

                # 根據情況決定下一個狀態
                if (
                    self.can_see_player(player)
                    and self.get_distance_to_player(player) > self.attack_range
                ):
                    self.ai_state = "chase"  # 繼續追蹤
                else:
                    self.ai_state = "chase"  # 先返回追蹤狀態

    def _return_to_patrol(self):
        """
        返回巡邏狀態\n
        \n
        重置追蹤相關的狀態並返回巡邏\n
        """
        self.ai_state = "patrol"
        self.target_player = None
        self.last_known_player_pos = None
        self.chase_timer = 0
        self.aggressive_mode = False

        # 恢復原本的速度和攻擊距離
        self.speed = 1.5
        self.attack_range = 40

    def attack_player(self, player) -> dict:
        """
        攻擊玩家\n
        \n
        執行對玩家的攻擊，造成傷害和效果\n
        \n
        參數:\n
        player: 玩家物件\n
        \n
        回傳:\n
        dict: 攻擊結果資訊\n
        """
        # 檢查攻擊是否命中
        attack_rect = self.get_attack_rect()
        player_rect = player.get_collision_rect()

        if attack_rect.colliderect(player_rect):
            # 造成傷害
            damage = self.attack_damage
            if self.aggressive_mode:
                damage = int(damage * 1.2)  # 激進模式傷害加成

            player.take_damage(damage)

            # 計算擊退方向
            knockback_x = 3 if player.x > self.x else -3
            knockback_y = -1  # 輕微向上擊退

            return {
                "hit": True,
                "damage": damage,
                "knockback": (knockback_x, knockback_y),
                "effect": "basic_melee_hit",
            }
        else:
            return {"hit": False, "effect": "attack_miss"}

    def get_attack_rect(self) -> pygame.Rect:
        """
        取得攻擊範圍矩形\n
        \n
        回傳:\n
        pygame.Rect: 攻擊判定範圍\n
        """
        # 攻擊範圍在敵人前方
        attack_width = 35
        attack_height = self.height

        if self.facing_direction == 1:  # 面向右
            attack_x = self.x + self.width
        else:  # 面向左
            attack_x = self.x - attack_width

        return pygame.Rect(attack_x, self.y, attack_width, attack_height)

    def render(self, screen: pygame.Surface, camera_y: float):
        """
        繪製基本敵人\n
        \n
        繪製敵人的外觀和狀態指示器\n
        \n
        參數:\n
        screen (pygame.Surface): 螢幕表面\n
        camera_y (float): 攝影機偏移\n
        """
        if not self.is_in_screen_bounds(screen, camera_y):
            return

        # 計算螢幕座標
        screen_x = int(self.x)
        screen_y = int(self.y - camera_y + screen.get_height() // 2)

        # 根據狀態選擇顏色
        color = self.enemy_color

        if self.is_dead:
            color = self.dead_color
        elif self.damage_flash_timer > 0:
            # 受傷時閃爍
            if (self.damage_flash_timer // 2) % 2:
                color = self.damaged_color
        elif self.aggressive_mode:
            # 激進模式時顏色更深
            color = tuple(max(0, c - 30) for c in self.enemy_color)

        # 繪製敵人主體
        enemy_rect = pygame.Rect(screen_x, screen_y, self.width, self.height)
        pygame.draw.rect(screen, color, enemy_rect)

        # 繪製邊框
        border_color = (0, 0, 0) if not self.is_dead else (50, 50, 50)
        pygame.draw.rect(screen, border_color, enemy_rect, 2)

        # 繪製眼睛（簡單的點）
        if not self.is_dead:
            eye_color = (255, 255, 255) if not self.aggressive_mode else (255, 0, 0)

            if self.facing_direction == 1:  # 面向右
                eye_x = screen_x + self.width - 8
            else:  # 面向左
                eye_x = screen_x + 5

            pygame.draw.circle(screen, eye_color, (eye_x, screen_y + 8), 3)

        # 繪製血量條
        self._draw_health_bar(screen, screen_x, screen_y - 8)

        # 繪製燃燒效果（如果正在燃燒）
        if self.is_burning:
            self._draw_burn_effect(screen, screen_x, screen_y)

        # 繪製狀態指示器
        self._draw_state_indicator(screen, screen_x, screen_y)

        # 攻擊時繪製攻擊範圍
        if self.ai_state == "attack" and self.attack_active > 0:
            self._draw_attack_range(screen, camera_y)

    def _draw_health_bar(self, screen: pygame.Surface, x: int, y: int):
        """
        繪製血量條\n
        \n
        在敵人上方顯示血量狀態\n
        """
        if self.is_dead:
            return

        bar_width = self.width
        bar_height = 4

        # 血量條背景
        pygame.draw.rect(screen, (100, 100, 100), (x, y, bar_width, bar_height))

        # 血量條前景
        health_ratio = self.health / self.max_health
        health_width = int(bar_width * health_ratio)

        # 根據血量比例決定顏色
        if health_ratio > 0.6:
            health_color = (0, 255, 0)  # 綠色
        elif health_ratio > 0.3:
            health_color = (255, 255, 0)  # 黃色
        else:
            health_color = (255, 0, 0)  # 紅色

        if health_width > 0:
            pygame.draw.rect(screen, health_color, (x, y, health_width, bar_height))

    def _draw_state_indicator(self, screen: pygame.Surface, x: int, y: int):
        """
        繪製狀態指示器\n
        \n
        用不同顏色的小圓點表示 AI 狀態\n
        """
        if self.is_dead:
            return

        # 狀態顏色對應
        state_colors = {
            "patrol": (0, 255, 0),  # 綠色：巡邏
            "chase": (255, 255, 0),  # 黃色：追蹤
            "attack": (255, 0, 0),  # 紅色：攻擊
        }

        state_color = state_colors.get(self.ai_state, (128, 128, 128))

        # 在敵人右上角繪製狀態點
        pygame.draw.circle(screen, state_color, (x + self.width - 5, y - 5), 4)

    def _draw_burn_effect(self, screen: pygame.Surface, x: int, y: int):
        """
        繪製燃燒效果\n
        \n
        在燃燒的敵人身上繪製火焰粒子效果\n
        \n
        參數:\n
        screen (pygame.Surface): 螢幕表面\n
        x (int): 敵人螢幕 X 座標\n
        y (int): 敵人螢幕 Y 座標\n
        """
        if not self.is_burning:
            return

        import random
        import math

        # 繪製燃燒粒子效果
        for i in range(6):  # 6個火焰粒子
            # 粒子位置隨機分布在敵人周圍
            offset_x = random.randint(-5, 5)
            offset_y = random.randint(-10, 5)

            particle_x = x + self.width // 2 + offset_x
            particle_y = (
                y + offset_y + int(math.sin(self.burn_particle_timer * 0.2 + i) * 3)
            )

            # 粒子顏色（橙紅色變化）
            flame_colors = [
                (255, 100, 0),  # 橙色
                (255, 150, 0),  # 橙黃色
                (255, 50, 0),  # 紅橙色
                (255, 200, 0),  # 黃色
            ]

            color = flame_colors[i % len(flame_colors)]

            # 根據燃燒時間調整粒子大小
            size = 2 + int((self.burn_timer % 60) / 15)  # 大小在2-5之間變化

            # 繪製火焰粒子
            pygame.draw.circle(screen, color, (particle_x, particle_y), size)

        # 繪製燃燒光暈（敵人周圍的橙色光暈）
        glow_alpha = 50 + int(math.sin(self.burn_particle_timer * 0.1) * 30)
        try:
            glow_surface = pygame.Surface(
                (self.width + 10, self.height + 10), pygame.SRCALPHA
            )
            glow_color = (255, 100, 0, glow_alpha)
            pygame.draw.rect(
                glow_surface,
                glow_color,
                (5, 5, self.width, self.height),
                border_radius=3,
            )
            screen.blit(glow_surface, (x - 5, y - 5))
        except:
            # 如果透明度繪製失敗，使用普通邊框
            pygame.draw.rect(
                screen,
                (255, 100, 0),
                (x - 2, y - 2, self.width + 4, self.height + 4),
                2,
            )

    def _draw_attack_range(self, screen: pygame.Surface, camera_y: float):
        """
        繪製攻擊範圍\n
        \n
        攻擊時顯示攻擊判定區域\n
        """
        attack_rect = self.get_attack_rect()
        screen_attack_rect = pygame.Rect(
            attack_rect.x,
            attack_rect.y - camera_y + screen.get_height() // 2,
            attack_rect.width,
            attack_rect.height,
        )

        # 用半透明紅色顯示攻擊範圍
        attack_color = (255, 0, 0, 100)
        pygame.draw.rect(screen, (255, 0, 0), screen_attack_rect, 3)
