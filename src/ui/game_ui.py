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
                "stats": {"血量": 130, "速度": 6, "跳躍": 16, "攻擊": 25},
            },
            {
                "name": "跳跳瑪莉歐",
                "description": "擁有二段跳能力",
                "color": (0, 0, 255),
                "stats": {"血量": 100, "速度": 4, "跳躍": 17, "攻擊": 20},
            },
            {
                "name": "坦克瑪莉歐",
                "description": "高血量高攻擊",
                "color": (128, 0, 128),
                "stats": {"血量": 150, "速度": 5, "跳躍": 15, "攻擊": 28},
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

    def _get_stat_comparison_color(self, stat_name: str, stat_value: int):
        """
        根據三隻角色的數值比較，決定數值條的顏色\n
        \n
        參數:\n
        stat_name (str): 能力名稱（血量、速度、跳躍、攻擊）\n
        stat_value (int): 該角色的能力數值\n
        \n
        回傳:\n
        tuple: RGB 顏色值，最大值為綠色，最小值為紅色，其他為黃色\n
        """
        # 收集所有角色的該項數值
        stat_values = [
            character["stats"][stat_name] for character in self.character_info
        ]

        max_value = max(stat_values)
        min_value = min(stat_values)

        # 如果該數值是最大值，顯示綠色
        if stat_value == max_value:
            return (50, 255, 50)  # 綠色
        # 如果該數值是最小值，顯示紅色
        elif stat_value == min_value:
            return (255, 50, 50)  # 紅色
        # 其他數值顯示黃色
        else:
            return (255, 255, 50)  # 黃色

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
        以進度條的形式顯示角色能力，根據三隻角色的數值比較使用不同顏色：\n
        - 最大值：綠色\n
        - 最小值：紅色\n
        - 中間值：黃色\n
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
        max_values = {"血量": 150, "速度": 8, "跳躍": 18, "攻擊": 30}
        max_value = max_values.get(stat_name, 100)

        fill_ratio = min(stat_value / max_value, 1.0)
        fill_width = int(width * fill_ratio)

        # 根據三隻角色的數值比較選擇顏色
        fill_color = self._get_stat_comparison_color(stat_name, stat_value)

        if fill_width > 0:
            fill_rect = pygame.Rect(x, y, fill_width, bar_height)
            pygame.draw.rect(screen, fill_color, fill_rect)

        # 數值文字，使用相同的比較顏色
        value_text = self.fonts["tiny"].render(str(stat_value), True, fill_color)
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
        # 繪製玩家血量條和攻擊模式指示器
        self._draw_player_health(screen, player)

        # 繪製關卡資訊
        self._draw_level_info(screen, level_number)

        # 繪製藥水庫存（在關卡資訊下方）
        self._draw_potion_inventory(screen, player)

        # 繪製操作提示
        self._draw_controls_hint(screen)

    def _draw_player_health(self, screen: pygame.Surface, player):
        """
        繪製玩家血量條、護盾和狀態效果\n
        \n
        在螢幕左上角顯示玩家的血量狀態、護盾值和攻擊模式\n
        """
        # 血量條位置和大小
        bar_x = 20
        bar_y = 20
        bar_width = 200
        bar_height = 20

        # 血量條背景
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

        # 護盾條（如果有護盾值）
        shield_y = bar_y + bar_height + 5
        if hasattr(player, "shield") and player.shield > 0:
            # 護盾條背景
            shield_bg_rect = pygame.Rect(bar_x, shield_y, bar_width, 15)
            pygame.draw.rect(screen, (30, 30, 60), shield_bg_rect)
            pygame.draw.rect(screen, (100, 150, 255), shield_bg_rect, 2)

            # 護盾填充
            shield_ratio = player.shield / player.max_shield
            shield_fill_width = int(bar_width * shield_ratio)

            if shield_fill_width > 0:
                shield_fill_rect = pygame.Rect(bar_x, shield_y, shield_fill_width, 15)
                pygame.draw.rect(screen, (50, 150, 255), shield_fill_rect)

            # 護盾數值文字
            shield_text = self.fonts["tiny"].render(
                f"護盾: {player.shield}/{player.max_shield}", True, (200, 220, 255)
            )
            screen.blit(shield_text, (bar_x + bar_width + 10, shield_y))

        # 角色名稱
        name_text = self.fonts["tiny"].render(
            player.name, True, self.ui_colors["secondary"]
        )
        screen.blit(name_text, (bar_x, bar_y - 15))

        # 攻擊力增強效果顯示
        attack_boost_y = (
            shield_y + 20
            if (hasattr(player, "shield") and player.shield > 0)
            else bar_y + bar_height + 10
        )
        if (
            hasattr(player, "attack_boost_percentage")
            and player.attack_boost_percentage > 0
        ):
            # 顯示攻擊力增強效果
            boost_text = self.fonts["tiny"].render(
                f"攻擊力 +{player.attack_boost_percentage}% ({player.attack_boost_duration // 60}秒)",
                True,
                (255, 200, 50),
            )
            screen.blit(boost_text, (bar_x, attack_boost_y))
            attack_boost_y += 15

        # 在血條下方顯示攻擊模式
        self._draw_attack_mode_indicator(screen, player, bar_x, attack_boost_y)

    def _draw_attack_mode_indicator(
        self, screen: pygame.Surface, player, x: int, y: int
    ):
        """
        在血條下方顯示當前攻擊模式指示器\n
        \n
        根據玩家當前的投射物類型顯示對應的模式標籤\n
        \n
        參數:\n
        screen (pygame.Surface): 螢幕表面\n
        player: 玩家物件\n
        x (int): 指示器 X 座標\n
        y (int): 指示器 Y 座標\n
        """
        # 檢查玩家是否有投射物類型屬性
        if not hasattr(player, "projectile_type"):
            return

        # 根據投射物類型設定顯示內容和顏色
        if player.projectile_type == "fireball":
            mode_text = "🔥 火焰球模式"
            mode_color = (255, 100, 50)  # 橙紅色
            bg_color = (80, 25, 15)  # 深紅色背景
        elif player.projectile_type == "iceball":
            mode_text = "❄️ 冰凍球模式"
            mode_color = (150, 200, 255)  # 淺藍色
            bg_color = (25, 40, 80)  # 深藍色背景
        else:
            mode_text = "❓ 未知模式"
            mode_color = (200, 200, 200)  # 灰色
            bg_color = (40, 40, 40)  # 深灰色背景

        # 計算文字尺寸和背景框
        mode_surface = self.fonts["tiny"].render(mode_text, True, mode_color)
        text_width = mode_surface.get_width()
        text_height = mode_surface.get_height()

        # 添加一些內邊距
        padding = 6
        bg_width = text_width + padding * 2
        bg_height = text_height + padding

        # 繪製背景框
        bg_rect = pygame.Rect(x, y, bg_width, bg_height)
        pygame.draw.rect(screen, bg_color, bg_rect)
        pygame.draw.rect(screen, mode_color, bg_rect, 1)  # 邊框

        # 繪製文字
        text_x = x + padding
        text_y = y + padding // 2
        screen.blit(mode_surface, (text_x, text_y))

        # 繪製切換提示（在指示器右側）
        hint_text = self.fonts["tiny"].render(
            "(V切換)", True, self.ui_colors["secondary"]
        )
        hint_x = x + bg_width + 10
        hint_y = y + bg_height // 2 - hint_text.get_height() // 2
        screen.blit(hint_text, (hint_x, hint_y))

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
            "V: 切換攻擊模式",
            "ESC: 暫停",
        ]

        hint_y = self.screen_height - 95  # 調整位置給更多提示留空間
        for i, hint in enumerate(hints):
            hint_text = self.fonts["tiny"].render(
                hint, True, self.ui_colors["secondary"]
            )
            hint_rect = hint_text.get_rect(left=20, top=hint_y + i * 15)
            screen.blit(hint_text, hint_rect)

    def _draw_projectile_type(self, screen: pygame.Surface, player):
        """
        繪製當前投射物類型\n
        \n
        在螢幕右下角顯示當前選擇的投射物類型\n
        \n
        參數:\n
        screen (pygame.Surface): 螢幕表面\n
        player: 玩家物件\n
        """
        if not hasattr(player, "projectile_type"):
            return

        # 根據投射物類型設定顯示內容和顏色
        if player.projectile_type == "fireball":
            type_text = "火焰球"
            type_color = (255, 100, 50)  # 橙紅色
            bg_color = (100, 30, 20)  # 深紅色背景
        elif player.projectile_type == "iceball":
            type_text = "冰凍球"
            type_color = (150, 200, 255)  # 淺藍色
            bg_color = (30, 50, 100)  # 深藍色背景
        else:
            type_text = "未知"
            type_color = (200, 200, 200)  # 灰色
            bg_color = (50, 50, 50)  # 深灰色背景

        # 繪製背景框
        text_width = 120
        text_height = 40
        bg_x = self.screen_width - text_width - 20
        bg_y = self.screen_height - text_height - 20

        bg_rect = pygame.Rect(bg_x, bg_y, text_width, text_height)
        pygame.draw.rect(screen, bg_color, bg_rect)
        pygame.draw.rect(screen, type_color, bg_rect, 2)

        # 繪製投射物類型文字
        projectile_text = self.fonts["small"].render(type_text, True, type_color)
        text_rect = projectile_text.get_rect(center=bg_rect.center)
        screen.blit(projectile_text, text_rect)

        # 繪製切換提示
        hint_text = self.fonts["tiny"].render(
            "V: 切換", True, self.ui_colors["secondary"]
        )
        hint_rect = hint_text.get_rect(centerx=bg_rect.centerx, bottom=bg_y - 5)
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

    def draw_victory_screen(self, screen: pygame.Surface):
        """
        繪製勝利畫面\n
        \n
        顯示遊戲勝利訊息和後續選項\n
        \n
        參數:\n
        screen (pygame.Surface): 要繪製到的螢幕表面\n
        """
        # 半透明金色遮罩，營造勝利的氛圍
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(180)
        overlay.fill((50, 30, 0))  # 暖金色調
        screen.blit(overlay, (0, 0))

        # 勝利標題
        title_text = self.fonts["title"].render(
            "恭喜！遊戲完成！", True, (255, 215, 0)  # 金色
        )
        title_rect = title_text.get_rect(
            center=(self.screen_width // 2, self.screen_height // 2 - 80)
        )
        screen.blit(title_text, title_rect)

        # 恭喜訊息
        congrats_text = self.fonts["medium"].render(
            "你成功擊敗了所有的 Boss！", True, self.ui_colors["primary"]
        )
        congrats_rect = congrats_text.get_rect(
            center=(self.screen_width // 2, self.screen_height // 2 - 20)
        )
        screen.blit(congrats_text, congrats_rect)

        # 操作提示
        restart_text = self.fonts["small"].render(
            "按 SPACE 重新開始遊戲", True, self.ui_colors["secondary"]
        )
        restart_rect = restart_text.get_rect(
            center=(self.screen_width // 2, self.screen_height // 2 + 30)
        )
        screen.blit(restart_text, restart_rect)

        menu_text = self.fonts["small"].render(
            "按 ESC 返回主選單", True, self.ui_colors["secondary"]
        )
        menu_rect = menu_text.get_rect(
            center=(self.screen_width // 2, self.screen_height // 2 + 60)
        )
        screen.blit(menu_text, menu_rect)

        # 繪製一些慶祝效果（簡單的星星）
        import math
        import time

        current_time = time.time()

        for i in range(15):
            # 計算星星的動畫位置
            angle = (current_time * 2 + i * 0.4) % (2 * math.pi)
            radius = 50 + 30 * math.sin(current_time * 3 + i)

            star_x = int(self.screen_width // 2 + radius * math.cos(angle))
            star_y = int(self.screen_height // 2 - 80 + radius * math.sin(angle))

            # 繪製簡單的星星（小圓點）
            pygame.draw.circle(screen, (255, 215, 0), (star_x, star_y), 3)

    def _draw_potion_inventory(self, screen: pygame.Surface, player):
        """
        繪製藥水庫存信息\n
        \n
        在螢幕右上角關卡資訊下方顯示藥水持有數量\n
        """
        # 藥水顯示位置（在關卡資訊下方）
        start_x = self.screen_width - 20
        start_y = 60  # 關卡資訊下方一些距離

        # 藥水資訊配置
        potion_info = [
            {"type": "attack", "name": "攻擊藥水", "key": "1", "color": (255, 200, 50)},
            {"type": "shield", "name": "護盾藥水", "key": "2", "color": (50, 150, 255)},
            {"type": "healing", "name": "治療藥水", "key": "3", "color": (255, 50, 50)},
        ]

        for i, potion in enumerate(potion_info):
            y_pos = start_y + i * 25
            count = player.get_potion_count(potion["type"])

            # 顯示藥水名稱和數量
            text = f"[{potion['key']}] {potion['name']}: {count}"
            rendered_text = self.fonts["small"].render(text, True, potion["color"])
            text_rect = rendered_text.get_rect(right=start_x, y=y_pos)
            screen.blit(rendered_text, text_rect)

            # 在數量為0時顯示灰色
            if count == 0:
                gray_overlay = pygame.Surface(rendered_text.get_size(), pygame.SRCALPHA)
                gray_overlay.fill((128, 128, 128, 100))
                screen.blit(gray_overlay, text_rect)
