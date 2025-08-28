######################載入套件######################
import pygame
from typing import List, Tuple


######################關卡基礎類別######################
class Level:
    """
    單一關卡的基礎類別\n
    \n
    代表遊戲中的一個完整關卡，包含：\n
    1. 關卡的所有靜態元素（平台、背景）\n
    2. 動態元素管理（敵人、陷阱）\n
    3. 關卡完成條件和狀態\n
    4. 視覺效果和渲染\n
    \n
    屬性:\n
    level_number (int): 關卡編號\n
    platforms (List): 平台物件清單\n
    traps (List): 陷阱物件清單\n
    enemies (List): 敵人物件清單\n
    player_start_x, player_start_y (float): 玩家起始位置\n
    level_completion_height (float): 完成關卡所需到達的高度\n
    background_color (Tuple): 背景顏色 RGB 值\n
    \n
    關卡設計原則:\n
    - 垂直向上的攀爬結構\n
    - 由簡單到複雜的難度漸進\n
    - 多樣化的挑戰元素組合\n
    """

    def __init__(
        self,
        level_number: int,
        platforms: List,
        traps: List,
        enemies: List,
        player_start_x: float,
        player_start_y: float,
        level_completion_height: float,
        background_color: Tuple[int, int, int],
    ):
        """
        初始化關卡\n
        \n
        建立關卡的所有基本元素和設定\n
        \n
        參數:\n
        level_number (int): 關卡編號，從 1 開始\n
        platforms (List): 平台物件清單\n
        traps (List): 陷阱物件清單\n
        enemies (List): 敵人物件清單\n
        player_start_x (float): 玩家起始 X 座標\n
        player_start_y (float): 玩家起始 Y 座標\n
        level_completion_height (float): 完成關卡的目標高度\n
        background_color (Tuple): 背景顏色 (R, G, B)\n
        """
        self.level_number = level_number
        self.platforms = platforms
        self.traps = traps
        self.enemies = enemies

        # 玩家起始位置
        self.player_start_x = player_start_x
        self.player_start_y = player_start_y

        # 關卡完成條件
        self.level_completion_height = level_completion_height

        # 視覺設定
        self.background_color = background_color

        # 關卡狀態
        self.is_completed = False
        self.completion_time = 0  # 完成關卡所花的時間

        # 統計資料
        self.enemies_defeated = 0
        self.traps_triggered = 0

        # 自動調整敵人巡邏範圍，避免掉下平台
        self._adjust_enemies_patrol_ranges()

    def _adjust_enemies_patrol_ranges(self):
        """
        調整所有敵人的巡邏範圍\n
        \n
        在關卡初始化時自動檢查每個敵人的巡邏範圍是否安全，\n
        如果可能導致敵人掉下平台就自動縮小範圍\n
        """
        for enemy in self.enemies:
            if hasattr(enemy, "adjust_patrol_range_for_platforms"):
                enemy.adjust_patrol_range_for_platforms(self.platforms)

    def update(self, player):
        """
        更新關卡狀態\n
        \n
        每幀更新關卡中的所有動態元素：\n
        1. 更新所有敵人的 AI 和移動\n
        2. 更新陷阱的動畫和狀態\n
        3. 檢查玩家與各種元素的互動\n
        4. 更新關卡統計資料\n
        \n
        參數:\n
        player: 玩家物件，用於敵人 AI 和互動檢測\n
        """
        # 更新所有敵人
        for enemy in self.enemies[:]:  # 使用副本避免修改列表時出錯
            # 建立包含移動平台的完整平台清單
            all_platforms = self.platforms.copy()

            # 把移動平台也加入平台清單，讓敵人可以站在上面
            from src.traps.moving_platform import MovingPlatform

            for trap in self.traps:
                if isinstance(trap, MovingPlatform):
                    all_platforms.append(trap)

            # 更新敵人，傳入平台資料用於碰撞檢測
            enemy.update(player, all_platforms)

            # 檢查玩家是否與敵人發生接觸（用來激活敵人追蹤）
            if not enemy.has_been_touched:
                player_rect = player.get_collision_rect()
                enemy_rect = enemy.get_collision_rect()
                if player_rect.colliderect(enemy_rect):
                    # 玩家碰到敵人，激活敵人的追蹤模式
                    enemy.has_been_touched = True

            # 檢查敵人是否被玩家攻擊擊敗（只在攻擊剛開始時判定，避免重複傷害）
            if player.attack_just_started and self._check_player_attack_hit(
                player, enemy
            ):
                enemy.take_damage(player.attack_damage)

                # 敵人死亡時從列表移除
                if enemy.health <= 0:
                    self.enemies.remove(enemy)
                    self.enemies_defeated += 1

        # 更新所有陷阱
        for trap in self.traps:
            trap.update()

        # 更新關卡計時器
        if not self.is_completed:
            self.completion_time += 1

    def _check_player_attack_hit(self, player, enemy) -> bool:
        """
        檢查玩家攻擊是否命中敵人\n
        \n
        判斷玩家的攻擊範圍是否與敵人重疊\n
        \n
        參數:\n
        player: 玩家物件\n
        enemy: 敵人物件\n
        \n
        回傳:\n
        bool: 是否命中敵人\n
        """
        player_attack_rect = player.get_attack_rect()
        enemy_rect = enemy.get_collision_rect()
        return player_attack_rect.colliderect(enemy_rect)

    def render(self, screen: pygame.Surface, camera_y: float):
        """
        繪製關卡\n
        \n
        渲染關卡的所有視覺元素，包括背景、平台、陷阱、敵人\n
        \n
        參數:\n
        screen (pygame.Surface): 要繪製到的螢幕表面\n
        camera_y (float): 攝影機的 Y 軸偏移（用於卷軸效果）\n
        \n
        繪製順序:\n
        1. 背景 → 2. 平台 → 3. 陷阱 → 4. 敵人\n
        """
        # 填充背景色
        screen.fill(self.background_color)

        # 繪製背景裝飾（雲朵、遠山等）
        self._draw_background_decorations(screen, camera_y)

        # 繪製所有平台
        for platform in self.platforms:
            platform.render(screen, camera_y)

        # 繪製所有陷阱
        for trap in self.traps:
            trap.render(screen, camera_y)

        # 繪製所有敵人
        for enemy in self.enemies:
            enemy.render(screen, camera_y)

        # 繪製關卡特殊效果
        self._draw_level_effects(screen, camera_y)

    def _draw_background_decorations(self, screen: pygame.Surface, camera_y: float):
        """
        繪製背景裝飾元素\n
        \n
        根據關卡主題繪製背景裝飾，如雲朵、星星等\n
        \n
        參數:\n
        screen (pygame.Surface): 螢幕表面\n
        camera_y (float): 攝影機偏移\n
        """
        screen_height = screen.get_height()

        # 根據關卡編號繪製不同的背景裝飾
        if self.level_number <= 2:
            # 前兩關繪製雲朵
            self._draw_clouds(screen, camera_y)
        elif self.level_number == 3:
            # 第三關繪製工業風格的背景
            self._draw_industrial_background(screen, camera_y)
        elif self.level_number == 4:
            # 第四關繪製夜晚星空
            self._draw_night_sky(screen, camera_y)
        elif self.level_number == 5:
            # 最終關繪製神秘的紫色能量效果
            self._draw_mystical_effects(screen, camera_y)

    def _draw_clouds(self, screen: pygame.Surface, camera_y: float):
        """
        繪製雲朵裝飾\n
        \n
        在天空背景中繪製白雲\n
        """
        cloud_color = (255, 255, 255, 100)  # 半透明白色
        screen_height = screen.get_height()

        # 計算雲朵位置（考慮攝影機移動）
        cloud_positions = [
            (100, 200),
            (300, 150),
            (600, 180),
            (900, 120),
            (150, 400),
            (450, 350),
            (750, 380),
            (1000, 320),
            (80, 600),
            (400, 550),
            (800, 580),
        ]

        for cloud_x, cloud_y in cloud_positions:
            # 根據攝影機位置調整雲朵的螢幕座標
            screen_y = cloud_y - camera_y * 0.3 + screen_height // 2  # 視差效果

            # 只繪製在螢幕範圍內的雲朵
            if -50 < screen_y < screen_height + 50:
                # 用幾個圓形組成雲朵形狀
                pygame.draw.circle(
                    screen, (240, 240, 240), (int(cloud_x), int(screen_y)), 25
                )
                pygame.draw.circle(
                    screen, (240, 240, 240), (int(cloud_x + 20), int(screen_y)), 20
                )
                pygame.draw.circle(
                    screen, (240, 240, 240), (int(cloud_x + 35), int(screen_y + 10)), 18
                )

    def _draw_industrial_background(self, screen: pygame.Surface, camera_y: float):
        """
        繪製工業風格背景\n
        \n
        第三關的工廠背景裝飾\n
        """
        # 繪製遠處的工廠煙囪
        chimney_color = (60, 60, 60)
        screen_height = screen.get_height()

        chimneys = [(200, 500), (800, 450), (1000, 520)]
        for chimney_x, chimney_y in chimneys:
            screen_y = chimney_y - camera_y * 0.2 + screen_height // 2
            if -100 < screen_y < screen_height + 100:
                # 煙囪主體
                pygame.draw.rect(screen, chimney_color, (chimney_x, screen_y, 30, 150))
                # 煙霧效果
                for i in range(3):
                    smoke_y = screen_y - 20 - i * 15
                    smoke_alpha = 100 - i * 30
                    pygame.draw.circle(
                        screen,
                        (200, 200, 200),
                        (chimney_x + 15, int(smoke_y)),
                        8 + i * 2,
                    )

    def _draw_night_sky(self, screen: pygame.Surface, camera_y: float):
        """
        繪製夜空星星\n
        \n
        第四關的夜晚背景\n
        """
        star_color = (255, 255, 200)
        screen_height = screen.get_height()

        # 星星位置（預設的星空圖案）
        stars = [
            (50, 100),
            (150, 80),
            (250, 120),
            (350, 90),
            (450, 110),
            (550, 70),
            (650, 100),
            (750, 85),
            (850, 95),
            (950, 75),
            (1050, 105),
            (1150, 90),
            (80, 300),
            (280, 280),
            (480, 310),
            (680, 290),
            (880, 300),
            (1080, 285),
        ]

        for star_x, star_y in stars:
            screen_y = star_y - camera_y * 0.1 + screen_height // 2
            if -20 < screen_y < screen_height + 20:
                # 繪製閃爍的星星
                pygame.draw.circle(screen, star_color, (int(star_x), int(screen_y)), 2)

    def _draw_mystical_effects(self, screen: pygame.Surface, camera_y: float):
        """
        繪製神秘能量效果\n
        \n
        最終關的特殊視覺效果\n
        """
        # 繪製紫色能量波動
        effect_color = (148, 0, 211, 50)  # 半透明紫色
        screen_height = screen.get_height()

        # 創建能量波動效果（這裡簡化為圓圈）
        energy_centers = [(300, 200), (700, 300), (500, 500)]

        for center_x, center_y in energy_centers:
            screen_y = center_y - camera_y * 0.4 + screen_height // 2
            if -100 < screen_y < screen_height + 100:
                # 繪製多層能量圈
                for radius in [20, 40, 60]:
                    pygame.draw.circle(
                        screen, (148, 0, 211), (int(center_x), int(screen_y)), radius, 2
                    )

    def _draw_level_effects(self, screen: pygame.Surface, camera_y: float):
        """
        繪製關卡特殊效果\n
        \n
        如完成線、提示箭頭等\n
        """
        screen_height = screen.get_height()

        # 繪製完成線（目標高度的視覺指示）
        completion_screen_y = (
            self.level_completion_height - camera_y + screen_height // 2
        )

        if -10 < completion_screen_y < screen_height + 10:
            # 繪製閃爍的完成線
            line_color = (255, 215, 0)  # 金色
            pygame.draw.line(
                screen,
                line_color,
                (0, completion_screen_y),
                (screen.get_width(), completion_screen_y),
                3,
            )

            # 繪製「GOAL」文字
            font = pygame.font.Font(None, 36)
            goal_text = font.render("GOAL!", True, line_color)
            screen.blit(
                goal_text, (screen.get_width() // 2 - 40, completion_screen_y - 25)
            )

    def reset(self):
        """
        重置關卡狀態\n
        \n
        將關卡恢復到初始狀態，用於重新開始遊戲\n
        """
        self.is_completed = False
        self.completion_time = 0
        self.enemies_defeated = 0
        self.traps_triggered = 0

        # 重置所有敵人狀態
        for enemy in self.enemies:
            enemy.reset()

        # 重置所有陷阱狀態
        for trap in self.traps:
            trap.reset()

    def get_completion_stats(self) -> dict:
        """
        取得關卡完成統計\n
        \n
        回傳關卡的完成資料，用於計分和評價\n
        \n
        回傳:\n
        dict: 包含完成時間、擊敗敵人數等統計資料\n
        """
        return {
            "completion_time": self.completion_time,
            "enemies_defeated": self.enemies_defeated,
            "traps_triggered": self.traps_triggered,
            "is_completed": self.is_completed,
            "total_enemies": len(self.enemies) + self.enemies_defeated,
            "total_traps": len(self.traps),
        }
