######################載入套件######################
import pygame
import math
import random
from typing import List, Optional


######################冰球投射物類別######################
class Iceball:
    """
    玩家發射的冰球投射物\n
    \n
    實現冰球的物理運動、碰撞檢測和視覺效果：\n
    1. 直線飛行物理運動\n
    2. 碰撞檢測（敵人、平台、螢幕邊界）\n
    3. 冰球視覺效果和動畫\n
    4. 暈眩狀態效果處理\n
    \n
    屬性:\n
    x, y (float): 冰球當前位置\n
    velocity_x, velocity_y (float): 冰球飛行速度\n
    damage (int): 冰球造成的傷害\n
    stun_duration (int): 暈眩狀態持續時間（幀數）\n
    is_active (bool): 冰球是否還存在\n
    """

    def __init__(
        self, start_x: float, start_y: float, direction: int, speed: float = 8.0
    ):
        """
        初始化冰球\n
        \n
        根據發射位置和方向創建冰球物件\n
        \n
        參數:\n
        start_x (float): 發射起始 X 座標\n
        start_y (float): 發射起始 Y 座標\n
        direction (int): 發射方向（1: 右, -1: 左）\n
        speed (float): 冰球飛行速度\n
        """
        # 基本位置和移動
        self.x = float(start_x)
        self.y = float(start_y)
        self.velocity_x = direction * speed
        self.velocity_y = 0.0  # 冰球水平飛行，無垂直分量

        # 冰球尺寸和碰撞
        self.width = 12
        self.height = 12
        self.radius = 6  # 圓形碰撞檢測用

        # 傷害設定
        self.damage = 25  # 冰球直接命中傷害（和火焰球一樣）
        self.stun_duration = 180  # 暈眩持續時間（3秒 = 180幀）

        # 冰球狀態
        self.is_active = True
        self.has_hit_enemy = False  # 是否已擊中敵人（防止重複傷害）

        # 動畫和視覺效果
        self.animation_frame = 0
        self.particle_trail = []  # 冰霜軌跡粒子
        self.max_trail_particles = 8

        # 冰球存活時間（防止永遠飛行）
        self.lifetime = 600  # 10秒後自動消失

    def update(self, platforms: List, screen_width: int = 800):
        """
        更新冰球狀態\n
        \n
        處理冰球的移動、碰撞檢測和粒子效果\n
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
        更新冰霜軌跡粒子效果\n
        \n
        創建跟隨冰球的粒子軌跡，增強視覺效果\n
        """
        # 每3幀添加一個新粒子
        if self.animation_frame % 3 == 0:
            # 在冰球後方隨機位置生成粒子
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
        冰球撞到平台時會消失\n
        \n
        參數:\n
        platforms (List): 平台物件清單\n
        """
        iceball_rect = self.get_collision_rect()

        for platform in platforms:
            platform_rect = platform.get_collision_rect()
            if iceball_rect.colliderect(platform_rect):
                # 冰球撞到平台，消失並產生碎裂效果
                self.is_active = False
                self._create_shatter_effect()
                break

    def _create_shatter_effect(self):
        """
        創建冰球碎裂效果\n
        \n
        冰球消失時產生碎裂粒子效果\n
        """
        # 生成碎裂粒子
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
        檢測冰球是否擊中敵人，並處理傷害和暈眩效果\n
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

        iceball_center_x = self.x + self.width // 2
        iceball_center_y = self.y + self.height // 2

        # 計算距離
        distance = math.sqrt(
            (enemy_center_x - iceball_center_x) ** 2
            + (enemy_center_y - iceball_center_y) ** 2
        )

        # 碰撞檢測（圓形與矩形的近似檢測）
        collision_distance = self.radius + min(enemy_rect.width, enemy_rect.height) // 2

        if distance <= collision_distance:
            # 對敵人造成直接傷害
            enemy.take_damage(self.damage)

            # 給敵人添加暈眩狀態
            self._apply_stun_effect(enemy)

            # 冰球消失
            self.is_active = False
            self.has_hit_enemy = True
            self._create_shatter_effect()

            return True

        return False

    def _apply_stun_effect(self, enemy):
        """
        對敵人施加暈眩狀態效果\n
        \n
        為敵人添加暈眩狀態，暫停 AI 行為\n
        \n
        參數:\n
        enemy: 敵人物件\n
        """
        # 為敵人添加暈眩狀態
        # 如果敵人還沒有暈眩狀態屬性，就添加
        if not hasattr(enemy, "stunned_time"):
            enemy.stunned_time = 0

        # 設定或重新設定暈眩狀態
        enemy.stunned_time = self.stun_duration  # 暈眩持續時間

        # 標記敵人正在被暈眩
        enemy.is_stunned = True

    def get_collision_rect(self) -> pygame.Rect:
        """
        取得冰球的碰撞矩形\n
        \n
        回傳:\n
        pygame.Rect: 用於碰撞檢測的矩形\n
        """
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def render(self, screen: pygame.Surface, camera_y: float):
        """
        繪製冰球和粒子效果\n
        \n
        在螢幕上繪製冰球及其軌跡粒子效果\n
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

        # 先繪製軌跡粒子（在冰球後面）
        self._render_particles(screen, camera_y)

        # 繪製冰球主體
        self._render_iceball_core(screen, screen_x, screen_y)

        # 繪製冰球外圍光暈
        self._render_iceball_glow(screen, screen_x, screen_y)

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

            # 粒子顏色（從淺藍色到白色）
            life_ratio = particle["life"] / 15.0
            if life_ratio > 0.7:
                # 淺藍色
                color = (150, 200, 255)
            elif life_ratio > 0.3:
                # 藍白色
                color = (200, 220, 255)
            else:
                # 白色淡化
                color = (255, 255, 255)

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
                        (150, 200, 255),
                        (particle_screen_x, particle_screen_y),
                        size,
                    )

    def _render_iceball_core(
        self, screen: pygame.Surface, screen_x: int, screen_y: int
    ):
        """
        繪製冰球核心\n
        \n
        參數:\n
        screen (pygame.Surface): 螢幕表面\n
        screen_x (int): 螢幕 X 座標\n
        screen_y (int): 螢幕 Y 座標\n
        """
        # 冰球核心（明亮的藍白色圓形）
        center_x = screen_x + self.width // 2
        center_y = screen_y + self.height // 2

        # 繪製冰球核心（漸變效果，從內到外）
        for i in range(self.radius, 0, -1):
            # 顏色從白色（中心）到藍色（外圍）
            intensity = i / self.radius
            if intensity > 0.7:
                color = (255, 255, 255)  # 白色
            elif intensity > 0.4:
                color = (200, 230, 255)  # 淺藍白色
            else:
                color = (100, 150, 255)  # 藍色

            pygame.draw.circle(screen, color, (center_x, center_y), i)

    def _render_iceball_glow(
        self, screen: pygame.Surface, screen_x: int, screen_y: int
    ):
        """
        繪製冰球外圍光暈效果\n
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
            glow_color = (150, 200, 255, 100)  # 藍色半透明
            pygame.draw.circle(
                glow_surface, glow_color, (glow_radius, glow_radius), glow_radius
            )
            screen.blit(glow_surface, (center_x - glow_radius, center_y - glow_radius))
        except:
            # 如果透明度繪製失敗，使用普通繪製
            pygame.draw.circle(
                screen, (150, 200, 255), (center_x, center_y), glow_radius, 2
            )

    def is_in_screen_bounds(
        self, screen_width: int, screen_height: int, camera_y: float
    ) -> bool:
        """
        檢查冰球是否在螢幕可見範圍內\n
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


######################冰球管理器######################
class IceballManager:
    """
    冰球管理器\n
    \n
    管理所有活躍的冰球：\n
    1. 冰球的生成和移除\n
    2. 批量更新所有冰球\n
    3. 批量渲染所有冰球\n
    4. 冰球與敵人的碰撞檢測\n
    """

    def __init__(self):
        """
        初始化冰球管理器\n
        """
        self.iceballs = []  # 儲存所有活躍的冰球

    def create_iceball(self, player_x: float, player_y: float, direction: int):
        """
        創建新冰球\n
        \n
        在玩家位置發射冰球\n
        \n
        參數:\n
        player_x (float): 玩家 X 座標\n
        player_y (float): 玩家 Y 座標\n
        direction (int): 發射方向（1: 右, -1: 左）\n
        """
        # 計算冰球發射位置（在玩家前方稍微偏移）
        offset_x = 15 * direction  # 在玩家前方15像素
        offset_y = 0  # 與玩家中心同高度，提高命中率

        iceball = Iceball(
            start_x=player_x + offset_x,
            start_y=player_y + offset_y,
            direction=direction,
        )

        self.iceballs.append(iceball)

    def update(self, platforms: List, enemies: List, screen_width: int = 800):
        """
        更新所有冰球\n
        \n
        處理冰球移動、碰撞檢測，移除無效冰球\n
        \n
        參數:\n
        platforms (List): 平台物件清單\n
        enemies (List): 敵人物件清單\n
        screen_width (int): 螢幕寬度\n
        """
        # 更新每個冰球
        for iceball in self.iceballs[:]:  # 使用切片複製避免迭代時修改列表
            iceball.update(platforms, screen_width)

            # 檢查與敵人的碰撞
            for enemy in enemies:
                if not enemy.is_dead:
                    iceball.check_enemy_collision(enemy)

        # 移除無效的冰球
        self.iceballs = [ib for ib in self.iceballs if ib.is_active]

    def render_all(self, screen: pygame.Surface, camera_y: float):
        """
        渲染所有冰球\n
        \n
        參數:\n
        screen (pygame.Surface): 螢幕表面\n
        camera_y (float): 攝影機偏移\n
        """
        for iceball in self.iceballs:
            if iceball.is_in_screen_bounds(
                screen.get_width(), screen.get_height(), camera_y
            ):
                iceball.render(screen, camera_y)

    def clear_all(self):
        """
        清除所有冰球\n
        \n
        用於關卡切換或遊戲重置\n
        """
        self.iceballs.clear()

    def get_active_count(self) -> int:
        """
        取得當前活躍冰球數量\n
        \n
        回傳:\n
        int: 活躍冰球數量\n
        """
        return len(self.iceballs)
