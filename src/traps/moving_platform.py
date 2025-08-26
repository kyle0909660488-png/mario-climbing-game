######################載入套件######################
import pygame
import math
from typing import Tuple, Optional
from src.traps.base_trap import BaseTrap


######################移動平台類別######################
class MovingPlatform(BaseTrap):
    """
    移動平台類別\n
    \n
    特殊的平台型陷阱，具有以下特性：\n
    1. 在固定路徑上週期性移動\n
    2. 玩家可以站在上面跟隨移動\n
    3. 如果玩家沒跟上會掉落\n
    4. 可以水平或垂直移動\n
    5. 移動到邊界時會反轉方向\n
    \n
    特性:\n
    - 不會直接造成傷害\n
    - 需要時機掌握來安全通過\n
    - 可以作為必經路線或捷徑\n
    - 增加關卡的動態挑戰性\n
    """

    def __init__(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        end_x: float,
        end_y: float,
        speed: float = 2.0,
        is_vertical: bool = False,
    ):
        """
        初始化移動平台\n
        \n
        參數:\n
        x (float): 平台起始 X 座標\n
        y (float): 平台起始 Y 座標\n
        width (float): 平台寬度\n
        height (float): 平台高度\n
        end_x (float): 移動終點 X 座標\n
        end_y (float): 移動終點 Y 座標\n
        speed (float): 移動速度（像素/幀）\n
        is_vertical (bool): 是否為垂直移動\n
        """
        # 移動平台不造成傷害，但有互動效果
        super().__init__(x, y, width, height, damage=0, cooldown=0)

        # 移動路徑設定
        self.start_x = float(x)
        self.start_y = float(y)
        self.end_x = float(end_x)
        self.end_y = float(end_y)
        self.speed = speed
        self.is_vertical = is_vertical

        # 當前移動狀態
        self.current_x = self.start_x
        self.current_y = self.start_y
        self.velocity_x = 0.0
        self.velocity_y = 0.0
        self.is_moving_to_end = True  # True: 移向終點，False: 移向起點

        # 計算移動距離和方向
        self.total_distance = math.sqrt(
            (self.end_x - self.start_x) ** 2 + (self.end_y - self.start_y) ** 2
        )

        if self.total_distance > 0:
            # 正規化方向向量
            self.direction_x = (self.end_x - self.start_x) / self.total_distance
            self.direction_y = (self.end_y - self.start_y) / self.total_distance
        else:
            # 如果起點終點相同，就不移動
            self.direction_x = 0
            self.direction_y = 0

        # 平台外觀設定
        self.platform_color = (100, 150, 200)  # 藍灰色
        self.moving_color = (80, 120, 180)  # 深一點的藍色（移動時）
        self.border_color = (50, 75, 100)  # 深邊框

        # 載重檢測（站在平台上的物件）
        self.passengers = []

        # 更新初始速度
        self._update_velocity()

    def _update_velocity(self):
        """
        更新移動速度\n
        \n
        根據目標方向計算當前幀的移動向量\n
        """
        if self.total_distance == 0:
            self.velocity_x = 0
            self.velocity_y = 0
            return

        if self.is_moving_to_end:
            self.velocity_x = self.direction_x * self.speed
            self.velocity_y = self.direction_y * self.speed
        else:
            self.velocity_x = -self.direction_x * self.speed
            self.velocity_y = -self.direction_y * self.speed

    def update(self):
        """
        更新移動平台狀態\n
        \n
        處理平台移動、邊界檢查和方向切換\n
        """
        self._update_base_properties()

        # 更新位置
        self.current_x += self.velocity_x
        self.current_y += self.velocity_y

        # 更新基礎類別的座標（用於碰撞檢測）
        self.x = self.current_x
        self.y = self.current_y

        # 檢查是否到達邊界
        self._check_boundary_collision()

        # 更新載客清單
        self._update_passengers()

    def _check_boundary_collision(self):
        """
        檢查邊界碰撞並切換移動方向\n
        \n
        當平台到達移動路徑的兩端時，反轉移動方向\n
        """
        if self.total_distance == 0:
            return

        # 計算當前位置到起點的距離
        distance_from_start = math.sqrt(
            (self.current_x - self.start_x) ** 2 + (self.current_y - self.start_y) ** 2
        )

        # 檢查是否超出移動範圍
        if self.is_moving_to_end:
            if distance_from_start >= self.total_distance:
                # 到達終點，切換方向
                self.current_x = self.end_x
                self.current_y = self.end_y
                self.is_moving_to_end = False
                self._update_velocity()
        else:
            if distance_from_start <= 0.5:  # 允許小誤差
                # 回到起點，切換方向
                self.current_x = self.start_x
                self.current_y = self.start_y
                self.is_moving_to_end = True
                self._update_velocity()

    def _update_passengers(self):
        """
        更新站在平台上的乘客\n
        \n
        檢查哪些物件還站在平台上，移除已經離開的物件\n
        """
        # 這裡簡化處理，實際遊戲中可能需要更複雜的載客系統
        self.passengers = []

    def check_player_standing(self, player) -> bool:
        """
        檢查玩家是否站在平台上\n
        \n
        用於判斷玩家是否應該跟隨平台移動\n
        \n
        參數:\n
        player: 玩家物件\n
        \n
        回傳:\n
        bool: 玩家是否站在平台上\n
        """
        player_rect = player.get_collision_rect()
        platform_rect = self.get_collision_rect()

        # 檢查玩家是否在平台上方且接觸平台頂部
        is_above = player_rect.bottom <= platform_rect.top + 5  # 允許小誤差
        is_horizontally_aligned = (
            player_rect.right > platform_rect.left
            and player_rect.left < platform_rect.right
        )

        return is_above and is_horizontally_aligned and player.velocity_y >= 0

    def move_passenger(self, passenger):
        """
        移動乘客（玩家或其他物件）\n
        \n
        讓站在平台上的物件跟隨平台移動\n
        \n
        參數:\n
        passenger: 需要移動的乘客物件\n
        """
        passenger.x += self.velocity_x
        passenger.y += self.velocity_y

        # 如果乘客有速度屬性，也要更新
        if hasattr(passenger, "velocity_x"):
            passenger.velocity_x += self.velocity_x * 0.1  # 給一點平台的慣性

    def render(self, screen: pygame.Surface, camera_y: float):
        """
        繪製移動平台\n
        \n
        繪製平台本體和移動指示器\n
        \n
        參數:\n
        screen (pygame.Surface): 螢幕表面\n
        camera_y (float): 攝影機偏移\n
        """
        if not self.is_in_screen_bounds(screen, camera_y):
            return

        # 計算螢幕座標
        screen_x = int(self.current_x)
        screen_y = int(self.current_y - camera_y + screen.get_height() // 2)

        # 選擇顏色（移動時顏色略有不同）
        is_moving = self.velocity_x != 0 or self.velocity_y != 0
        color = self.moving_color if is_moving else self.platform_color

        # 繪製平台主體
        platform_rect = pygame.Rect(screen_x, screen_y, self.width, self.height)
        pygame.draw.rect(screen, color, platform_rect)

        # 繪製邊框
        pygame.draw.rect(screen, self.border_color, platform_rect, 3)

        # 繪製移動方向指示器
        self._draw_direction_indicator(screen, screen_x, screen_y)

        # 繪製移動路徑（半透明線條）
        self._draw_movement_path(screen, camera_y)

    def _draw_direction_indicator(
        self, screen: pygame.Surface, screen_x: int, screen_y: int
    ):
        """
        繪製移動方向指示器\n
        \n
        用箭頭顯示平台的移動方向\n
        """
        if self.velocity_x == 0 and self.velocity_y == 0:
            return  # 不移動就不畫箭頭

        # 計算箭頭位置（平台中心）
        arrow_x = screen_x + self.width // 2
        arrow_y = screen_y + self.height // 2

        # 計算箭頭方向
        arrow_length = 15
        end_x = arrow_x + self.velocity_x * arrow_length / self.speed
        end_y = arrow_y + self.velocity_y * arrow_length / self.speed

        # 繪製箭頭主線
        pygame.draw.line(
            screen, (255, 255, 255), (arrow_x, arrow_y), (int(end_x), int(end_y)), 3
        )

        # 繪製箭頭頭部
        if self.velocity_x != 0 or self.velocity_y != 0:
            # 計算箭頭兩翼的點
            angle = math.atan2(self.velocity_y, self.velocity_x)
            wing_length = 8

            wing1_x = end_x - wing_length * math.cos(angle - 0.5)
            wing1_y = end_y - wing_length * math.sin(angle - 0.5)
            wing2_x = end_x - wing_length * math.cos(angle + 0.5)
            wing2_y = end_y - wing_length * math.sin(angle + 0.5)

            pygame.draw.line(
                screen,
                (255, 255, 255),
                (int(end_x), int(end_y)),
                (int(wing1_x), int(wing1_y)),
                2,
            )
            pygame.draw.line(
                screen,
                (255, 255, 255),
                (int(end_x), int(end_y)),
                (int(wing2_x), int(wing2_y)),
                2,
            )

    def _draw_movement_path(self, screen: pygame.Surface, camera_y: float):
        """
        繪製移動路徑\n
        \n
        用半透明線條顯示平台的移動軌跡\n
        """
        if self.total_distance == 0:
            return

        # 轉換起點終點到螢幕座標
        start_screen_x = int(self.start_x)
        start_screen_y = int(self.start_y - camera_y + screen.get_height() // 2)
        end_screen_x = int(self.end_x)
        end_screen_y = int(self.end_y - camera_y + screen.get_height() // 2)

        # 繪製路徑線（虛線效果）
        path_color = (200, 200, 200, 100)  # 半透明灰色

        # 計算線段數量來創造虛線效果
        segment_length = 10
        total_length = math.sqrt(
            (end_screen_x - start_screen_x) ** 2 + (end_screen_y - start_screen_y) ** 2
        )

        if total_length > 0:
            segments = int(total_length / segment_length)
            for i in range(0, segments, 2):  # 每隔一個線段繪製
                t1 = i / segments
                t2 = min((i + 1) / segments, 1.0)

                x1 = int(start_screen_x + t1 * (end_screen_x - start_screen_x))
                y1 = int(start_screen_y + t1 * (end_screen_y - start_screen_y))
                x2 = int(start_screen_x + t2 * (end_screen_x - start_screen_x))
                y2 = int(start_screen_y + t2 * (end_screen_y - start_screen_y))

                pygame.draw.line(screen, (150, 150, 150), (x1, y1), (x2, y2), 2)

    def _trigger_effect(self, player) -> dict:
        """
        移動平台觸發效果\n
        \n
        移動平台不造成傷害，但會影響玩家移動\n
        \n
        參數:\n
        player: 玩家物件\n
        \n
        回傳:\n
        dict: 互動效果資訊\n
        """
        return {
            "effect_type": "platform_interaction",
            "platform_velocity": (self.velocity_x, self.velocity_y),
            "is_safe": True,
            "sound_effect": "platform_step",
        }

    def get_platform_velocity(self) -> Tuple[float, float]:
        """
        取得平台移動速度\n
        \n
        用於物理引擎計算玩家跟隨移動\n
        \n
        回傳:\n
        Tuple[float, float]: 移動速度向量 (x, y)\n
        """
        return (self.velocity_x, self.velocity_y)
