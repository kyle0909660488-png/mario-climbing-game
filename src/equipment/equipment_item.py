######################載入套件######################
import pygame
import random
import math


######################裝備物品基礎類別######################
class EquipmentItem:
    """
    裝備物品基礎類別\n
    \n
    代表地面上可撿拾的裝備物品：\n
    1. 套裝件的視覺呈現\n
    2. 撿拾範圍和動畫效果\n
    3. 品質分級和稀有度顯示\n
    4. 自動消失機制\n
    \n
    屬性:\n
    x, y (int): 物品位置座標\n
    set_name (str): 所屬套裝名稱\n
    rarity (str): 稀有度等級\n
    lifetime (int): 存在時間計數器\n
    """

    def __init__(self, x: int, y: int, set_name: str):
        """
        初始化裝備物品\n
        \n
        參數:\n
        x (int): 生成位置 x 座標\n
        y (int): 生成位置 y 座標\n
        set_name (str): 套裝名稱 ('fire', 'ice', 'shadow', 'tank')\n
        """
        self.x = x
        self.y = y
        self.set_name = set_name

        # 物品尺寸
        self.width = 20
        self.height = 20

        # 品質分級（影響外觀和效果）
        self.rarity = self._determine_rarity()

        # 存在時間（10秒後消失）
        self.lifetime = 600
        self.max_lifetime = 600

        # 動畫效果
        self.float_offset = 0
        self.glow_intensity = 0
        self.pulse_timer = 0

        # 撿拾範圍
        self.pickup_range = 25

        # 套裝顏色配置
        self.colors = {
            "fire": (255, 100, 0),
            "ice": (100, 200, 255),
            "shadow": (80, 80, 80),
            "tank": (150, 150, 150),
        }

        # 稀有度配置
        self.rarity_effects = {
            "common": {"glow": (255, 255, 255), "bonus": 1.0},
            "rare": {"glow": (0, 255, 0), "bonus": 1.2},
            "epic": {"glow": (128, 0, 255), "bonus": 1.5},
            "legendary": {"glow": (255, 215, 0), "bonus": 2.0},
        }

    def _determine_rarity(self) -> str:
        """
        決定裝備稀有度\n
        \n
        根據機率分配稀有度等級\n
        \n
        回傳:\n
        str: 稀有度名稱\n
        """
        rand = random.random()
        if rand < 0.6:  # 60%
            return "common"
        elif rand < 0.85:  # 25%
            return "rare"
        elif rand < 0.95:  # 10%
            return "epic"
        else:  # 5%
            return "legendary"

    def update(self):
        """
        更新裝備物品狀態\n
        \n
        處理動畫效果和存在時間倒數\n
        """
        # 減少存在時間
        self.lifetime -= 1

        # 更新浮動動畫
        self.float_offset = math.sin(pygame.time.get_ticks() * 0.005) * 3

        # 更新光暈效果
        self.pulse_timer += 1
        self.glow_intensity = abs(math.sin(self.pulse_timer * 0.1)) * 50

    def draw(self, screen, camera_x=0, camera_y=0):
        """
        繪製裝備物品\n
        \n
        包含套裝顏色、稀有度光暈和動畫效果\n
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

        # 繪製稀有度光暈
        if self.rarity != "common":
            glow_color = self.rarity_effects[self.rarity]["glow"]
            glow_alpha = int(self.glow_intensity)

            # 創建光暈表面
            glow_size = self.width + 20
            glow_surface = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)

            # 繪製漸變光暈
            for i in range(3):
                radius = (glow_size // 2) - i * 3
                alpha = glow_alpha // (i + 1)
                color_with_alpha = (*glow_color, alpha)

                pygame.draw.circle(
                    glow_surface,
                    color_with_alpha,
                    (glow_size // 2, glow_size // 2),
                    radius,
                )

            screen.blit(glow_surface, (screen_x - 10, screen_y - 10))

        # 繪製主要物品
        base_color = self.colors.get(self.set_name, (128, 128, 128))

        # 根據稀有度調整顏色亮度
        brightness_bonus = self.rarity_effects[self.rarity]["bonus"]
        enhanced_color = tuple(min(255, int(c * brightness_bonus)) for c in base_color)

        # 繪製物品外框
        pygame.draw.rect(
            screen,
            (255, 255, 255),
            (screen_x - 1, screen_y - 1, self.width + 2, self.height + 2),
        )

        # 繪製物品主體
        pygame.draw.rect(
            screen, enhanced_color, (screen_x, screen_y, self.width, self.height)
        )

        # 繪製套裝圖案（簡化的符號）
        self._draw_set_symbol(screen, screen_x, screen_y, enhanced_color)

        # 繪製存在時間警告（最後2秒）
        if self.lifetime < 120:
            alpha = int(abs(math.sin(self.lifetime * 0.1)) * 255)
            warning_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            warning_surface.fill((255, 0, 0, alpha))
            screen.blit(warning_surface, (screen_x, screen_y))

    def _draw_set_symbol(self, screen, x, y, color):
        """
        繪製套裝專屬符號\n
        \n
        用簡單圖形表示不同套裝類型\n
        \n
        參數:\n
        screen: pygame 畫面物件\n
        x, y (int): 繪製位置\n
        color: 基礎顏色\n
        """
        center_x = x + self.width // 2
        center_y = y + self.height // 2

        if self.set_name == "fire":
            # 火焰：三角形
            points = [
                (center_x, y + 3),
                (center_x - 6, y + self.height - 3),
                (center_x + 6, y + self.height - 3),
            ]
            pygame.draw.polygon(screen, (255, 255, 0), points)

        elif self.set_name == "ice":
            # 冰霜：雪花（十字形）
            pygame.draw.line(
                screen,
                (255, 255, 255),
                (center_x, y + 3),
                (center_x, y + self.height - 3),
                2,
            )
            pygame.draw.line(
                screen,
                (255, 255, 255),
                (x + 3, center_y),
                (x + self.width - 3, center_y),
                2,
            )
            pygame.draw.line(
                screen,
                (255, 255, 255),
                (x + 5, y + 5),
                (x + self.width - 5, y + self.height - 5),
                1,
            )
            pygame.draw.line(
                screen,
                (255, 255, 255),
                (x + self.width - 5, y + 5),
                (x + 5, y + self.height - 5),
                1,
            )

        elif self.set_name == "shadow":
            # 影子：圓形
            pygame.draw.circle(screen, (200, 200, 200), (center_x, center_y), 6)
            pygame.draw.circle(screen, (50, 50, 50), (center_x, center_y), 4)

        elif self.set_name == "tank":
            # 坦克：正方形
            pygame.draw.rect(
                screen, (200, 200, 200), (center_x - 5, center_y - 5, 10, 10)
            )
            pygame.draw.rect(
                screen, (100, 100, 100), (center_x - 3, center_y - 3, 6, 6)
            )

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
        回傳物品的詳細資料供玩家參考\n
        \n
        回傳:\n
        dict: 物品資訊\n
        """
        set_names = {
            "fire": "火焰套裝",
            "ice": "冰霜套裝",
            "shadow": "影子套裝",
            "tank": "坦克套裝",
        }

        rarity_names = {
            "common": "普通",
            "rare": "稀有",
            "epic": "史詩",
            "legendary": "傳說",
        }

        return {
            "set_name": self.set_name,
            "set_display_name": set_names.get(self.set_name, "未知套裝"),
            "rarity": self.rarity,
            "rarity_display_name": rarity_names.get(self.rarity, "未知"),
            "bonus_multiplier": self.rarity_effects[self.rarity]["bonus"],
            "remaining_time": self.lifetime,
        }


######################套裝掉落管理器######################
class EquipmentDropManager:
    """
    套裝掉落管理器\n
    \n
    管理裝備物品的生成、更新和撿拾：\n
    1. 從敵人或寶箱掉落裝備\n
    2. 管理場景中的所有裝備物品\n
    3. 處理玩家撿拾邏輯\n
    4. 清理過期的裝備物品\n
    """

    def __init__(self):
        """
        初始化掉落管理器\n
        """
        # 場景中的所有裝備物品
        self.items = []

        # 掉落機率配置
        self.drop_chances = {
            "basic_enemy": 0.15,  # 基礎敵人 15% 掉落率
            "elite_enemy": 0.35,  # 精英敵人 35% 掉落率
            "boss": 1.0,  # Boss 100% 掉落率
            "treasure_box": 0.8,  # 寶箱 80% 掉落率
        }

    def try_drop_item(self, x: int, y: int, source_type: str = "basic_enemy") -> bool:
        """
        嘗試在指定位置掉落裝備\n
        \n
        根據掉落源類型決定是否生成裝備物品\n
        \n
        參數:\n
        x (int): 掉落位置 x 座標\n
        y (int): 掉落位置 y 座標\n
        source_type (str): 掉落源類型\n
        \n
        回傳:\n
        bool: 是否成功掉落物品\n
        """
        drop_chance = self.drop_chances.get(source_type, 0.1)

        if random.random() < drop_chance:
            # 隨機選擇套裝類型
            set_types = ["fire", "ice", "shadow", "tank"]
            set_name = random.choice(set_types)

            # 創建裝備物品
            item = EquipmentItem(x, y, set_name)
            self.items.append(item)
            return True

        return False

    def force_drop_item(self, x: int, y: int, set_name: str) -> EquipmentItem:
        """
        強制在指定位置掉落指定套裝\n
        \n
        用於特殊情況或獎勵機制\n
        \n
        參數:\n
        x (int): 掉落位置 x 座標\n
        y (int): 掉落位置 y 座標\n
        set_name (str): 套裝類型\n
        \n
        回傳:\n
        EquipmentItem: 創建的裝備物品\n
        """
        item = EquipmentItem(x, y, set_name)
        self.items.append(item)
        return item

    def update(self):
        """
        更新所有裝備物品\n
        \n
        處理動畫效果並移除過期物品\n
        """
        # 更新每個物品
        for item in self.items[:]:  # 使用複本避免修改時出錯
            item.update()

            # 移除過期物品
            if item.is_expired():
                self.items.remove(item)

    def draw(self, screen, camera_x=0, camera_y=0):
        """
        繪製所有裝備物品\n
        \n
        參數:\n
        screen: pygame 畫面物件\n
        camera_x (int): 攝影機 x 偏移\n
        camera_y (int): 攝影機 y 偏移\n
        """
        for item in self.items:
            item.draw(screen, camera_x, camera_y)

    def check_pickup(self, player_x: int, player_y: int, equipment_manager) -> list:
        """
        檢查玩家撿拾\n
        \n
        檢測玩家範圍內的裝備並進行撿拾\n
        \n
        參數:\n
        player_x (int): 玩家 x 座標\n
        player_y (int): 玩家 y 座標\n
        equipment_manager: 裝備管理器\n
        \n
        回傳:\n
        list: 撿到的裝備資訊清單\n
        """
        picked_items = []

        for item in self.items[:]:  # 使用複本避免修改時出錯
            if item.can_pickup(player_x, player_y):
                # 將裝備添加到玩家裝備中
                if equipment_manager.add_set_piece(item.set_name):
                    picked_items.append(item.get_pickup_info())
                    self.items.remove(item)

        return picked_items

    def clear_all(self):
        """
        清空所有裝備物品\n
        \n
        用於重新開始遊戲或切換關卡\n
        """
        self.items.clear()

    def get_item_count(self) -> int:
        """
        取得場景中的裝備物品數量\n
        \n
        回傳:\n
        int: 物品數量\n
        """
        return len(self.items)
