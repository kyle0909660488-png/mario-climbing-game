######################載入套件######################
import pygame
import random
import math


######################藥水物品基礎類別######################
class Potion:
    """
    藥水物品基礎類別\n
    \n
    代表地面上可撿拾的藥水物品：\n
    1. 三種藥水類型的視覺呈現\n
    2. 撿拾範圍和動畫效果\n
    3. 藥水效果說明\n
    4. 自動消失機制\n
    \n
    屬性:\n
    x, y (int): 物品位置座標\n
    potion_type (str): 藥水類型名稱\n
    effect_value (int): 效果數值\n
    lifetime (int): 存在時間計數器\n
    """

    def __init__(self, x: int, y: int, potion_type: str):
        """
        初始化藥水物品\n
        \n
        參數:\n
        x (int): 生成位置 x 座標\n
        y (int): 生成位置 y 座標\n
        potion_type (str): 藥水類型 ('healing', 'shield', 'attack')\n
        """
        self.x = x
        self.y = y
        self.potion_type = potion_type

        # 物品尺寸
        self.width = 20
        self.height = 30

        # 存在時間（15秒後消失）
        self.lifetime = 900
        self.max_lifetime = 900

        # 動畫效果
        self.float_offset = 0
        self.glow_intensity = 0
        self.pulse_timer = 0

        # 撿拾範圍
        self.pickup_range = 30

        # 藥水配置
        self.potion_configs = {
            "healing": {
                "name": "治療藥水",
                "color": (255, 50, 50),  # 紅色
                "glow": (255, 100, 100),
                "effect_value": 60,
                "description": "回復 60 點血量",
            },
            "shield": {
                "name": "護盾藥水",
                "color": (50, 150, 255),  # 藍色
                "glow": (100, 200, 255),
                "effect_value": 50,
                "description": "獲得 50 點護盾",
            },
            "attack": {
                "name": "攻擊藥水",
                "color": (255, 200, 50),  # 金色
                "glow": (255, 255, 100),
                "effect_value": 50,  # 50% 攻擊力加成
                "description": "攻擊力提升 50%，持續 15 秒",
            },
        }

        # 獲取當前藥水的配置
        self.config = self.potion_configs.get(
            potion_type, self.potion_configs["healing"]
        )

    def update(self):
        """
        更新藥水物品狀態\n
        \n
        處理動畫效果和存在時間倒數\n
        """
        # 減少存在時間
        self.lifetime -= 1

        # 更新浮動動畫（上下漂浮）
        self.float_offset = math.sin(pygame.time.get_ticks() * 0.004) * 4

        # 更新光暈效果（閃爍）
        self.pulse_timer += 1
        self.glow_intensity = abs(math.sin(self.pulse_timer * 0.08)) * 60

    def draw(self, screen, camera_x=0, camera_y=0):
        """
        繪製藥水物品\n
        \n
        包含藥水顏色、光暈效果和動畫效果\n
        \n
        參數:\n
        screen: pygame 畫面物件\n
        camera_x (int): 攝影機 x 偏移\n
        camera_y (int): 攝影機 y 偏移\n
        """
        # 計算螢幕位置
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y + self.float_offset

        # 檢查是否在螢幕範圍內
        if (
            screen_x < -50
            or screen_x > screen.get_width() + 50
            or screen_y < -50
            or screen_y > screen.get_height() + 50
        ):
            return

        # 繪製光暈效果
        if self.glow_intensity > 0:
            glow_color = self.config["glow"]
            glow_alpha = int(self.glow_intensity)

            # 創建光暈表面
            glow_size = self.width + 25
            glow_surface = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)

            # 繪製漸變光暈
            for i in range(4):
                radius = (glow_size // 2) - i * 4
                alpha = glow_alpha // (i + 1)
                if radius > 0:
                    color_with_alpha = (*glow_color, alpha)
                    pygame.draw.circle(
                        glow_surface,
                        color_with_alpha,
                        (glow_size // 2, glow_size // 2),
                        radius,
                    )

            screen.blit(glow_surface, (screen_x - 12, screen_y - 12))

        # 繪製藥水瓶身（橢圓形主體）
        main_color = self.config["color"]
        bottle_rect = pygame.Rect(
            screen_x + 2, screen_y + 8, self.width - 4, self.height - 12
        )
        pygame.draw.ellipse(screen, main_color, bottle_rect)

        # 繪製瓶身高光
        highlight_rect = pygame.Rect(
            screen_x + 4, screen_y + 10, (self.width - 4) // 3, (self.height - 12) // 2
        )
        highlight_color = tuple(min(255, c + 80) for c in main_color)
        pygame.draw.ellipse(screen, highlight_color, highlight_rect)

        # 繪製瓶蓋（深灰色矩形）
        cap_rect = pygame.Rect(screen_x + 6, screen_y, self.width - 12, 8)
        pygame.draw.rect(screen, (80, 80, 80), cap_rect)
        pygame.draw.rect(
            screen, (120, 120, 120), (screen_x + 7, screen_y + 1, self.width - 14, 6)
        )

        # 繪製瓶身輪廓
        pygame.draw.ellipse(screen, (40, 40, 40), bottle_rect, 2)

        # 繪製藥水類型標誌
        self._draw_potion_symbol(screen, screen_x, screen_y)

        # 繪製存在時間警告（最後3秒）
        if self.lifetime < 180:
            alpha = int(abs(math.sin(self.lifetime * 0.15)) * 200)
            warning_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            warning_surface.fill((255, 255, 255, alpha))
            screen.blit(warning_surface, (screen_x, screen_y))

    def _draw_potion_symbol(self, screen, x, y):
        """
        繪製藥水類型專屬符號\n
        \n
        用簡單圖形表示不同藥水類型的效果\n
        \n
        參數:\n
        screen: pygame 畫面物件\n
        x, y (int): 繪製位置\n
        """
        center_x = x + self.width // 2
        center_y = y + self.height // 2

        if self.potion_type == "healing":
            # 治療：紅十字
            pygame.draw.line(
                screen,
                (255, 255, 255),
                (center_x - 4, center_y),
                (center_x + 4, center_y),
                3,
            )
            pygame.draw.line(
                screen,
                (255, 255, 255),
                (center_x, center_y - 4),
                (center_x, center_y + 4),
                3,
            )

        elif self.potion_type == "shield":
            # 護盾：盾牌形狀
            shield_points = [
                (center_x, center_y - 6),
                (center_x - 4, center_y - 2),
                (center_x - 4, center_y + 2),
                (center_x, center_y + 6),
                (center_x + 4, center_y + 2),
                (center_x + 4, center_y - 2),
            ]
            pygame.draw.polygon(screen, (255, 255, 255), shield_points)
            pygame.draw.polygon(screen, (150, 150, 255), shield_points, 2)

        elif self.potion_type == "attack":
            # 攻擊：向上箭頭
            arrow_points = [
                (center_x, center_y - 6),
                (center_x - 3, center_y - 2),
                (center_x - 1, center_y - 2),
                (center_x - 1, center_y + 4),
                (center_x + 1, center_y + 4),
                (center_x + 1, center_y - 2),
                (center_x + 3, center_y - 2),
            ]
            pygame.draw.polygon(screen, (255, 255, 255), arrow_points)

    def is_expired(self) -> bool:
        """
        檢查物品是否已過期\n
        \n
        回傳:\n
        bool: 物品是否應該被移除\n
        """
        return self.lifetime <= 0

    def can_pickup(self, player_x: int, player_y: int) -> bool:
        """
        檢查玩家是否可以撿拾此物品\n
        \n
        參數:\n
        player_x (int): 玩家 x 座標\n
        player_y (int): 玩家 y 座標\n
        \n
        回傳:\n
        bool: 是否在撿拾範圍內\n
        """
        distance = math.sqrt((player_x - self.x) ** 2 + (player_y - self.y) ** 2)
        return distance <= self.pickup_range

    def get_pickup_info(self) -> dict:
        """
        取得撿拾資訊\n
        \n
        回傳物品的詳細資料供玩家使用\n
        \n
        回傳:\n
        dict: 物品資訊和效果數據\n
        """
        return {
            "potion_type": self.potion_type,
            "name": self.config["name"],
            "effect_value": self.config["effect_value"],
            "description": self.config["description"],
            "remaining_time": self.lifetime,
        }


######################藥水掉落管理器######################
class PotionDropManager:
    """
    藥水掉落管理器\n
    \n
    管理藥水物品的生成、更新和撿拾：\n
    1. 從敵人或寶箱掉落藥水（50% 機率）\n
    2. 管理場景中的所有藥水物品\n
    3. 處理玩家撿拾邏輯和效果應用\n
    4. 清理過期的藥水物品\n
    """

    def __init__(self):
        """
        初始化掉落管理器\n
        """
        # 場景中的所有藥水物品
        self.potions = []

        # 基礎掉落機率
        self.base_drop_chance = 0.5  # 50% 掉落率

        # 不同來源的掉落機率修正
        self.drop_chance_modifiers = {
            "basic_enemy": 1.0,  # 基礎敵人使用標準機率
            "elite_enemy": 1.2,  # 精英敵人機率提升 20%
            "boss": 2.0,  # Boss 100% 掉落（0.5 * 2.0 = 1.0）
            "treasure_box": 1.4,  # 寶箱機率提升 40%
        }

        # 藥水類型權重（決定掉落哪種藥水的機率）
        self.potion_type_weights = {
            "healing": 0.5,  # 50% 機率掉治療藥水
            "shield": 0.3,  # 30% 機率掉護盾藥水
            "attack": 0.2,  # 20% 機率掉攻擊藥水
        }

    def try_drop_potion(self, x: int, y: int, source_type: str = "basic_enemy") -> bool:
        """
        嘗試在指定位置掉落藥水\n
        \n
        根據掉落源類型和機率決定是否生成藥水物品\n
        \n
        參數:\n
        x (int): 掉落位置 x 座標\n
        y (int): 掉落位置 y 座標\n
        source_type (str): 掉落源類型\n
        \n
        回傳:\n
        bool: 是否成功掉落物品\n
        """
        # 計算實際掉落機率
        modifier = self.drop_chance_modifiers.get(source_type, 1.0)
        actual_drop_chance = min(1.0, self.base_drop_chance * modifier)

        if random.random() < actual_drop_chance:
            # 根據權重選擇藥水類型
            potion_type = self._choose_potion_type()

            # 創建藥水物品
            potion = Potion(x, y, potion_type)
            self.potions.append(potion)
            return True

        return False

    def _choose_potion_type(self) -> str:
        """
        根據權重隨機選擇藥水類型\n
        \n
        回傳:\n
        str: 選中的藥水類型\n
        """
        rand = random.random()
        cumulative_weight = 0.0

        for potion_type, weight in self.potion_type_weights.items():
            cumulative_weight += weight
            if rand <= cumulative_weight:
                return potion_type

        # 如果沒有選中任何類型（理論上不會發生），返回治療藥水
        return "healing"

    def force_drop_potion(self, x: int, y: int, potion_type: str) -> Potion:
        """
        強制在指定位置掉落指定藥水\n
        \n
        用於特殊情況或測試用途\n
        \n
        參數:\n
        x (int): 掉落位置 x 座標\n
        y (int): 掉落位置 y 座標\n
        potion_type (str): 藥水類型\n
        \n
        回傳:\n
        Potion: 創建的藥水物品\n
        """
        potion = Potion(x, y, potion_type)
        self.potions.append(potion)
        return potion

    def update(self):
        """
        更新所有藥水物品\n
        \n
        處理動畫效果並移除過期物品\n
        """
        # 更新每個藥水
        for potion in self.potions[:]:  # 使用複本避免修改時出錯
            potion.update()

            # 移除過期藥水
            if potion.is_expired():
                self.potions.remove(potion)

    def draw(self, screen, camera_x=0, camera_y=0):
        """
        繪製所有藥水物品\n
        \n
        參數:\n
        screen: pygame 畫面物件\n
        camera_x (int): 攝影機 x 偏移\n
        camera_y (int): 攝影機 y 偏移\n
        """
        for potion in self.potions:
            potion.draw(screen, camera_x, camera_y)

    def check_pickup(self, player_x: int, player_y: int, player) -> list:
        """
        檢查玩家撿拾並收集藥水到庫存\n
        \n
        檢測玩家範圍內的藥水並加入玩家庫存\n
        \n
        參數:\n
        player_x (int): 玩家 x 座標\n
        player_y (int): 玩家 y 座標\n
        player: 玩家物件\n
        \n
        回傳:\n
        list: 撿到的藥水資訊清單\n
        """
        picked_potions = []

        for potion in self.potions[:]:  # 使用複本避免修改時出錯
            if potion.can_pickup(player_x, player_y):
                # 嘗試添加藥水到玩家庫存
                if player.add_potion(potion.potion_type):
                    # 記錄撿拾資訊
                    picked_potions.append(potion.get_pickup_info())
                    # 從場景中移除藥水
                    self.potions.remove(potion)

        return picked_potions

    def clear_all(self):
        """
        清空所有藥水物品\n
        \n
        用於重新開始遊戲或切換關卡\n
        """
        self.potions.clear()

    def get_potion_count(self) -> int:
        """
        取得場景中的藥水物品數量\n
        \n
        回傳:\n
        int: 物品數量\n
        """
        return len(self.potions)
