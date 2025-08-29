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

        # 角色選擇圖片快取
        self.character_image_cache = self._load_character_selection_image()

        # 難度選項資訊
        self.difficulty_info = {
            "easy": {
                "name": "簡單模式",
                "description": "到達關卡頂部即可過關",
                "color": (50, 255, 50),  # 綠色
                "details": ["無需擊敗所有敵人", "適合新手玩家", "快速通關體驗"]
            },
            "hard": {
                "name": "困難模式", 
                "description": "必須擊敗所有敵人才能過關",
                "color": (255, 50, 50),  # 紅色
                "details": ["必須擊敗所有敵人", "完整戰鬥體驗", "挑戰性更高"]
            }
        }

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

    def _load_character_selection_image(self):
        """
        載入角色選擇畫面的圖片\n
        \n
        回傳:\n
        pygame.Surface: 快取的角色選擇圖片，載入失敗時回傳 None\n
        """
        try:
            character_image = pygame.image.load("assets/images/角色1.png").convert_alpha()
            return pygame.transform.scale(character_image, (80, 80))  # 預設預覽大小
        except (pygame.error, FileNotFoundError) as e:
            print(f"無法載入角色選擇圖片: {e}")
            return None

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

    def draw_character_selection(self, screen: pygame.Surface, selected_index: int, selected_difficulty: str):
        """
        繪製角色選擇選單\n
        \n
        顯示可選角色和難度選項\n
        \n
        參數:\n
        screen (pygame.Surface): 螢幕表面\n
        selected_index (int): 目前選中的角色索引\n
        selected_difficulty (str): 目前選中的難度\n
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
        title_rect = title_text.get_rect(center=(self.screen_width // 2, 60))
        screen.blit(title_text, title_rect)

        # 操作提示
        hint_text = self.fonts["small"].render(
            "← → 選擇角色，↑ ↓ 選擇難度，按 Enter 開始遊戲", True, self.ui_colors["secondary"]
        )
        hint_rect = hint_text.get_rect(
            center=(self.screen_width // 2, self.screen_height - 30)
        )
        screen.blit(hint_text, hint_rect)

        # 繪製角色選項
        self._draw_character_options(screen, selected_index)
        
        # 繪製難度選擇
        self._draw_difficulty_selection(screen, selected_difficulty)

    def _draw_character_options(self, screen: pygame.Surface, selected_index: int):
        """
        繪製角色選項卡\n
        \n
        顯示每個角色的詳細資訊\n
        """
        # 計算每個角色卡片的位置和大小（稍微調整位置為難度選擇留空間）
        card_width = 280  # 增加卡片寬度避免文字超出邊界
        card_height = 340  # 增加卡片高度容納更多內容
        spacing = 25  # 減少間距適應更寬的卡片
        total_width = (
            len(self.character_info) * card_width
            + (len(self.character_info) - 1) * spacing
        )
        start_x = (self.screen_width - total_width) // 2
        start_y = 120  # 向下移動一點為難度選擇留空間

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

        # 角色預覽（使用快取圖片）
        preview_size = 80
        preview_x = x + (width - preview_size) // 2
        preview_y = y + 20
        preview_rect = pygame.Rect(preview_x, preview_y, preview_size, preview_size)
        
        # 使用快取的角色圖片
        if hasattr(self, 'character_image_cache') and self.character_image_cache:
            screen.blit(self.character_image_cache, (preview_x, preview_y))
        else:
            # 如果沒有快取圖片，使用原本的彩色矩形
            pygame.draw.rect(screen, character["color"], preview_rect)
        
        # 繪製邊框
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

    def _draw_difficulty_selection(self, screen: pygame.Surface, selected_difficulty: str):
        """
        繪製難度選擇區域\n
        \n
        在角色選擇下方顯示難度選項\n
        \n
        參數:\n
        screen (pygame.Surface): 螢幕表面\n
        selected_difficulty (str): 目前選中的難度\n
        """
        # 難度選擇區域位置（調整到更下面的位置）
        section_y = 500  # 向下移動避免重疊
        section_height = 200
        
        # 繪製難度選擇標題
        difficulty_title = self.fonts["large"].render(
            "選擇遊戲難度", True, self.ui_colors["accent"]
        )
        title_rect = difficulty_title.get_rect(center=(self.screen_width // 2, section_y))
        screen.blit(difficulty_title, title_rect)

        # 繪製兩個難度選項（增加寬度和高度避免文字擠壓）
        option_width = 320  # 增加寬度
        option_height = 140  # 增加高度
        spacing = 40  # 減少間距
        total_width = 2 * option_width + spacing
        start_x = (self.screen_width - total_width) // 2
        option_y = section_y + 50

        # 簡單模式
        easy_x = start_x
        self._draw_difficulty_option(
            screen, "easy", easy_x, option_y, option_width, option_height,
            selected_difficulty == "easy"
        )

        # 困難模式
        hard_x = start_x + option_width + spacing
        self._draw_difficulty_option(
            screen, "hard", hard_x, option_y, option_width, option_height,
            selected_difficulty == "hard"
        )

    def _draw_difficulty_option(
        self, screen: pygame.Surface, difficulty: str, x: int, y: int, 
        width: int, height: int, is_selected: bool
    ):
        """
        繪製單個難度選項卡\n
        \n
        參數:\n
        screen (pygame.Surface): 螢幕表面\n
        difficulty (str): 難度類型 ("easy" 或 "hard")\n
        x, y (int): 選項卡位置\n
        width, height (int): 選項卡大小\n
        is_selected (bool): 是否被選中\n
        """
        difficulty_data = self.difficulty_info[difficulty]
        
        # 選項卡背景顏色
        if is_selected:
            bg_color = (60, 60, 60)
            border_color = difficulty_data["color"]
            border_width = int(4 * self.pulse_effect)
        else:
            bg_color = (40, 40, 40)
            border_color = (80, 80, 80)
            border_width = 2

        # 繪製選項卡背景
        option_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(screen, bg_color, option_rect)
        pygame.draw.rect(screen, border_color, option_rect, border_width)

        # 難度名稱
        name_text = self.fonts["medium"].render(
            difficulty_data["name"], True, difficulty_data["color"]
        )
        name_rect = name_text.get_rect(center=(x + width // 2, y + 25))
        screen.blit(name_text, name_rect)

        # 難度描述 - 使用更小的字體避免超出邊界
        desc_text = self.fonts["tiny"].render(
            difficulty_data["description"], True, self.ui_colors["secondary"]
        )
        desc_rect = desc_text.get_rect(center=(x + width // 2, y + 55))
        screen.blit(desc_text, desc_rect)

        # 詳細說明 - 調整位置和字體大小
        details_start_y = y + 80
        for i, detail in enumerate(difficulty_data["details"]):
            # 使用 tiny 字體並確保文字適合框內
            detail_text = self.fonts["tiny"].render(
                f"• {detail}", True, self.ui_colors["primary"]
            )
            # 確保文字不超出選項卡寬度
            detail_rect = detail_text.get_rect(
                centerx=x + width // 2, y=details_start_y + i * 16
            )
            # 如果文字太寬，需要左對齊並在框內顯示
            if detail_rect.width > width - 20:
                detail_rect.left = x + 10
            screen.blit(detail_text, detail_rect)

    def draw_game_ui(self, screen: pygame.Surface, player, level_manager):
        """
        繪製遊戲中的 HUD 介面\n
        \n
        顯示玩家狀態、關卡資訊、剩餘敵人數量等重要資料\n
        \n
        參數:\n
        screen (pygame.Surface): 螢幕表面\n
        player: 玩家物件\n
        level_manager: 關卡管理器物件\n
        """
        # 繪製玩家血量條和攻擊模式指示器，並取得下一個可用的Y位置
        next_y = self._draw_player_health(screen, player)

        # 繪製關卡資訊（包含剩餘敵人數量）
        self._draw_level_info(screen, level_manager)

        # 繪製藥水庫存（在攻擊模式指示器下方）
        self._draw_potion_inventory(screen, player, next_y)

        # 繪製操作提示
        self._draw_controls_hint(screen)

    def _draw_player_health(self, screen: pygame.Surface, player):
        """
        繪製玩家血量條、護盾和狀態效果\n
        \n
        在螢幕左上角顯示玩家的血量狀態、護盾值和攻擊模式\n
        \n
        回傳:\n
        int: 下一個可用的 Y 座標位置\n
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

        # 在血條下方顯示攻擊模式，並取得下一個可用位置
        next_y = self._draw_attack_mode_indicator(screen, player, bar_x, attack_boost_y)

        return next_y

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
        \n
        回傳:\n
        int: 下一個可用的 Y 座標位置\n
        """
        # 檢查玩家是否有投射物類型屬性
        if not hasattr(player, "projectile_type"):
            return y

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

        # 回傳下一個可用的Y位置（攻擊模式指示器下方加一些間距）
        return y + bg_height + 10

    def _draw_level_info(self, screen: pygame.Surface, level_manager):
        """
        繪製關卡資訊\n
        \n
        在螢幕右上角顯示當前關卡、剩餘敵人數量和難度\n
        """
        # 取得關卡資訊
        level_info = level_manager.get_level_info()
        level_number = level_info["number"]
        remaining_enemies = level_info["remaining_enemies"]
        difficulty = level_info.get("difficulty", "easy")

        # 關卡編號
        level_text = self.fonts["medium"].render(
            f"第 {level_number} 關", True, self.ui_colors["accent"]
        )
        level_rect = level_text.get_rect(right=self.screen_width - 20, top=20)
        screen.blit(level_text, level_rect)

        # 難度顯示 - 在關卡編號旁邊
        difficulty_name = "簡單" if difficulty == "easy" else "困難"
        difficulty_color = (50, 255, 50) if difficulty == "easy" else (255, 50, 50)
        difficulty_text = self.fonts["small"].render(
            f"[{difficulty_name}]", True, difficulty_color
        )
        difficulty_rect = difficulty_text.get_rect(
            right=level_rect.left - 10, centery=level_rect.centery
        )
        screen.blit(difficulty_text, difficulty_rect)

        # 剩餘敵人數量 - 顯示在關卡編號下方
        enemy_color = (
            self.ui_colors["danger"]
            if remaining_enemies > 0
            else self.ui_colors["success"]
        )
        enemy_text = self.fonts["small"].render(
            f"剩餘敵人: {remaining_enemies}", True, enemy_color
        )
        enemy_rect = enemy_text.get_rect(
            right=self.screen_width - 20, top=level_rect.bottom + 5
        )
        
        # 為剩餘敵人數量文字添加背景色，提高可讀性
        enemy_bg_padding = 4
        enemy_bg_rect = pygame.Rect(
            enemy_rect.left - enemy_bg_padding,
            enemy_rect.top - enemy_bg_padding,
            enemy_rect.width + enemy_bg_padding * 2,
            enemy_rect.height + enemy_bg_padding * 2
        )
        # 使用半透明黑色背景
        enemy_bg_surface = pygame.Surface((enemy_bg_rect.width, enemy_bg_rect.height), pygame.SRCALPHA)
        enemy_bg_surface.fill((0, 0, 0, 150))  # 半透明黑色
        screen.blit(enemy_bg_surface, (enemy_bg_rect.x, enemy_bg_rect.y))
        
        screen.blit(enemy_text, enemy_rect)

        # 根據難度和關卡顯示過關條件提示
        condition_y = enemy_rect.bottom + 3
        
        # 針對第六關（Boss戰）特別處理文字顯示
        if level_number == 6:
            if difficulty == "easy":
                if remaining_enemies == 0:
                    clear_text = self.fonts["tiny"].render(
                        "可以前往關卡頂部過關！", True, self.ui_colors["success"]
                    )
                else:
                    clear_text = self.fonts["tiny"].render(
                        "擊敗Boss通關", True, self.ui_colors["info"]
                    )
            else:  # hard mode
                if remaining_enemies == 0:
                    clear_text = self.fonts["tiny"].render(
                        "可以前往關卡頂部過關！", True, self.ui_colors["success"]
                    )
                else:
                    clear_text = self.fonts["tiny"].render(
                        "擊敗Boss和小怪通關", True, self.ui_colors["warning"]
                    )
        else:
            # 其他關卡使用原本的文字
            if difficulty == "easy":
                if remaining_enemies == 0:
                    clear_text = self.fonts["tiny"].render(
                        "可以前往關卡頂部過關！", True, self.ui_colors["success"]
                    )
                else:
                    clear_text = self.fonts["tiny"].render(
                        "前往關卡頂部即可過關", True, self.ui_colors["info"]
                    )
            else:  # hard mode
                if remaining_enemies == 0:
                    clear_text = self.fonts["tiny"].render(
                        "可以前往關卡頂部過關！", True, self.ui_colors["success"]
                    )
                else:
                    clear_text = self.fonts["tiny"].render(
                        "需擊敗所有敵人才能過關", True, self.ui_colors["warning"]
                    )

        clear_rect = clear_text.get_rect(
            right=self.screen_width - 20, top=condition_y
        )
        
        # 為過關條件文字添加背景色，提高可讀性
        bg_padding = 4
        bg_rect = pygame.Rect(
            clear_rect.left - bg_padding,
            clear_rect.top - bg_padding,
            clear_rect.width + bg_padding * 2,
            clear_rect.height + bg_padding * 2
        )
        # 使用半透明黑色背景
        bg_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        bg_surface.fill((0, 0, 0, 150))  # 半透明黑色
        screen.blit(bg_surface, (bg_rect.x, bg_rect.y))
        
        screen.blit(clear_text, clear_rect)

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
            "按 SPACE 關閉遊戲", True, self.ui_colors["secondary"]
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

    def _draw_potion_inventory(self, screen: pygame.Surface, player, start_y: int):
        """
        繪製藥水庫存信息\n
        \n
        在攻擊模式指示器下方顯示藥水持有數量\n
        \n
        參數:\n
        screen (pygame.Surface): 螢幕表面\n
        player: 玩家物件\n
        start_y (int): 開始繪製的 Y 座標位置\n
        """
        # 藥水顯示位置（在攻擊模式指示器下方）
        start_x = 20  # 與攻擊模式指示器對齊

        # 藥水資訊配置
        potion_info = [
            {"type": "attack", "name": "攻擊藥水", "key": "1", "color": (255, 200, 50)},
            {"type": "shield", "name": "護盾藥水", "key": "2", "color": (50, 150, 255)},
            {"type": "healing", "name": "治療藥水", "key": "3", "color": (255, 50, 50)},
        ]

        for i, potion in enumerate(potion_info):
            y_pos = start_y + i * 26  # 進一步增加行間距確保背景框不重疊
            count = player.get_potion_count(potion["type"])

            # 顯示藥水名稱和數量
            text = f"[{potion['key']}] {potion['name']}: {count}"
            rendered_text = self.fonts["tiny"].render(text, True, potion["color"])
            text_rect = rendered_text.get_rect(left=start_x, y=y_pos)
            
            # 為藥水文字添加背景色，提高可讀性
            potion_bg_padding = 3  # 稍微增加內邊距讓背景更明顯
            potion_bg_rect = pygame.Rect(
                text_rect.left - potion_bg_padding,
                text_rect.top - potion_bg_padding,
                text_rect.width + potion_bg_padding * 2,
                text_rect.height + potion_bg_padding * 2
            )
            # 使用半透明黑色背景
            potion_bg_surface = pygame.Surface((potion_bg_rect.width, potion_bg_rect.height), pygame.SRCALPHA)
            potion_bg_surface.fill((0, 0, 0, 120))  # 稍微透明一點，避免遮擋過多
            screen.blit(potion_bg_surface, (potion_bg_rect.x, potion_bg_rect.y))
            
            screen.blit(rendered_text, text_rect)

            # 在數量為0時顯示灰色覆蓋
            if count == 0:
                gray_overlay = pygame.Surface(rendered_text.get_size(), pygame.SRCALPHA)
                gray_overlay.fill((128, 128, 128, 100))
                screen.blit(gray_overlay, text_rect)
