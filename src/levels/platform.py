######################載入套件######################
import pygame
from typing import Tuple
import os


######################平台類別######################
class Platform:
    """
    遊戲平台基礎類別\n
    \n
    代表玩家可以站立的靜態平台，是關卡中最基本的元素：\n
    1. 提供玩家站立和跳躍的基礎\n
    2. 處理碰撞檢測\n
    3. 視覺渲染\n
    \n
    屬性:\n
    x, y (float): 平台左上角位置座標\n
    width, height (float): 平台的寬度和高度\n
    color (Tuple): 平台顏色 RGB 值\n
    platform_type (str): 平台類型（'normal', 'fragile', 'ice' 等）\n
    \n
    平台類型說明:\n
    - normal: 普通平台，堅固可靠\n
    - fragile: 脆弱平台，踩太久會碎裂\n
    - ice: 冰面平台，增加滑動效果\n
    - bounce: 彈跳平台，增加跳躍高度\n
    """

    def __init__(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        platform_type: str = "normal",
    ):
        """
        初始化平台\n
        \n
        建立平台的基本屬性和外觀設定\n
        \n
        參數:\n
        x (float): 平台左上角 X 座標\n
        y (float): 平台左上角 Y 座標\n
        width (float): 平台寬度，範圍通常 50-500\n
        height (float): 平台高度，範圍通常 10-50\n
        platform_type (str): 平台類型，影響顏色和特殊效果\n
        """
        self.x = float(x)
        self.y = float(y)
        self.width = float(width)
        self.height = float(height)
        self.platform_type = platform_type

        # 根據平台類型設定顏色和屬性
        self.color = self._get_platform_color()
        self.border_color = (0, 0, 0)  # 黑色邊框

        # 特殊平台的額外屬性
        self.durability = self._get_platform_durability()  # 耐久度
        self.friction = self._get_platform_friction()  # 摩擦係數
        self.bounce_power = self._get_bounce_power()  # 彈跳力度

        # 狀態屬性
        self.is_active = True
        self.damage_level = 0  # 損壞程度（0-100）

        # 載入平台圖片
        self._load_platform_images()

    def _get_platform_color(self) -> Tuple[int, int, int]:
        """
        根據平台類型取得對應顏色\n
        \n
        回傳:\n
        Tuple[int, int, int]: RGB 顏色值\n
        """
        color_map = {
            "normal": (139, 69, 19),  # 棕色（木頭）
            "fragile": (160, 82, 45),  # 淺棕色（舊木頭）
            "ice": (173, 216, 230),  # 淺藍色（冰塊）
            "bounce": (50, 205, 50),  # 綠色（彈性材質）
            "metal": (105, 105, 105),  # 灰色（金屬）
            "stone": (128, 128, 128),  # 深灰色（石頭）
        }
        return color_map.get(self.platform_type, (139, 69, 19))

    def _get_platform_durability(self) -> int:
        """
        根據平台類型取得耐久度\n
        \n
        回傳:\n
        int: 耐久度數值，-1 表示無法破壞\n
        """
        durability_map = {
            "normal": -1,  # 普通平台不會破壞
            "fragile": 100,  # 脆弱平台有限耐久度
            "ice": -1,  # 冰面不會破壞但會滑
            "bounce": -1,  # 彈跳平台很堅固
            "metal": -1,  # 金屬平台非常堅固
            "stone": -1,  # 石頭平台很堅固
        }
        return durability_map.get(self.platform_type, -1)

    def _get_platform_friction(self) -> float:
        """
        根據平台類型取得摩擦係數\n
        \n
        回傳:\n
        float: 摩擦係數，1.0 為標準，越小越滑\n
        """
        friction_map = {
            "normal": 1.0,  # 標準摩擦
            "fragile": 1.0,  # 標準摩擦
            "ice": 0.3,  # 很滑
            "bounce": 1.2,  # 較高摩擦
            "metal": 0.8,  # 稍滑
            "stone": 1.1,  # 較粗糙
        }
        return friction_map.get(self.platform_type, 1.0)

    def _get_bounce_power(self) -> float:
        """
        根據平台類型取得彈跳力度\n
        \n
        回傳:\n
        float: 彈跳力倍數，1.0 為無額外彈跳\n
        """
        bounce_map = {
            "normal": 1.0,  # 無特殊彈跳
            "fragile": 1.0,  # 無特殊彈跳
            "ice": 1.0,  # 無特殊彈跳
            "bounce": 1.5,  # 50% 額外彈跳力
            "metal": 1.0,  # 無特殊彈跳
            "stone": 1.0,  # 無特殊彈跳
        }
        return bounce_map.get(self.platform_type, 1.0)

    def _load_platform_images(self):
        """
        載入平台的 tile 圖片\n
        \n
        載入左中右三個部分的 tile 圖片，用於拼接不同大小的平台\n
        """
        try:
            # 載入平台的左中右 tile 圖片
            assets_path = "assets/images/"
            self.tile_left = pygame.image.load(os.path.join(assets_path, "tile_0103.png")).convert_alpha()
            self.tile_middle = pygame.image.load(os.path.join(assets_path, "tile_0104.png")).convert_alpha()
            self.tile_right = pygame.image.load(os.path.join(assets_path, "tile_0106.png")).convert_alpha()
            
            # 取得 tile 的原始尺寸
            self.tile_size = self.tile_left.get_size()
            
            # 根據平台高度調整 tile 大小
            if self.height != self.tile_size[1]:
                scale_ratio = self.height / self.tile_size[1]
                new_width = int(self.tile_size[0] * scale_ratio)
                new_height = int(self.height)
                
                self.tile_left = pygame.transform.scale(self.tile_left, (new_width, new_height))
                self.tile_middle = pygame.transform.scale(self.tile_middle, (new_width, new_height))
                self.tile_right = pygame.transform.scale(self.tile_right, (new_width, new_height))
                
                # 更新 tile 尺寸
                self.tile_size = (new_width, new_height)
            
        except pygame.error as e:
            print(f"無法載入平台圖片: {e}")
            # 如果載入失敗，設定為 None，改用幾何圖形
            self.tile_left = None
            self.tile_middle = None
            self.tile_right = None
            self.tile_size = (32, 32)  # 預設大小

    def get_collision_rect(self) -> pygame.Rect:
        """
        取得平台的碰撞矩形\n
        \n
        回傳平台的精確碰撞範圍，用於物理引擎\n
        \n
        回傳:\n
        pygame.Rect: 碰撞檢測用的矩形\n
        """
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def check_player_interaction(self, player) -> dict:
        """
        檢查玩家與平台的互動\n
        \n
        處理特殊平台的效果（滑動、彈跳、損壞等）\n
        \n
        參數:\n
        player: 玩家物件\n
        \n
        回傳:\n
        dict: 互動結果，包含特殊效果資訊\n
        """
        interaction_result = {
            "friction_modifier": self.friction,
            "bounce_modifier": self.bounce_power,
            "platform_damaged": False,
            "platform_destroyed": False,
        }

        # 處理脆弱平台的損壞
        if self.platform_type == "fragile" and self.durability > 0:
            self.damage_level += 1  # 每次踩踏增加損壞

            if self.damage_level >= self.durability:
                # 平台完全損壞
                self.is_active = False
                interaction_result["platform_destroyed"] = True
            elif self.damage_level >= self.durability * 0.7:
                # 平台開始裂開（視覺效果）
                interaction_result["platform_damaged"] = True

        return interaction_result

    def repair(self):
        """
        修復平台\n
        \n
        恢復平台到完好狀態，通常在關卡重置時使用\n
        """
        self.is_active = True
        self.damage_level = 0

    def render(self, screen: pygame.Surface, camera_y: float):
        """
        繪製平台\n
        \n
        在螢幕上繪製平台，使用 tile 圖片拼接成所需大小\n
        \n
        參數:\n
        screen (pygame.Surface): 要繪製到的螢幕表面\n
        camera_y (float): 攝影機 Y 軸偏移\n
        """
        if not self.is_active:
            return  # 被破壞的平台不繪製

        # 計算在螢幕上的位置（考慮攝影機偏移）
        screen_x = int(self.x)
        screen_y = int(self.y - camera_y + screen.get_height() // 2)

        # 只繪製在螢幕可見範圍內的平台
        if (
            screen_y + self.height < 0
            or screen_y > screen.get_height()
            or screen_x + self.width < 0
            or screen_x > screen.get_width()
        ):
            return

        # 如果有載入 tile 圖片，使用 tile 繪製
        if self.tile_left and self.tile_middle and self.tile_right:
            self._render_with_tiles(screen, screen_x, screen_y)
        else:
            # 沒有圖片時使用原本的幾何圖形
            self._render_with_geometry(screen, screen_x, screen_y)

        # 繪製特殊效果
        self._draw_special_effects(screen, screen_x, screen_y)

    def _render_with_tiles(self, screen: pygame.Surface, screen_x: int, screen_y: int):
        """
        使用 tile 圖片繪製平台\n
        \n
        根據平台寬度拼接左中右 tile 圖片\n
        """
        tile_width = self.tile_size[0]
        
        # 計算需要多少個中間 tile
        remaining_width = self.width - (tile_width * 2)  # 扣除左右兩個 tile
        middle_tiles_count = max(0, int(remaining_width / tile_width))
        
        current_x = screen_x
        
        # 繪製左側 tile
        screen.blit(self.tile_left, (current_x, screen_y))
        current_x += tile_width
        
        # 繪製中間 tile（重複拼接）
        for i in range(middle_tiles_count):
            screen.blit(self.tile_middle, (current_x, screen_y))
            current_x += tile_width
        
        # 如果還有剩餘空間，繪製部分中間 tile
        remaining_space = self.width - (current_x - screen_x) - tile_width
        if remaining_space > 0:
            # 裁切中間 tile 來填補剩餘空間
            partial_tile = pygame.Surface((int(remaining_space), self.tile_size[1]), pygame.SRCALPHA)
            partial_tile.blit(self.tile_middle, (0, 0), (0, 0, int(remaining_space), self.tile_size[1]))
            screen.blit(partial_tile, (current_x, screen_y))
            current_x += remaining_space
        
        # 繪製右側 tile
        if current_x < screen_x + self.width:
            screen.blit(self.tile_right, (screen_x + self.width - tile_width, screen_y))

    def _render_with_geometry(self, screen: pygame.Surface, screen_x: int, screen_y: int):
        """
        使用幾何圖形繪製平台（當圖片載入失敗時的備用方案）\n
        \n
        繪製簡單的矩形平台，改用地面色彩 tile_0000 的風格\n
        """
        # 根據損壞程度調整顏色
        # 使用類似 tile_0000 的地面色彩（土褐色）
        base_color = (101, 67, 33)  # 深褐色（土地色）
        render_color = base_color
        
        if self.platform_type == "fragile" and self.damage_level > 0:
            # 損壞的平台顏色變暗
            damage_ratio = self.damage_level / self.durability
            render_color = tuple(int(c * (1 - damage_ratio * 0.5)) for c in base_color)

        # 繪製平台主體（土地紋理效果）
        platform_rect = pygame.Rect(screen_x, screen_y, self.width, self.height)
        pygame.draw.rect(screen, render_color, platform_rect)

        # 繪製平台邊框
        pygame.draw.rect(screen, (139, 69, 19), platform_rect, 2)

        # 繪製土地紋理線條
        for i in range(0, int(self.width), 8):
            pygame.draw.line(
                screen,
                (139, 69, 19),  # 稍亮的土色
                (screen_x + i, screen_y + 2),
                (screen_x + i, screen_y + self.height - 2),
                1,
            )

    def _draw_special_effects(
        self, screen: pygame.Surface, screen_x: int, screen_y: int
    ):
        """
        繪製平台的特殊視覺效果\n
        \n
        根據平台類型繪製對應的特效\n
        \n
        參數:\n
        screen (pygame.Surface): 螢幕表面\n
        screen_x (int): 平台在螢幕上的 X 座標\n
        screen_y (int): 平台在螢幕上的 Y 座標\n
        """
        if self.platform_type == "ice":
            # 冰面平台：繪製閃亮效果
            highlight_color = (255, 255, 255, 150)
            for i in range(0, int(self.width), 20):
                pygame.draw.circle(
                    screen, (200, 255, 255), (screen_x + i + 10, screen_y + 5), 3
                )

        elif self.platform_type == "bounce":
            # 彈跳平台：繪製彈簧紋理
            spring_color = (0, 150, 0)
            for i in range(5, int(self.width), 15):
                pygame.draw.line(
                    screen,
                    spring_color,
                    (screen_x + i, screen_y + 2),
                    (screen_x + i, screen_y + self.height - 2),
                    2,
                )

        elif (
            self.platform_type == "fragile"
            and self.damage_level > self.durability * 0.5
        ):
            # 受損的脆弱平台：繪製裂痕
            crack_color = (139, 69, 19)  # 深棕色
            crack_positions = [
                (self.width * 0.3, 2),
                (self.width * 0.7, self.height - 2),
            ]

            for crack_x, crack_y in crack_positions:
                start_pos = (screen_x + int(crack_x), screen_y + int(crack_y))
                end_pos = (screen_x + int(crack_x) + 10, screen_y + int(crack_y) + 8)
                pygame.draw.line(screen, crack_color, start_pos, end_pos, 2)

        elif self.platform_type == "metal":
            # 金屬平台：繪製金屬質感
            for i in range(0, int(self.height), 5):
                highlight_y = screen_y + i
                pygame.draw.line(
                    screen,
                    (150, 150, 150),
                    (screen_x, highlight_y),
                    (screen_x + self.width, highlight_y),
                    1,
                )

    def get_surface_properties(self) -> dict:
        """
        取得平台表面屬性\n
        \n
        回傳平台的物理屬性，供物理引擎使用\n
        \n
        回傳:\n
        dict: 包含摩擦、彈性等物理屬性\n
        """
        return {
            "friction": self.friction,
            "bounce": self.bounce_power,
            "type": self.platform_type,
            "is_active": self.is_active,
            "durability_ratio": (
                (self.durability - self.damage_level) / self.durability
                if self.durability > 0
                else 1.0
            ),
        }
