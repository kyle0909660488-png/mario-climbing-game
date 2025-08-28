######################載入套件######################
import pygame
import math
import random
from typing import List, Optional


######################火球投射物類別######################
class Fireball:
    """
    玩家發射的火球投射物\n
    \n
    實現火球的物理運動、碰撞檢測和視覺效果：\n
    1. 直線飛行物理運動\n
    2. 碰撞檢測（敵人、平台、螢幕邊界）\n
    3. 火球視覺效果和動畫\n
    4. 燃燒狀態效果處理\n
    \n
    屬性:\n
    x, y (float): 火球當前位置\n
    velocity_x, velocity_y (float): 火球飛行速度\n
    damage (int): 火球造成的初始傷害\n
    burn_damage (int): 燃燒狀態每次造成的持續傷害\n
    burn_duration (int): 燃燒狀態持續時間（幀數）\n
    is_active (bool): 火球是否還存在\n
    """

    def __init__(
        self,
        start_x: float,
        start_y: float,
        direction: int,
        player_attack: int = 25,
        speed: float = 8.0,
    ):
        """
        初始化火球\n
        \n
        根據發射位置、方向和玩家攻擊力創建火球物件\n
        \n
        參數:\n
        start_x (float): 發射起始 X 座標\n
        start_y (float): 發射起始 Y 座標\n
        direction (int): 發射方向（1: 右, -1: 左）\n
        player_attack (int): 玩家攻擊力，用於計算火球傷害\n
        speed (float): 火球飛行速度\n
        """
        # 基本位置和移動
        self.x = float(start_x)
        self.y = float(start_y)
        self.velocity_x = direction * speed
        self.velocity_y = 0.0  # 火球水平飛行，無垂直分量

        # 火球尺寸和碰撞
        self.width = 12
        self.height = 12
        self.radius = 6  # 圓形碰撞檢測用

        # 傷害設定 - 根據玩家攻擊力計算
        self.damage = int(player_attack * 0.8)  # 火球傷害為玩家攻擊力的80%
        self.burn_damage = max(
            1, int(player_attack * 0.1)
        )  # 燃燒傷害為攻擊力的10%，最少1點
        self.burn_duration = 300  # 燃燒持續時間（5秒 = 300幀）

        # 火球狀態
        self.is_active = True
        self.has_hit_enemy = False  # 是否已擊中敵人（防止重複傷害）

        # 動畫和視覺效果
        self.animation_frame = 0
        self.particle_trail = []  # 火焰軌跡粒子
        self.max_trail_particles = 8

        # 火球存活時間（防止永遠飛行）
        self.lifetime = 600  # 10秒後自動消失

    def update(self, platforms: List, screen_width: int = 800):
        """
        更新火球狀態\n
        \n
        處理火球的移動、碰撞檢測和粒子效果\n
        \n
        參數:\n
        platforms (List): 平台物件清單，用於碰撞檢測\n
        screen_width (int): 螢幕寬度，用於邊界檢測\n
        """
        if not self.is_active:
            return

        # 更新位置
        self.x += self.velocity_x
        self.y += self.velocity_y

        # 更新動畫幀
        self.animation_frame += 1

        # 更新粒子軌跡效果
        self._update_particle_trail()

        # 檢查螢幕邊界碰撞
        if self.x < -self.width or self.x > screen_width + self.width:
            self.is_active = False
            return

        # 檢查平台碰撞
        self._check_platform_collisions(platforms)

        # 檢查存活時間
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.is_active = False

    def _update_particle_trail(self):
        """
        更新火焰軌跡粒子效果\n
        \n
        創建跟隨火球的粒子軌跡，增強視覺效果\n
        """
        # 每3幀添加一個新粒子
        if self.animation_frame % 3 == 0:
            # 在火球後方隨機位置生成粒子
            particle_x = self.x + self.width // 2 - self.velocity_x * 0.5
            particle_y = self.y + self.height // 2 + (random.randint(-3, 3))

            particle = {
                "x": particle_x,
                "y": particle_y,
                "life": 15,  # 粒子存活時間
                "size": random.randint(2, 4),
                "opacity": 255,
            }

            self.particle_trail.append(particle)

        # 更新現有粒子
        particles_to_remove = []
        for i, particle in enumerate(self.particle_trail):
            particle["life"] -= 1
            particle["opacity"] = max(0, particle["opacity"] - 17)  # 逐漸透明
            particle["size"] = max(1, particle["size"] - 0.1)  # 逐漸縮小

            if particle["life"] <= 0:
                particles_to_remove.append(i)

        # 移除已消失的粒子
        for i in reversed(particles_to_remove):
            del self.particle_trail[i]

        # 限制粒子數量，避免效能問題
        if len(self.particle_trail) > self.max_trail_particles:
            self.particle_trail.pop(0)

    def _check_platform_collisions(self, platforms: List):
        """
        檢查與平台的碰撞\n
        \n
        火球撞到平台時會消失\n
        \n
        參數:\n
        platforms (List): 平台物件清單\n
        """
        fireball_rect = self.get_collision_rect()

        for platform in platforms:
            platform_rect = platform.get_collision_rect()
            if fireball_rect.colliderect(platform_rect):
                # 火球撞到平台，消失並產生爆炸效果
                self.is_active = False
                self._create_explosion_effect()
                break

    def _create_explosion_effect(self):
        """
        創建火球爆炸效果\n
        \n
        火球消失時產生爆炸粒子效果\n
        """
        # 生成爆炸粒子
        for _ in range(8):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 5)

            particle = {
                "x": self.x + self.width // 2,
                "y": self.y + self.height // 2,
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed,
                "life": random.randint(20, 40),
                "size": random.randint(3, 6),
                "opacity": 255,
            }

            self.particle_trail.append(particle)

    def check_enemy_collision(self, enemy) -> bool:
        """
        檢查與敵人的碰撞\n
        \n
        檢測火球是否擊中敵人，並處理傷害和燃燒效果\n
        \n
        參數:\n
        enemy: 敵人物件\n
        \n
        回傳:\n
        bool: 是否發生碰撞\n
        """
        if not self.is_active or self.has_hit_enemy:
            return False

        # 檢查圓形碰撞（更精確的碰撞檢測）
        enemy_rect = enemy.get_collision_rect()
        enemy_center_x = enemy_rect.x + enemy_rect.width // 2
        enemy_center_y = enemy_rect.y + enemy_rect.height // 2

        fireball_center_x = self.x + self.width // 2
        fireball_center_y = self.y + self.height // 2

        # 計算距離
        distance = math.sqrt(
            (enemy_center_x - fireball_center_x) ** 2
            + (enemy_center_y - fireball_center_y) ** 2
        )

        # 碰撞檢測（圓形與矩形的近似檢測）
        collision_distance = self.radius + min(enemy_rect.width, enemy_rect.height) // 2

        if distance <= collision_distance:
            # 對敵人造成直接傷害
            enemy.take_damage(self.damage)

            # 給敵人添加燃燒狀態
            self._apply_burn_effect(enemy)

            # 火球消失
            self.is_active = False
            self.has_hit_enemy = True
            self._create_explosion_effect()

            return True

        return False

    def _apply_burn_effect(self, enemy):
        """
        對敵人施加燃燒狀態效果\n
        \n
        為敵人添加燃燒狀態，造成持續傷害\n
        \n
        參數:\n
        enemy: 敵人物件\n
        """
        # 為敵人添加燃燒狀態
        # 如果敵人還沒有燃燒狀態屬性，就添加
        if not hasattr(enemy, "burn_timer"):
            enemy.burn_timer = 0
            enemy.burn_damage_timer = 0

        # 設定或重新設定燃燒狀態
        enemy.burn_timer = self.burn_duration  # 燃燒持續時間
        enemy.burn_damage_timer = 0  # 重置燃燒傷害計時器

        # 標記敵人正在燃燒
        enemy.is_burning = True

    def get_collision_rect(self) -> pygame.Rect:
        """
        取得火球的碰撞矩形\n
        \n
        回傳:\n
        pygame.Rect: 用於碰撞檢測的矩形\n
        """
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def render(self, screen: pygame.Surface, camera_y: float):
        """
        繪製火球和粒子效果\n
        \n
        在螢幕上繪製火球及其軌跡粒子效果\n
        \n
        參數:\n
        screen (pygame.Surface): 要繪製到的畫面\n
        camera_y (float): 攝影機 Y 軸偏移\n
        """
        if not self.is_active:
            return

        # 計算螢幕位置
        screen_x = int(self.x)
        screen_y = int(self.y - camera_y + screen.get_height() // 2)

        # 先繪製軌跡粒子（在火球後面）
        self._render_particles(screen, camera_y)

        # 繪製火球主體
        self._render_fireball_core(screen, screen_x, screen_y)

        # 繪製火球外圍光暈
        self._render_fireball_glow(screen, screen_x, screen_y)

    def _render_particles(self, screen: pygame.Surface, camera_y: float):
        """
        繪製粒子軌跡效果\n
        \n
        參數:\n
        screen (pygame.Surface): 螢幕表面\n
        camera_y (float): 攝影機偏移\n
        """
        for particle in self.particle_trail:
            particle_screen_x = int(particle["x"])
            particle_screen_y = int(particle["y"] - camera_y + screen.get_height() // 2)

            # 粒子顏色（從紅色到橙色到黃色）
            life_ratio = particle["life"] / 15.0
            if life_ratio > 0.7:
                # 紅色
                color = (255, int(100 + 100 * life_ratio), 0)
            elif life_ratio > 0.3:
                # 橙色
                color = (255, int(165 * life_ratio), 0)
            else:
                # 黃色淡化
                color = (255, 255, int(255 * life_ratio))

            # 調整透明度
            alpha = min(255, int(particle["opacity"] * life_ratio))

            # 繪製粒子（圓形）
            if alpha > 0 and particle["size"] > 0:
                size = max(1, int(particle["size"]))
                try:
                    # 創建帶透明度的表面
                    particle_surface = pygame.Surface(
                        (size * 2, size * 2), pygame.SRCALPHA
                    )
                    pygame.draw.circle(
                        particle_surface, (*color, alpha), (size, size), size
                    )
                    screen.blit(
                        particle_surface,
                        (particle_screen_x - size, particle_screen_y - size),
                    )
                except ValueError:
                    # 如果顏色值超出範圍，使用預設顏色
                    pygame.draw.circle(
                        screen,
                        (255, 100, 0),
                        (particle_screen_x, particle_screen_y),
                        size,
                    )

    def _render_fireball_core(
        self, screen: pygame.Surface, screen_x: int, screen_y: int
    ):
        """
        繪製火球核心\n
        \n
        參數:\n
        screen (pygame.Surface): 螢幕表面\n
        screen_x (int): 螢幕 X 座標\n
        screen_y (int): 螢幕 Y 座標\n
        """
        # 火球核心（明亮的橙紅色圓形）
        center_x = screen_x + self.width // 2
        center_y = screen_y + self.height // 2

        # 繪製火球核心（漸變效果，從內到外）
        for i in range(self.radius, 0, -1):
            # 顏色從白色（中心）到紅色（外圍）
            intensity = i / self.radius
            if intensity > 0.7:
                color = (255, 255, 200)  # 白熱色
            elif intensity > 0.4:
                color = (255, 200, 0)  # 黃色
            else:
                color = (255, 100, 0)  # 紅橙色

            pygame.draw.circle(screen, color, (center_x, center_y), i)

    def _render_fireball_glow(
        self, screen: pygame.Surface, screen_x: int, screen_y: int
    ):
        """
        繪製火球外圍光暈效果\n
        \n
        參數:\n
        screen (pygame.Surface): 螢幕表面\n
        screen_x (int): 螢幕 X 座標\n
        screen_y (int): 螢幕 Y 座標\n
        """
        center_x = screen_x + self.width // 2
        center_y = screen_y + self.height // 2

        # 動態光暈效果（根據動畫幀數變化）
        glow_radius = self.radius + 3 + int(math.sin(self.animation_frame * 0.3) * 2)

        # 繪製外圍光暈（半透明）
        try:
            glow_surface = pygame.Surface(
                (glow_radius * 2, glow_radius * 2), pygame.SRCALPHA
            )
            glow_color = (255, 150, 0, 100)  # 橙色半透明
            pygame.draw.circle(
                glow_surface, glow_color, (glow_radius, glow_radius), glow_radius
            )
            screen.blit(glow_surface, (center_x - glow_radius, center_y - glow_radius))
        except:
            # 如果透明度繪製失敗，使用普通繪製
            pygame.draw.circle(
                screen, (255, 150, 0), (center_x, center_y), glow_radius, 2
            )

    def is_in_screen_bounds(
        self, screen_width: int, screen_height: int, camera_y: float
    ) -> bool:
        """
        檢查火球是否在螢幕可見範圍內\n
        \n
        用於優化渲染效能\n
        \n
        參數:\n
        screen_width (int): 螢幕寬度\n
        screen_height (int): 螢幕高度\n
        camera_y (float): 攝影機偏移\n
        \n
        回傳:\n
        bool: 是否在可見範圍內\n
        """
        screen_y = self.y - camera_y + screen_height // 2

        return (
            -self.width < self.x < screen_width + self.width
            and -self.height < screen_y < screen_height + self.height
        )


######################火球管理器######################
class FireballManager:
    """
    火球管理器\n
    \n
    管理所有活躍的火球：\n
    1. 火球的生成和移除\n
    2. 批量更新所有火球\n
    3. 批量渲染所有火球\n
    4. 火球與敵人的碰撞檢測\n
    """

    def __init__(self):
        """
        初始化火球管理器\n
        """
        self.fireballs = []  # 儲存所有活躍的火球

    def create_fireball(
        self, player_x: float, player_y: float, direction: int, player_attack: int = 25
    ):
        """
        創建新火球\n
        \n
        在玩家位置發射火球\n
        \n
        參數:\n
        player_x (float): 玩家 X 座標\n
        player_y (float): 玩家 Y 座標\n
        direction (int): 發射方向（1: 右, -1: 左）\n
        player_attack (int): 玩家攻擊力，影響火球傷害\n
        """
        # 計算火球發射位置（在玩家前方稍微偏移）
        offset_x = 15 * direction  # 在玩家前方15像素
        offset_y = 0  # 與玩家中心同高度，提高命中率

        fireball = Fireball(
            start_x=player_x + offset_x,
            start_y=player_y + offset_y,
            direction=direction,
            player_attack=player_attack,  # 傳入玩家攻擊力
        )

        self.fireballs.append(fireball)

    def update(self, platforms: List, enemies: List, screen_width: int = 800):
        """
        更新所有火球\n
        \n
        處理火球移動、碰撞檢測，移除無效火球\n
        \n
        參數:\n
        platforms (List): 平台物件清單\n
        enemies (List): 敵人物件清單\n
        screen_width (int): 螢幕寬度\n
        """
        # 更新每個火球
        for fireball in self.fireballs[:]:  # 使用切片複製避免迭代時修改列表
            fireball.update(platforms, screen_width)

            # 檢查與敵人的碰撞
            for enemy in enemies:
                if not enemy.is_dead:
                    fireball.check_enemy_collision(enemy)

        # 移除無效的火球
        self.fireballs = [fb for fb in self.fireballs if fb.is_active]

    def render_all(self, screen: pygame.Surface, camera_y: float):
        """
        渲染所有火球\n
        \n
        參數:\n
        screen (pygame.Surface): 螢幕表面\n
        camera_y (float): 攝影機偏移\n
        """
        for fireball in self.fireballs:
            if fireball.is_in_screen_bounds(
                screen.get_width(), screen.get_height(), camera_y
            ):
                fireball.render(screen, camera_y)

    def clear_all(self):
        """
        清除所有火球\n
        \n
        用於關卡切換或遊戲重置\n
        """
        self.fireballs.clear()

    def get_active_count(self) -> int:
        """
        取得當前活躍火球數量\n
        \n
        回傳:\n
        int: 活躍火球數量\n
        """
        return len(self.fireballs)
