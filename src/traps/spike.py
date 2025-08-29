######################載入套件######################
import pygame
import math
import os
from typing import Tuple
from src.traps.base_trap import BaseTrap


######################尖刺陷阱類別######################
class Spike(BaseTrap):
    """
    尖刺陷阱類別\n
    \n
    最基本的傷害型陷阱，玩家碰到會受到傷害：\n
    1. 靜態陷阱，不會移動\n
    2. 觸碰即造成傷害\n
    3. 有短暫冷卻時間避免連續傷害\n
    4. 視覺上呈現尖銳的刺狀結構\n
    \n
    特性:\n
    - 立即觸發，無預警時間\n
    - 中等傷害，適合作為路障\n
    - 可以放置在地面、牆壁或天花板\n
    - 有輕微的擊退效果\n
    """

    def __init__(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        damage: int = 25,
        spike_type: str = "ground",
    ):
        """
        初始化尖刺陷阱\n
        \n
        參數:\n
        x (float): 尖刺左上角 X 座標\n
        y (float): 尖刺左上角 Y 座標\n
        width (float): 尖刺區域寬度\n
        height (float): 尖刺區域高度\n
        damage (int): 造成的傷害值\n
        spike_type (str): 尖刺類型 ('ground', 'ceiling', 'wall')\n
        """
        # 尖刺的冷卻時間較短，避免玩家卡在上面一直扣血
        super().__init__(x, y, width, height, damage, cooldown=40)

        self.spike_type = spike_type
        self.spike_color = (139, 69, 19)  # 棕色（木刺）
        self.spike_tip_color = (160, 82, 45)  # 淺棕色（尖端）
        self.base_color = (101, 67, 33)  # 深棕色（基座）

        # 根據尖刺類型設定方向
        self.spike_direction = self._get_spike_direction()

        # 計算尖刺的幾何形狀
        self.spike_points = self._calculate_spike_geometry()
        
        # 載入尖刺圖片
        self._load_spike_image()

    def _get_spike_direction(self) -> Tuple[int, int]:
        """
        根據尖刺類型取得尖刺指向\n
        \n
        回傳:\n
        Tuple[int, int]: 方向向量 (x, y)\n
        """
        direction_map = {
            "ground": (0, -1),  # 地面尖刺向上
            "ceiling": (0, 1),  # 天花板尖刺向下
            "wall_left": (1, 0),  # 左牆尖刺向右
            "wall_right": (-1, 0),  # 右牆尖刺向左
        }
        return direction_map.get(self.spike_type, (0, -1))

    def _calculate_spike_geometry(self) -> list:
        """
        計算尖刺的幾何形狀點座標\n
        \n
        根據尖刺類型和尺寸計算三角形尖刺的頂點\n
        \n
        回傳:\n
        list: 包含所有尖刺三角形頂點的清單\n
        """
        spikes = []

        if self.spike_type == "ground":
            # 地面尖刺：底部為基座，向上延伸多個三角形
            spike_count = max(1, int(self.width // 15))  # 每 15 像素一個尖刺
            spike_width = self.width / spike_count

            for i in range(spike_count):
                base_x = self.x + i * spike_width
                # 每個尖刺都是一個三角形
                triangle = [
                    (base_x, self.y + self.height),  # 左下
                    (base_x + spike_width, self.y + self.height),  # 右下
                    (base_x + spike_width / 2, self.y),  # 頂點
                ]
                spikes.append(triangle)

        elif self.spike_type == "ceiling":
            # 天花板尖刺：頂部為基座，向下延伸
            spike_count = max(1, int(self.width // 15))
            spike_width = self.width / spike_count

            for i in range(spike_count):
                base_x = self.x + i * spike_width
                triangle = [
                    (base_x, self.y),  # 左上
                    (base_x + spike_width, self.y),  # 右上
                    (base_x + spike_width / 2, self.y + self.height),  # 頂點
                ]
                spikes.append(triangle)

        return spikes

    def _load_spike_image(self):
        """
        載入尖刺的 tile 圖片\n
        \n
        載入 tile_0068.png 作為尖刺圖片，並根據尖刺區域大小調整\n
        """
        try:
            # 載入尖刺 tile 圖片
            assets_path = "assets/images/"
            self.spike_image = pygame.image.load(os.path.join(assets_path, "tile_0068.png")).convert_alpha()
            
            # 取得原始尺寸
            original_size = self.spike_image.get_size()
            self.tile_size = original_size
            
            # 如果尖刺區域尺寸和圖片不同，需要調整
            # 計算需要多少個 tile 來填滿整個尖刺區域
            tiles_x = max(1, int(self.width / original_size[0]) + (1 if self.width % original_size[0] > 0 else 0))
            tiles_y = max(1, int(self.height / original_size[1]) + (1 if self.height % original_size[1] > 0 else 0))
            
            self.tiles_x = tiles_x
            self.tiles_y = tiles_y
            
        except pygame.error as e:
            print(f"無法載入尖刺圖片: {e}")
            # 如果載入失敗，設定為 None，改用幾何圖形
            self.spike_image = None
            self.tile_size = (32, 32)  # 預設大小
            self.tiles_x = 1
            self.tiles_y = 1

    def update(self):
        """
        更新尖刺狀態\n
        \n
        尖刺是靜態陷阱，主要更新冷卻時間和視覺效果\n
        """
        self._update_base_properties()

        # 尖刺沒有特殊的更新邏輯，只需要基本的狀態管理

    def render(self, screen: pygame.Surface, camera_y: float):
        """
        繪製尖刺陷阱\n
        \n
        繪製尖銳的尖刺，使用 tile_0068.png 圖片\n
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

        # 如果有載入 tile 圖片，使用 tile 繪製
        if self.spike_image:
            self._render_with_tiles(screen, screen_x, screen_y)
        else:
            # 沒有圖片時使用原本的幾何圖形
            self._render_with_geometry(screen, screen_x, screen_y)

        # 如果陷阱處於冷卻狀態，繪製冷卻指示
        if self.trigger_cooldown > 0:
            self._draw_cooldown_indicator(screen, screen_y)

    def _render_with_tiles(self, screen: pygame.Surface, screen_x: int, screen_y: int):
        """
        使用 tile 圖片繪製尖刺\n
        \n
        根據尖刺區域大小重複繪製 tile_0068.png\n
        """
        tile_width, tile_height = self.tile_size
        
        # 根據觸發狀態調整圖片顏色
        spike_image = self.spike_image
        if self.flash_timer > 0:
            # 觸發時變紅色
            intensity = self.flash_timer / 20.0
            red_overlay = pygame.Surface(self.tile_size, pygame.SRCALPHA)
            red_overlay.fill((255, 0, 0, int(100 * intensity)))
            
            spike_image = self.spike_image.copy()
            spike_image.blit(red_overlay, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        
        # 重複繪製 tile 來填滿整個尖刺區域
        for tile_y in range(self.tiles_y):
            for tile_x in range(self.tiles_x):
                draw_x = screen_x + tile_x * tile_width
                draw_y = screen_y + tile_y * tile_height
                
                # 確保不超出尖刺區域邊界
                clip_width = min(tile_width, self.width - tile_x * tile_width)
                clip_height = min(tile_height, self.height - tile_y * tile_height)
                
                if clip_width > 0 and clip_height > 0:
                    # 如果需要裁切，創建裁切後的圖片
                    if clip_width < tile_width or clip_height < tile_height:
                        clipped_tile = pygame.Surface((clip_width, clip_height), pygame.SRCALPHA)
                        clipped_tile.blit(spike_image, (0, 0), (0, 0, clip_width, clip_height))
                        screen.blit(clipped_tile, (draw_x, draw_y))
                    else:
                        screen.blit(spike_image, (draw_x, draw_y))

    def _render_with_geometry(self, screen: pygame.Surface, screen_x: int, screen_y: int):
        """
        使用幾何圖形繪製尖刺（當圖片載入失敗時的備用方案）\n
        \n
        繪製原本的三角形尖刺\n
        """
        # 根據觸發狀態調整顏色
        spike_color = self.spike_color
        tip_color = self.spike_tip_color

        if self.flash_timer > 0:
            # 觸發時閃紅光
            intensity = self.flash_timer / 20.0
            spike_color = (
                min(255, int(self.spike_color[0] + 100 * intensity)),
                max(0, int(self.spike_color[1] - 50 * intensity)),
                max(0, int(self.spike_color[2] - 50 * intensity)),
            )
            tip_color = (255, 0, 0)  # 尖端變成紅色

        # 先繪製基座
        if self.spike_type == "ground":
            base_rect = pygame.Rect(screen_x, screen_y + self.height - 5, self.width, 5)
            pygame.draw.rect(screen, self.base_color, base_rect)
        elif self.spike_type == "ceiling":
            base_rect = pygame.Rect(screen_x, screen_y, self.width, 5)
            pygame.draw.rect(screen, self.base_color, base_rect)

        # 繪製所有尖刺三角形
        for triangle in self.spike_points:
            # 將世界座標轉換為螢幕座標
            screen_triangle = [
                (point[0], point[1] - camera_y + screen.get_height() // 2)
                for point in triangle
            ]

            # 繪製尖刺主體
            pygame.draw.polygon(screen, spike_color, screen_triangle)

            # 繪製尖刺邊框
            pygame.draw.polygon(screen, (0, 0, 0), screen_triangle, 2)

            # 在尖刺頂點繪製高亮，讓尖刺看起來更尖銳
            tip_point = screen_triangle[2]  # 三角形的頂點
            pygame.draw.circle(
                screen, tip_color, (int(tip_point[0]), int(tip_point[1])), 3
            )

    def _draw_cooldown_indicator(self, screen: pygame.Surface, screen_y: float):
        """
        繪製冷卻狀態指示器\n
        \n
        在尖刺上方顯示冷卻進度\n
        """
        cooldown_ratio = self.trigger_cooldown / self.max_cooldown
        indicator_width = int(self.width * 0.8)
        indicator_height = 4
        indicator_x = self.x + (self.width - indicator_width) // 2
        indicator_y = screen_y - 15

        # 背景條
        pygame.draw.rect(
            screen,
            (100, 100, 100),
            (indicator_x, indicator_y, indicator_width, indicator_height),
        )

        # 冷卻進度條
        progress_width = int(indicator_width * (1 - cooldown_ratio))
        if progress_width > 0:
            pygame.draw.rect(
                screen,
                (255, 200, 0),
                (indicator_x, indicator_y, progress_width, indicator_height),
            )

    def _trigger_effect(self, player) -> dict:
        """
        尖刺觸發效果\n
        \n
        造成傷害並提供輕微的擊退效果\n
        \n
        參數:\n
        player: 玩家物件\n
        \n
        回傳:\n
        dict: 觸發效果資訊\n
        """
        # 計算擊退方向（遠離尖刺）
        knockback_x = 0
        knockback_y = 0

        # 根據尖刺類型設定擊退方向
        if self.spike_type == "ground":
            # 地面尖刺向上擊退
            knockback_y = -3
        elif self.spike_type == "ceiling":
            # 天花板尖刺向下擊退
            knockback_y = 3

        # 水平方向的擊退：根據玩家相對位置
        spike_center_x = self.x + self.width / 2
        if player.x < spike_center_x:
            knockback_x = -2  # 向左擊退
        else:
            knockback_x = 2  # 向右擊退

        return {
            "effect_type": "damage_and_knockback",
            "knockback": (knockback_x, knockback_y),
            "sound_effect": "spike_hit",
            "visual_effect": "blood_splash",
        }

    def get_knockback(self) -> Tuple[float, float]:
        """
        取得尖刺的擊退向量\n
        \n
        回傳:\n
        Tuple[float, float]: 擊退向量 (x, y)\n
        """
        # 這個方法在 trigger 時會被覆寫，這裡提供預設值
        return (0, -2)  # 預設向上擊退
