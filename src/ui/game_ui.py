######################載入套件######################
import pygame
from typing import Tuple, Optional


######################遊戲 UI 管理類別######################
class GameUI:
    """
    遊戲使用者介面管理系統\n
    \n
    負責管理遊戲中所有的 UI 元素：\n
    1. 角色選擇選單\n
    2. 遊戲中的 HUD（血量、分數、關卡資訊）\n
    3. 暫停選單\n
    4. 遊戲結束畫面\n
    \n
    屬性:\n
    screen_width, screen_height (int): 螢幕尺寸\n
    fonts (dict): 不同大小的字型物件\n
    ui_colors (dict): UI 使用的顏色配色\n
    \n
    UI 設計原則:\n
    - 簡潔明瞭的資訊顯示\n
    - 一致的色彩風格\n
    - 適當的字型大小和層次\n
    - 響應式的佈局設計\n
    """

    def __init__(self, screen_width: int, screen_height: int):
        """
        初始化 UI 系統\n
        \n
        設定螢幕尺寸、字型和顏色配置\n
        \n
        參數:\n
        screen_width (int): 螢幕寬度\n
        screen_height (int): 螢幕高度\n
        """
        self.screen_width = screen_width
        self.screen_height = screen_height

        # 初始化字型系統
        pygame.font.init()
        self.fonts = self._initialize_chinese_fonts()

        # UI 顏色配置
        self.ui_colors = {
            "background": (0, 0, 0, 180),  # 半透明黑色背景
            "primary": (255, 255, 255),  # 主要文字顏色（白色）
            "secondary": (200, 200, 200),  # 次要文字顏色（淺灰）
            "accent": (255, 215, 0),  # 強調色（金色）
            "danger": (255, 0, 0),  # 危險色（紅色）
            "success": (0, 255, 0),  # 成功色（綠色）
            "warning": (255, 255, 0),  # 警告色（黃色）
            "info": (0, 150, 255),  # 資訊色（藍色）
            "health_high": (0, 200, 0),  # 高血量（綠）
            "health_medium": (255, 200, 0),  # 中血量（黃）
            "health_low": (255, 50, 50),  # 低血量（紅）
        }

        # 角色選擇相關
        self.character_info = [
            {
                "name": "平衡瑪莉歐",
                "description": "全面均衡的能力",
                "color": (255, 0, 0),
                "stats": {"血量": 100, "速度": 5, "跳躍": 12, "攻擊": 20},
            },
            {
                "name": "疾速瑪莉歐",
                "description": "超快移動速度",
                "color": (0, 255, 0),
                "stats": {"血量": 80, "速度": 8, "跳躍": 10, "攻擊": 15},
            },
            {
                "name": "跳跳瑪莉歐",
                "description": "擁有二段跳能力",
                "color": (0, 0, 255),
                "stats": {"血量": 90, "速度": 4, "跳躍": 15, "攻擊": 18},
            },
            {
                "name": "坦克瑪莉歐",
                "description": "高血量高攻擊",
                "color": (128, 0, 128),
                "stats": {"血量": 150, "速度": 3, "跳躍": 8, "攻擊": 25},
            },
        ]

        # UI 動畫效果
        self.animation_timer = 0
        self.pulse_effect = 0

    def _initialize_chinese_fonts(self):
        """
        初始化支援繁體中文的字型系統\n
        \n
        嘗試載入支援中文的字型，如果找不到就使用系統預設字型\n
        \n
        回傳:\n
        dict: 包含不同大小字型的字典\n
        """
        import os
        import platform

        # 常見的中文字型路徑
        chinese_font_paths = []

        # Windows 系統字型路徑
        if platform.system() == "Windows":
            chinese_font_paths = [
                "C:/Windows/Fonts/msjh.ttc",  # 微軟正黑體
                "C:/Windows/Fonts/mingliu.ttc",  # 細明體
                "C:/Windows/Fonts/simsun.ttc",  # 宋體
                "C:/Windows/Fonts/kaiu.ttf",  # 標楷體
            ]
        # macOS 系統字型路徑
        elif platform.system() == "Darwin":
            chinese_font_paths = [
                "/System/Library/Fonts/PingFang.ttc",
                "/Library/Fonts/Arial Unicode MS.ttf",
                "/System/Library/Fonts/STHeiti Light.ttc",
            ]
        # Linux 系統字型路徑
        elif platform.system() == "Linux":
            chinese_font_paths = [
                "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
                "/usr/share/fonts/truetype/arphic/uming.ttc",
                "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
            ]

        # 尋找可用的中文字型
        font_path = None
        for path in chinese_font_paths:
            if os.path.exists(path):
                font_path = path
                print(f"找到中文字型: {path}")
                break

        # 嘗試載入字型
        fonts = {}
        font_sizes = {"title": 72, "large": 48, "medium": 36, "small": 24, "tiny": 18}

        for name, size in font_sizes.items():
            try:
                if font_path:
                    # 使用找到的中文字型
                    fonts[name] = pygame.font.Font(font_path, size)
                else:
                    # 使用系統預設字型
                    print("警告: 未找到中文字型檔案，使用系統預設字型")
                    fonts[name] = pygame.font.Font(None, size)
            except Exception as e:
                print(f"載入字型失敗 {name}: {e}")
                # 降級使用系統預設字型
                fonts[name] = pygame.font.Font(None, size)

        return fonts

    def update_animations(self):
        """
        更新 UI 動畫效果\n
        \n
        處理各種 UI 元素的動畫和特效\n
        """
        self.animation_timer += 1
        if self.animation_timer >= 1000:
            self.animation_timer = 0

        # 脈衝效果（用於強調某些元素）
        import math

        self.pulse_effect = 0.8 + 0.2 * math.sin(self.animation_timer * 0.1)

    def draw_character_selection(self, screen: pygame.Surface, selected_index: int):
        """
        繪製角色選擇選單\n
        \n
        顯示可選角色和其能力資訊\n
        \n
        參數:\n
        screen (pygame.Surface): 螢幕表面\n
        selected_index (int): 目前選中的角色索引\n
        """
        self.update_animations()

        # 繪製半透明背景
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(200)
        overlay.fill((20, 30, 50))  # 深藍色背景
        screen.blit(overlay, (0, 0))

        # 標題
        title_text = self.fonts["title"].render(
            "選擇你的角色", True, self.ui_colors["accent"]
        )
        title_rect = title_text.get_rect(center=(self.screen_width // 2, 80))
        screen.blit(title_text, title_rect)

        # 操作提示
        hint_text = self.fonts["small"].render(
            "使用 ← → 選擇角色，按 Enter 開始遊戲", True, self.ui_colors["secondary"]
        )
        hint_rect = hint_text.get_rect(
            center=(self.screen_width // 2, self.screen_height - 50)
        )
        screen.blit(hint_text, hint_rect)

        # 繪製角色選項
        self._draw_character_options(screen, selected_index)

    def _draw_character_options(self, screen: pygame.Surface, selected_index: int):
        """
        繪製角色選項卡\n
        \n
        顯示每個角色的詳細資訊\n
        """
        # 計算每個角色卡片的位置和大小
        card_width = 250
        card_height = 350
        spacing = 30
        total_width = (
            len(self.character_info) * card_width
            + (len(self.character_info) - 1) * spacing
        )
        start_x = (self.screen_width - total_width) // 2
        start_y = 150

        for i, character in enumerate(self.character_info):
            card_x = start_x + i * (card_width + spacing)
            card_y = start_y

            # 選中的角色卡片會有特殊效果
            is_selected = i == selected_index

            self._draw_character_card(
                screen, character, card_x, card_y, card_width, card_height, is_selected
            )

    def _draw_character_card(
        self,
        screen: pygame.Surface,
        character: dict,
        x: int,
        y: int,
        width: int,
        height: int,
        is_selected: bool,
    ):
        """
        繪製單個角色卡片\n
        \n
        顯示角色的詳細資訊和能力數值\n
        """
        # 卡片背景
        card_color = (80, 80, 80) if not is_selected else (120, 120, 120)
        border_color = (
            self.ui_colors["secondary"] if not is_selected else self.ui_colors["accent"]
        )
        border_width = 2 if not is_selected else int(4 * self.pulse_effect)

        # 繪製卡片背景
        card_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(screen, card_color, card_rect)
        pygame.draw.rect(screen, border_color, card_rect, border_width)

        # 角色預覽（簡單的彩色矩形）
        preview_size = 80
        preview_x = x + (width - preview_size) // 2
        preview_y = y + 20
        preview_rect = pygame.Rect(preview_x, preview_y, preview_size, preview_size)
        pygame.draw.rect(screen, character["color"], preview_rect)
        pygame.draw.rect(screen, (0, 0, 0), preview_rect, 3)

        # 角色名稱
        name_text = self.fonts["medium"].render(
            character["name"], True, self.ui_colors["primary"]
        )
        name_rect = name_text.get_rect(
            center=(x + width // 2, preview_y + preview_size + 30)
        )
        screen.blit(name_text, name_rect)

        # 角色描述
        desc_text = self.fonts["small"].render(
            character["description"], True, self.ui_colors["secondary"]
        )
        desc_rect = desc_text.get_rect(center=(x + width // 2, name_rect.bottom + 20))
        screen.blit(desc_text, desc_rect)

        # 能力數值
        stats_y = desc_rect.bottom + 30
        for i, (stat_name, stat_value) in enumerate(character["stats"].items()):
            self._draw_stat_bar(
                screen, stat_name, stat_value, x + 20, stats_y + i * 35, width - 40
            )

    def _draw_stat_bar(
        self,
        screen: pygame.Surface,
        stat_name: str,
        stat_value: int,
        x: int,
        y: int,
        width: int,
    ):
        """
        繪製能力數值條\n
        \n
        以進度條的形式顯示角色能力\n
        """
        # 能力名稱
        name_text = self.fonts["tiny"].render(
            stat_name, True, self.ui_colors["primary"]
        )
        screen.blit(name_text, (x, y - 15))

        # 數值條背景
        bar_height = 8
        bar_rect = pygame.Rect(x, y, width, bar_height)
        pygame.draw.rect(screen, (50, 50, 50), bar_rect)

        # 數值條填充（根據數值類型設定最大值）
        max_values = {"血量": 150, "速度": 8, "跳躍": 15, "攻擊": 25}
        max_value = max_values.get(stat_name, 100)

        fill_ratio = min(stat_value / max_value, 1.0)
        fill_width = int(width * fill_ratio)

        # 根據數值高低選擇顏色
        if fill_ratio > 0.8:
            fill_color = self.ui_colors["success"]
        elif fill_ratio > 0.5:
            fill_color = self.ui_colors["warning"]
        else:
            fill_color = self.ui_colors["danger"]

        if fill_width > 0:
            fill_rect = pygame.Rect(x, y, fill_width, bar_height)
            pygame.draw.rect(screen, fill_color, fill_rect)

        # 數值文字
        value_text = self.fonts["tiny"].render(
            str(stat_value), True, self.ui_colors["primary"]
        )
        value_rect = value_text.get_rect(right=x + width, centery=y + bar_height // 2)
        screen.blit(value_text, value_rect)

    def draw_game_ui(self, screen: pygame.Surface, player, level_number: int):
        """
        繪製遊戲中的 HUD 介面\n
        \n
        顯示玩家狀態、關卡資訊等重要資料\n
        \n
        參數:\n
        screen (pygame.Surface): 螢幕表面\n
        player: 玩家物件\n
        level_number (int): 當前關卡編號\n
        """
        # 繪製玩家血量條
        self._draw_player_health(screen, player)

        # 繪製關卡資訊
        self._draw_level_info(screen, level_number)

        # 繪製操作提示
        self._draw_controls_hint(screen)

    def _draw_player_health(self, screen: pygame.Surface, player):
        """
        繪製玩家血量條\n
        \n
        在螢幕左上角顯示玩家的血量狀態\n
        """
        # 血量條位置和大小
        bar_x = 20
        bar_y = 20
        bar_width = 200
        bar_height = 20

        # 背景
        bg_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        pygame.draw.rect(screen, (50, 50, 50), bg_rect)
        pygame.draw.rect(screen, (255, 255, 255), bg_rect, 2)

        # 血量填充
        health_ratio = player.health / player.max_health
        fill_width = int(bar_width * health_ratio)

        # 根據血量比例選擇顏色
        if health_ratio > 0.6:
            health_color = self.ui_colors["health_high"]
        elif health_ratio > 0.3:
            health_color = self.ui_colors["health_medium"]
        else:
            health_color = self.ui_colors["health_low"]

        if fill_width > 0:
            fill_rect = pygame.Rect(bar_x, bar_y, fill_width, bar_height)
            pygame.draw.rect(screen, health_color, fill_rect)

        # 血量數值文字
        health_text = self.fonts["small"].render(
            f"{player.health}/{player.max_health}", True, self.ui_colors["primary"]
        )
        text_rect = health_text.get_rect(
            center=(bar_x + bar_width // 2, bar_y + bar_height // 2)
        )
        screen.blit(health_text, text_rect)

        # 角色名稱
        name_text = self.fonts["tiny"].render(
            player.name, True, self.ui_colors["secondary"]
        )
        screen.blit(name_text, (bar_x, bar_y - 15))

    def _draw_level_info(self, screen: pygame.Surface, level_number: int):
        """
        繪製關卡資訊\n
        \n
        在螢幕右上角顯示當前關卡\n
        """
        info_text = self.fonts["medium"].render(
            f"第 {level_number} 關", True, self.ui_colors["accent"]
        )
        info_rect = info_text.get_rect(right=self.screen_width - 20, top=20)
        screen.blit(info_text, info_rect)

    def _draw_controls_hint(self, screen: pygame.Surface):
        """
        繪製操作提示\n
        \n
        在螢幕底部顯示基本操作說明\n
        """
        hints = [
            "AD/方向鍵: 移動",
            "空白鍵/W: 跳躍",
            "S: 蹲下",
            "R: 加速衝刺",
            "C: 攻擊",
            "ESC: 暫停",
        ]

        hint_y = self.screen_height - 80  # 調整位置給更多提示留空間
        for i, hint in enumerate(hints):
            hint_text = self.fonts["tiny"].render(
                hint, True, self.ui_colors["secondary"]
            )
            hint_rect = hint_text.get_rect(left=20, top=hint_y + i * 15)
            screen.blit(hint_text, hint_rect)

    def draw_pause_menu(self, screen: pygame.Surface):
        """
        繪製暫停選單\n
        \n
        顯示暫停時的選項選單\n
        """
        # 半透明遮罩
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(150)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        # 暫停標題
        title_text = self.fonts["title"].render(
            "遊戲暫停", True, self.ui_colors["accent"]
        )
        title_rect = title_text.get_rect(
            center=(self.screen_width // 2, self.screen_height // 2 - 50)
        )
        screen.blit(title_text, title_rect)

        # 選項提示
        options = ["空白鍵 - 繼續遊戲", "ESC - 返回選單"]

        for i, option in enumerate(options):
            option_text = self.fonts["medium"].render(
                option, True, self.ui_colors["primary"]
            )
            option_rect = option_text.get_rect(
                center=(self.screen_width // 2, self.screen_height // 2 + 30 + i * 50)
            )
            screen.blit(option_text, option_rect)

    def draw_game_over(self, screen: pygame.Surface):
        """
        繪製遊戲結束畫面\n
        \n
        顯示遊戲失敗的訊息和重試選項\n
        """
        # 半透明紅色遮罩
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(180)
        overlay.fill((50, 0, 0))
        screen.blit(overlay, (0, 0))

        # 遊戲結束標題
        title_text = self.fonts["title"].render(
            "遊戲結束", True, self.ui_colors["danger"]
        )
        title_rect = title_text.get_rect(
            center=(self.screen_width // 2, self.screen_height // 2 - 50)
        )
        screen.blit(title_text, title_rect)

        # 重試提示
        retry_text = self.fonts["medium"].render(
            "按 ESC 返回選單重新開始", True, self.ui_colors["primary"]
        )
        retry_rect = retry_text.get_rect(
            center=(self.screen_width // 2, self.screen_height // 2 + 50)
        )
        screen.blit(retry_text, retry_rect)
