######################載入套件######################
import pygame
import math
import random
from typing import Tuple, List
from src.traps.base_trap import BaseTrap


######################火焰牆陷阱類別######################
class FireWall(BaseTrap):
    """
    火焰牆陷阱類別\n
    \n
    持續性傷害陷阱，會產生火焰效果：\n
    1. 持續造成傷害（比尖刺傷害高）\n
    2. 動態火焰視覺效果\n
    3. 週期性的強度變化\n
    4. 向上的擊退效果\n
    \n
    特性:\n
    - 持續性危險，需要快速通過\n
    - 較高的傷害值\n
    - 有預警階段（火焰變化）\n
    - 可以阻擋路徑或作為時間挑戰\n
    """

    def __init__(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        damage: int = 35,
        fire_intensity: str = "normal",
    ):
        """
        初始化火焰牆陷阱\n
        \n
        參數:\n
        x (float): 火焰牆左上角 X 座標\n
        y (float): 火焰牆左上角 Y 座標（通常是底部）\n
        width (float): 火焰牆寬度\n
        height (float): 火焰牆高度\n
        damage (int): 造成的傷害值\n
        fire_intensity (str): 火焰強度 ('low', 'normal', 'high')\n
        """
        # 火焰牆的冷卻時間較短，因為是持續性陷阱
        super().__init__(x, y, width, height, damage, cooldown=20)

        self.fire_intensity = fire_intensity
        self.intensity_cycle = 0  # 火焰強度變化週期

        # 火焰顏色設定
        self.base_colors = {
            "low": [(255, 100, 0), (255, 150, 0), (200, 80, 0)],  # 橘紅色
            "normal": [(255, 0, 0), (255, 100, 0), (255, 200, 0)],  # 紅橘黃色
            "high": [(255, 255, 255), (255, 0, 0), (255, 100, 0)],  # 白紅橘色
        }

        # 火焰粒子系統
        self.flame_particles = []
        self.max_particles = max(10, int(self.width * self.height / 100))

        # 火焰動畫狀態
        self.flame_phase = 0
        self.pulsing_intensity = 1.0

        # 初始化火焰粒子
        self._initialize_particles()

    def _initialize_particles(self):
        """
        初始化火焰粒子系統\n
        \n
        建立火焰效果所需的粒子物件\n
        """
        self.flame_particles = []

        for _ in range(self.max_particles):
            particle = {
                "x": random.uniform(self.x, self.x + self.width),
                "y": random.uniform(self.y, self.y + self.height),
                "vx": random.uniform(-1, 1),  # 水平速度
                "vy": random.uniform(-3, -1),  # 向上移動
                "life": random.uniform(0.5, 1.0),  # 生命週期
                "max_life": random.uniform(0.5, 1.0),
                "size": random.uniform(3, 8),
                "color_index": random.randint(0, 2),
            }
            self.flame_particles.append(particle)

    def update(self):
        """
        更新火焰牆狀態\n
        \n
        更新火焰動畫、粒子系統和強度變化\n
        """
        self._update_base_properties()

        # 更新火焰強度週期
        self.intensity_cycle += 1
        self.flame_phase = (self.flame_phase + 0.1) % (2 * math.pi)

        # 計算脈動強度（用於火焰大小變化）
        self.pulsing_intensity = 0.7 + 0.3 * math.sin(self.flame_phase * 2)

        # 更新火焰粒子
        self._update_particles()

        # 根據強度週期調整傷害
        if self.intensity_cycle % 180 == 0:  # 每 3 秒變化一次
            self._cycle_intensity()

    def _update_particles(self):
        """
        更新火焰粒子系統\n
        \n
        處理每個粒子的移動、生命週期和重生\n
        """
        colors = self.base_colors[self.fire_intensity]

        for particle in self.flame_particles:
            # 更新粒子位置
            particle["x"] += particle["vx"]
            particle["y"] += particle["vy"] * self.pulsing_intensity

            # 更新生命週期
            particle["life"] -= 0.02

            # 粒子死亡後重生
            if particle["life"] <= 0:
                particle["x"] = random.uniform(self.x, self.x + self.width)
                particle["y"] = self.y + self.height  # 從底部重生
                particle["vx"] = random.uniform(-1, 1)
                particle["vy"] = random.uniform(-3, -1)
                particle["life"] = particle["max_life"]
                particle["color_index"] = random.randint(0, len(colors) - 1)

            # 限制粒子在火焰區域內
            if particle["x"] < self.x or particle["x"] > self.x + self.width:
                particle["vx"] *= -0.5  # 反彈但減速

    def _cycle_intensity(self):
        """
        週期性改變火焰強度\n
        \n
        讓火焰在不同強度間切換，增加視覺變化\n
        """
        intensities = ["low", "normal", "high"]
        current_index = intensities.index(self.fire_intensity)

        # 大部分時間保持 normal，偶爾變化
        if random.random() < 0.7:
            self.fire_intensity = "normal"
        else:
            # 隨機切換到其他強度
            self.fire_intensity = random.choice(
                [i for i in intensities if i != self.fire_intensity]
            )

    def render(self, screen: pygame.Surface, camera_y: float):
        """
        繪製火焰牆\n
        \n
        繪製動態的火焰效果和粒子\n
        \n
        參數:\n
        screen (pygame.Surface): 螢幕表面\n
        camera_y (float): 攝影機偏移\n
        """
        if not self.is_in_screen_bounds(screen, camera_y):
            return

        # 計算螢幕座標
        screen_y = self.y - camera_y + screen.get_height() // 2

        # 繪製火焰基座（深紅色）
        base_rect = pygame.Rect(self.x, screen_y + self.height - 10, self.width, 10)
        pygame.draw.rect(screen, (100, 0, 0), base_rect)

        # 繪製火焰粒子
        self._render_flame_particles(screen, camera_y)

        # 繪製火焰主體（半透明效果）
        self._render_flame_body(screen, screen_y)

        # 觸發時的特殊效果
        if self.flash_timer > 0:
            self._render_trigger_effect(screen, screen_y)

    def _render_flame_particles(self, screen: pygame.Surface, camera_y: float):
        """
        繪製火焰粒子\n
        \n
        渲染所有火焰粒子，創造動態火焰效果\n
        """
        colors = self.base_colors[self.fire_intensity]

        for particle in self.flame_particles:
            if particle["life"] > 0:
                # 計算粒子的螢幕位置
                particle_screen_y = particle["y"] - camera_y + screen.get_height() // 2

                # 根據生命週期調整透明度和大小
                life_ratio = particle["life"] / particle["max_life"]
                size = int(particle["size"] * life_ratio * self.pulsing_intensity)

                if size > 1:
                    # 選擇顏色
                    color = colors[particle["color_index"]]

                    # 根據生命週期調整顏色強度，確保數值在有效範圍內 (0-255)
                    adjusted_color = tuple(
                        max(0, min(255, int(c * life_ratio))) for c in color
                    )

                    # 繪製粒子（用圓形）
                    pygame.draw.circle(
                        screen,
                        adjusted_color,
                        (int(particle["x"]), int(particle_screen_y)),
                        size,
                    )

    def _render_flame_body(self, screen: pygame.Surface, screen_y: float):
        """
        繪製火焰主體\n
        \n
        用漸層色彩繪製火焰的主要形狀\n
        """
        colors = self.base_colors[self.fire_intensity]

        # 從底部到頂部繪製不同強度的火焰層
        flame_layers = 5
        layer_height = self.height / flame_layers

        for i in range(flame_layers):
            layer_y = screen_y + self.height - (i + 1) * layer_height
            layer_alpha = int(255 * (1 - i / flame_layers) * 0.6)  # 上層較透明

            # 創建帶透明度的顏色
            layer_color = colors[min(i, len(colors) - 1)]

            # 計算這一層的寬度（上層較窄）
            width_factor = 1 - (i * 0.1)
            layer_width = self.width * width_factor
            layer_x = self.x + (self.width - layer_width) / 2

            # 繪製火焰層（用橢圓形營造火焰效果）
            if layer_alpha > 20:  # 只繪製可見的層
                flame_rect = pygame.Rect(layer_x, layer_y, layer_width, layer_height)
                pygame.draw.ellipse(screen, layer_color, flame_rect)

    def _render_trigger_effect(self, screen: pygame.Surface, screen_y: float):
        """
        繪製觸發時的特殊效果\n
        \n
        玩家觸發火焰時的強化視覺效果\n
        """
        # 觸發時火焰變得更亮更大
        intensity = self.flash_timer / 20.0

        # 繪製外圍光暈
        for radius in [15, 10, 5]:
            alpha = int(100 * intensity * (15 - radius) / 15)
            if alpha > 0:
                # 這裡簡化處理，用多個橢圓疊加營造光暈效果
                halo_rect = pygame.Rect(
                    self.x - radius,
                    screen_y - radius,
                    self.width + radius * 2,
                    self.height + radius * 2,
                )
                pygame.draw.ellipse(screen, (255, 100, 0), halo_rect, 2)

    def _trigger_effect(self, player) -> dict:
        """
        火焰牆觸發效果\n
        \n
        造成火焰傷害並向上擊退玩家\n
        \n
        參數:\n
        player: 玩家物件\n
        \n
        回傳:\n
        dict: 觸發效果資訊\n
        """
        # 火焰向上的擊退效果
        knockback_x = random.uniform(-1, 1)  # 隨機水平晃動
        knockback_y = -4  # 強烈向上擊退

        # 根據火焰強度調整效果
        intensity_multipliers = {"low": 0.8, "normal": 1.0, "high": 1.3}

        multiplier = intensity_multipliers[self.fire_intensity]
        damage_boost = int(self.damage * (multiplier - 1))

        return {
            "effect_type": "fire_damage",
            "damage_bonus": damage_boost,
            "knockback": (knockback_x, knockback_y * multiplier),
            "sound_effect": "fire_damage",
            "visual_effect": "fire_burst",
            "status_effect": "burning",  # 可以加入燃燒狀態
        }

    def get_knockback(self) -> Tuple[float, float]:
        """
        取得火焰牆的擊退向量\n
        \n
        回傳:\n
        Tuple[float, float]: 擊退向量 (x, y)\n
        """
        return (random.uniform(-1, 1), -4)
