######################載入套件######################
import pygame
from typing import Tuple, Optional
from abc import ABC, abstractmethod


######################陷阱基礎抽象類別######################
class BaseTrap(ABC):
    """
    所有陷阱的基礎抽象類別\n
    \n
    定義陷阱的共通介面和基本行為：\n
    1. 陷阱的基本屬性（位置、大小、傷害）\n
    2. 狀態管理（啟用、觸發、冷卻）\n
    3. 抽象方法強制子類別實作特定行為\n
    \n
    屬性:\n
    x, y (float): 陷阱位置座標\n
    width, height (float): 陷阱碰撞範圍\n
    damage (int): 陷阱造成的傷害\n
    is_active (bool): 陷阱是否啟用\n
    trigger_cooldown (int): 觸發後的冷卻時間\n
    \n
    子類別需要實作:\n
    - update(): 每幀更新陷阱狀態\n
    - render(): 繪製陷阱視覺效果\n
    - _trigger_effect(): 陷阱被觸發時的特殊效果\n
    """

    def __init__(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        damage: int = 20,
        cooldown: int = 60,
    ):
        """
        初始化基礎陷阱\n
        \n
        設定陷阱的基本屬性和狀態\n
        \n
        參數:\n
        x (float): 陷阱左上角 X 座標\n
        y (float): 陷阱左上角 Y 座標\n
        width (float): 陷阱碰撞範圍寬度\n
        height (float): 陷阱碰撞範圍高度\n
        damage (int): 陷阱造成的傷害值\n
        cooldown (int): 觸發後的冷卻幀數\n
        """
        self.x = float(x)
        self.y = float(y)
        self.width = float(width)
        self.height = float(height)
        self.damage = damage

        # 狀態管理
        self.is_active = True
        self.is_triggered = False
        self.trigger_cooldown = 0
        self.max_cooldown = cooldown

        # 視覺效果相關
        self.animation_frame = 0
        self.flash_timer = 0  # 用於閃爍效果

    @abstractmethod
    def update(self):
        """
        更新陷阱狀態（抽象方法）\n
        \n
        子類別必須實作此方法，用於：\n
        - 更新動畫效果\n
        - 處理觸發邏輯\n
        - 管理冷卻時間\n
        """
        pass

    @abstractmethod
    def render(self, screen: pygame.Surface, camera_y: float):
        """
        繪製陷阱（抽象方法）\n
        \n
        子類別必須實作此方法，用於繪製陷阱的視覺效果\n
        \n
        參數:\n
        screen (pygame.Surface): 要繪製到的螢幕表面\n
        camera_y (float): 攝影機 Y 軸偏移\n
        """
        pass

    @abstractmethod
    def _trigger_effect(self, player) -> dict:
        """
        陷阱觸發效果（抽象方法）\n
        \n
        子類別必須實作此方法，定義陷阱被觸發時的特殊效果\n
        \n
        參數:\n
        player: 觸發陷阱的玩家物件\n
        \n
        回傳:\n
        dict: 觸發效果的詳細資訊\n
        """
        pass

    def get_collision_rect(self) -> pygame.Rect:
        """
        取得陷阱的碰撞矩形\n
        \n
        回傳:\n
        pygame.Rect: 用於碰撞檢測的矩形\n
        """
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def check_player_collision(self, player) -> bool:
        """
        檢查玩家是否碰到陷阱\n
        \n
        參數:\n
        player: 玩家物件\n
        \n
        回傳:\n
        bool: 是否發生碰撞\n
        """
        if not self.is_active or self.trigger_cooldown > 0:
            return False

        player_rect = player.get_collision_rect()
        trap_rect = self.get_collision_rect()
        return player_rect.colliderect(trap_rect)

    def trigger(self, player) -> dict:
        """
        觸發陷阱\n
        \n
        當玩家碰觸陷阱時呼叫此方法\n
        \n
        參數:\n
        player: 觸發陷阱的玩家\n
        \n
        回傳:\n
        dict: 觸發結果和效果資訊\n
        """
        if not self.is_active or self.trigger_cooldown > 0:
            return {"triggered": False}

        # 設定觸發狀態
        self.is_triggered = True
        self.trigger_cooldown = self.max_cooldown
        self.flash_timer = 20  # 觸發時閃爍 20 幀

        # 執行特殊效果
        effect_result = self._trigger_effect(player)
        effect_result["triggered"] = True
        effect_result["damage"] = self.damage

        return effect_result

    def reset(self):
        """
        重置陷阱狀態\n
        \n
        將陷阱恢復到初始狀態，用於關卡重置\n
        """
        self.is_active = True
        self.is_triggered = False
        self.trigger_cooldown = 0
        self.animation_frame = 0
        self.flash_timer = 0

    def get_damage(self) -> int:
        """
        取得陷阱傷害值\n
        \n
        回傳:\n
        int: 陷阱造成的傷害\n
        """
        return self.damage

    def get_knockback(self) -> Optional[Tuple[float, float]]:
        """
        取得陷阱的擊退效果\n
        \n
        基礎陷阱沒有擊退效果，子類別可以覆寫此方法\n
        \n
        回傳:\n
        Optional[Tuple[float, float]]: 擊退向量 (x, y)，None 表示無擊退\n
        """
        return None

    def is_in_screen_bounds(self, screen: pygame.Surface, camera_y: float) -> bool:
        """
        檢查陷阱是否在螢幕可見範圍內\n
        \n
        用於優化渲染效能，只繪製可見的陷阱\n
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

    def _update_base_properties(self):
        """
        更新基礎屬性\n
        \n
        處理所有陷阱共通的狀態更新（冷卻時間、動畫等）\n
        """
        # 更新冷卻時間
        if self.trigger_cooldown > 0:
            self.trigger_cooldown -= 1

        # 更新閃爍計時器
        if self.flash_timer > 0:
            self.flash_timer -= 1

        # 更新動畫幀
        self.animation_frame += 1
        if self.animation_frame >= 1000:  # 防止數值過大
            self.animation_frame = 0

        # 重置觸發狀態
        if self.trigger_cooldown == 0:
            self.is_triggered = False
