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
        background_image: str = None,
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
        background_image (str): 背景圖片檔案路徑，可選參數\n
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
        self.background_image_path = background_image
        self.background_image = None
        self.background_scaled = None

        # 載入背景圖片
        if self.background_image_path:
            self._load_background_image()

        # 關卡狀態
        self.is_completed = False
        self.completion_time = 0  # 完成關卡所花的時間

        # 統計資料
        self.enemies_defeated = 0
        self.traps_triggered = 0

        # 保存原始敵人配置用於重置
        # 儲存每個敵人的類型和初始參數，用於重新建立敵人物件
        self._original_enemy_configs = []
        for enemy in enemies:
            enemy_config = self._get_enemy_config(enemy)
            self._original_enemy_configs.append(enemy_config)

        # 自動調整敵人巡邏範圍，避免掉下平台
        self._adjust_enemies_patrol_ranges()

    def _load_background_image(self):
        """
        載入關卡背景圖片\n
        \n
        載入指定的背景圖片檔案，如果載入失敗會印出錯誤訊息並使用純色背景\n
        """
        try:
            import os
            # 檢查檔案是否存在
            if not os.path.exists(self.background_image_path):
                print(f"背景圖片檔案不存在: {self.background_image_path}")
                return
                
            # 載入背景圖片
            self.background_image = pygame.image.load(self.background_image_path).convert()
            print(f"成功載入背景圖片: {self.background_image_path}")
            
        except pygame.error as e:
            print(f"載入背景圖片失敗: {e}")
            print(f"路徑: {self.background_image_path}")
            self.background_image = None
        except Exception as e:
            print(f"載入背景圖片時發生未預期錯誤: {e}")
            self.background_image = None

    def _scale_background_for_screen(self, screen_size):
        """
        根據螢幕大小等比例縮放背景圖片\n
        \n
        使用等比例縮放保持圖片原始比例，避免扭曲變形\n
        背景圖片會被縮放到完全填滿螢幕，多餘部分會被裁切\n
        \n
        參數:\n
        screen_size (Tuple[int, int]): 螢幕尺寸 (寬度, 高度)\n
        """
        if not self.background_image:
            return
            
        try:
            screen_width, screen_height = screen_size
            original_width, original_height = self.background_image.get_size()
            
            # 計算縮放比例，確保圖片完全填滿螢幕
            # 使用較大的縮放比例，讓圖片能夠覆蓋整個螢幕
            scale_x = screen_width / original_width
            scale_y = screen_height / original_height
            scale = max(scale_x, scale_y)  # 使用較大的比例確保填滿螢幕
            
            # 計算縮放後的尺寸（保持等比例）
            target_width = int(original_width * scale)
            target_height = int(original_height * scale)
            
            # 等比例縮放背景圖片
            self.background_scaled = pygame.transform.scale(
                self.background_image, 
                (target_width, target_height)
            )
            
            # 如果縮放後的圖片比螢幕大，計算置中偏移
            self.background_offset_x = (screen_width - target_width) // 2
            self.background_offset_y = (screen_height - target_height) // 2
            
            print(f"背景圖片等比例縮放: {original_width}x{original_height} -> {target_width}x{target_height} (比例: {scale:.2f})")
            
        except Exception as e:
            print(f"縮放背景圖片時發生錯誤: {e}")
            self.background_scaled = None

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

            # 檢查敵人是否攻擊玩家（敵人攻擊冷卻結束且在攻擊範圍內）
            if enemy.attack_cooldown <= 0:
                attack_result = enemy.attack_player(player)
                
                if attack_result["hit"]:
                    # 敵人成功攻擊到玩家，讓玩家受傷
                    player.take_damage(attack_result["damage"])
                    
                    # 重置敵人攻擊冷卻時間
                    enemy.attack_cooldown = enemy.max_attack_cooldown
                    
                    # 處理特殊效果（如擊退）
                    if "knockback" in attack_result.get("special_effects", []):
                        # 計算擊退方向（從敵人到玩家的方向）
                        dx = player.x - enemy.x
                        if dx != 0:
                            knockback_force = 8 if dx > 0 else -8
                            player.velocity_x += knockback_force

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
        1. 背景圖片 → 2. 背景裝飾 → 3. 平台 → 4. 陷阱 → 5. 敵人\n
        """
        # 繪製背景圖片（固定背景，不跟隨攝影機移動）
        self._draw_background_image(screen, camera_y)

        # 繪製背景裝飾（雲朵、遠山等）- 在背景圖片之上，但在遊戲物件之下
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

    def _draw_background_image(self, screen: pygame.Surface, camera_y: float):
        """
        繪製關卡背景圖片\n
        \n
        背景圖片固定在螢幕上，不跟隨攝影機移動\n
        使用等比例縮放，確保圖片不會扭曲變形\n
        \n
        參數:\n
        screen (pygame.Surface): 螢幕表面\n
        camera_y (float): 攝影機偏移（此參數在固定背景中不使用）\n
        """
        if not self.background_image:
            # 如果沒有背景圖片，用純色填充作為保底
            screen.fill(self.background_color)
            return
            
        # 第一次渲染時縮放背景圖片
        if not self.background_scaled:
            self._scale_background_for_screen(screen.get_size())
            
        if not self.background_scaled:
            # 縮放失敗時用純色填充
            screen.fill(self.background_color)
            return
            
        try:
            # 背景圖片固定在螢幕位置，不跟隨攝影機移動
            # 使用計算好的偏移來置中顯示
            background_rect = pygame.Rect(
                getattr(self, 'background_offset_x', 0),  # X 偏移（置中）
                getattr(self, 'background_offset_y', 0),  # Y 偏移（置中）
                self.background_scaled.get_width(),
                self.background_scaled.get_height()
            )
            
            # 繪製固定背景圖片
            screen.blit(self.background_scaled, background_rect)
            
        except Exception as e:
            print(f"繪製背景圖片時發生錯誤: {e}")
            # 發生錯誤時回退到純色背景
            screen.fill(self.background_color)

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
        if self.level_number == 4:
            # 第四關繪製夜晚星空（保留星星）
            self._draw_night_sky(screen, camera_y)
        # 第一二關的雲朵、第三關的工業背景、第五關的能量圓圈已移除

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

    def _get_enemy_config(self, enemy) -> dict:
        """
        取得敵人的配置資料\n
        \n
        擷取敵人的類型和初始參數，用於重新建立敵人物件\n
        \n
        參數:\n
        enemy: 敵人物件\n
        \n
        回傳:\n
        dict: 包含敵人類型和初始參數的字典\n
        """
        # 儲存敵人的類型和基本參數
        config = {
            "type": type(enemy).__name__,
            "module": type(enemy).__module__,
            "x": enemy.start_x if hasattr(enemy, "start_x") else enemy.x,
            "y": enemy.start_y if hasattr(enemy, "start_y") else enemy.y,
            "health": enemy.max_health,
            "attack_damage": enemy.attack_damage,
            "speed": enemy.speed,
        }

        # 如果是基礎敵人，還要儲存巡邏範圍
        if hasattr(enemy, "patrol_range"):
            config["patrol_range"] = enemy.patrol_range

        # 如果是 Boss，儲存 Boss 類型
        if hasattr(enemy, "boss_type"):
            config["boss_type"] = enemy.boss_type

        return config

    def _recreate_enemy_from_config(self, config: dict):
        """
        從配置資料重新建立敵人物件\n
        \n
        根據儲存的配置參數重新建立敵人物件\n
        \n
        參數:\n
        config (dict): 敵人的配置資料\n
        \n
        回傳:\n
        敵人物件\n
        """
        try:
            # 動態導入敵人類別
            module_path = config["module"]
            class_name = config["type"]

            # 導入模組
            import importlib

            module = importlib.import_module(module_path)
            enemy_class = getattr(module, class_name)

            # 根據敵人類型建立物件
            if class_name == "Boss":
                # Boss 需要特殊的初始化參數
                enemy = enemy_class(
                    config["x"], config["y"], boss_type=config.get("boss_type", "basic")
                )
            elif class_name == "BasicEnemy":
                # 基礎敵人需要巡邏範圍參數
                enemy = enemy_class(
                    config["x"],
                    config["y"],
                    patrol_range=config.get("patrol_range", 100),
                )
            else:
                # 其他敵人類型使用標準初始化
                enemy = enemy_class(
                    config["x"],
                    config["y"],
                    health=config["health"],
                    attack_damage=config["attack_damage"],
                    speed=config["speed"],
                )

            return enemy

        except Exception as e:
            print(f"重新建立敵人時發生錯誤：{e}")
            # 如果重建失敗，回退到建立基本敵人
            from src.enemies.basic_enemy import BasicEnemy

            return BasicEnemy(
                config["x"], config["y"], patrol_range=config.get("patrol_range", 100)
            )

    def reset(self):
        """
        重置關卡狀態\n
        \n
        將關卡恢復到初始狀態，重新建立所有敵人物件\n
        """
        self.is_completed = False
        self.completion_time = 0
        self.enemies_defeated = 0
        self.traps_triggered = 0

        # 重新建立所有敵人物件（這樣被殺死的敵人也會復活）
        self.enemies = []
        for enemy_config in self._original_enemy_configs:
            new_enemy = self._recreate_enemy_from_config(enemy_config)
            self.enemies.append(new_enemy)

        # 重新調整敵人巡邏範圍
        self._adjust_enemies_patrol_ranges()

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
