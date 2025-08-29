######################載入套件######################
import pygame
import random
import math
from src.enemies.base_enemy import BaseEnemy


######################Boss 敵人基礎類別######################
class Boss(BaseEnemy):
    """
    Boss 級敵人基礎類別\n
    \n
    比普通敵人更強大的 Boss 級敵人：\n
    1. 更多血量和攻擊力\n
    2. 多階段戰鬥模式\n
    3. 特殊技能和範圍攻擊\n
    4. 小兵召喚能力\n
    \n
    新增屬性:\n
    phase (int): 當前戰鬥階段\n
    special_skills (list): 可用的特殊技能\n
    skill_cooldowns (dict): 技能冷卻時間\n
    """

    def __init__(self, x, y, boss_type="basic"):
        """
        初始化 Boss 敵人\n
        \n
        參數:\n
        x (int): 初始 x 位置\n
        y (int): 初始 y 位置\n
        boss_type (str): Boss 類型\n
        """
        # 呼叫父類初始化，使用 Boss 級的屬性
        super().__init__(x, y, health=300, attack_damage=25, speed=1.5)

        # Boss 尺寸（比普通敵人大）
        self.width = 80
        self.height = 80
        self.boss_type = boss_type
        self.detection_range = 200

        # 戰鬥階段系統
        self.phase = 1
        self.max_phases = 3
        self.phase_health_thresholds = [0.7, 0.3]  # 70% 和 30% 血量時進入下個階段

        # 特殊技能系統
        self.special_skills = ["area_attack", "shockwave"]
        self.skill_cooldowns = {
            "area_attack": 0,
            "shockwave": 0,
            "charge_attack": 0,
        }

        # Boss 專屬狀態
        self.is_casting_skill = False
        self.cast_timer = 0
        self.current_skill = None

        # 視覺效果系統
        self.visual_effects = {
            "basic_attack": {"active": False, "timer": 0, "type": "slash"},
            "area_attack": {"active": False, "timer": 0, "type": "circle_explosion"},
            "shockwave": {"active": False, "timer": 0, "type": "wave"},
            "charge_attack": {"active": False, "timer": 0, "type": "lightning_trail"}
        }

        # 視覺效果
        self.boss_color = (150, 0, 0)  # 深紅色
        self.phase_colors = [
            (150, 0, 0),  # 階段1：深紅
            (200, 50, 0),  # 階段2：橙紅
            (255, 100, 0),  # 階段3：亮橙
        ]

        # 攻擊模式
        self.attack_patterns = {
            1: ["basic_attack", "area_attack"],
            2: ["basic_attack", "area_attack"],
            3: [
                "basic_attack",
                "area_attack",
                "shockwave",
                "charge_attack",
            ],
        }

        # 移動模式
        self.movement_timer = 0
        self.movement_pattern = "patrol"  # patrol, chase, retreat, cast

        # Boss圖片快取系統
        self.boss_image_cache = self._load_boss_images()

    def _load_boss_images(self):
        """
        載入Boss各階段圖片到快取\n
        \n
        回傳:\n
        dict: 包含各階段原始和翻轉版本的圖片快取\n
        """
        boss_files = {
            1: "assets/images/boss.png",
            2: "assets/images/boss2.png", 
            3: "assets/images/boss3.png"
        }
        
        cache = {}
        for phase, file_path in boss_files.items():
            try:
                boss_image = pygame.image.load(file_path).convert_alpha()
                boss_image = pygame.transform.scale(boss_image, (self.width, self.height))
                
                cache[phase] = {
                    "normal": boss_image,
                    "flipped": pygame.transform.flip(boss_image, True, False)
                }
            except (pygame.error, FileNotFoundError) as e:
                print(f"無法載入Boss圖片 {file_path}: {e}")
                cache[phase] = None
        
        return cache

    def update(self, player, platforms=None):
        """
        更新 Boss 狀態\n
        \n
        包含 AI 邏輯、技能冷卻、階段轉換等\n
        \n
        參數:\n
        player: 玩家物件\n
        platforms (list): 平台列表，用於碰撞檢測\n
        """
        if self.is_dead:
            self._update_death_animation()
            return

        # 更新基本屬性（必須先呼叫，包含物理更新）
        self._update_base_properties()

        # 更新技能冷卻時間
        self._update_skill_cooldowns()

        # 檢查階段轉換
        self._check_phase_transition()

        # 更新 AI 狀態
        if not self.is_casting_skill and not self.is_stunned:
            self._update_ai_logic(player)

        # 處理技能施放
        if self.is_casting_skill:
            self._update_skill_casting(player)

        # 應用物理效果（重力、碰撞檢測等）
        self._apply_physics(platforms)

        # 更新動畫
        self._update_animation()
        
        # 更新視覺效果
        self._update_visual_effects()

    def _update_skill_cooldowns(self):
        """
        更新所有技能的冷卻時間\n
        """
        for skill in self.skill_cooldowns:
            if self.skill_cooldowns[skill] > 0:
                self.skill_cooldowns[skill] -= 1

    def _check_phase_transition(self):
        """
        檢查是否需要進入下一個戰鬥階段\n
        """
        health_ratio = self.health / self.max_health

        # 檢查是否達到階段轉換條件
        if self.phase < self.max_phases:
            threshold = self.phase_health_thresholds[self.phase - 1]
            if health_ratio <= threshold:
                self._enter_next_phase()

    def _enter_next_phase(self):
        """
        進入下一個戰鬥階段\n
        \n
        增強 Boss 的能力並解鎖新技能\n
        """
        self.phase += 1

        # 階段強化效果
        if self.phase == 2:
            self.attack_damage += 10
            self.speed += 0.5
            self.detection_range += 50
        elif self.phase == 3:
            self.attack_damage += 15
            self.speed += 0.5
            self.detection_range += 50
            # 最終階段：降低技能冷卻時間
            for skill in self.skill_cooldowns:
                self.skill_cooldowns[skill] = max(0, self.skill_cooldowns[skill] // 2)

        # 更新顏色
        if self.phase <= len(self.phase_colors):
            self.boss_color = self.phase_colors[self.phase - 1]

    def _update_ai_logic(self, player):
        """
        更新 Boss AI 邏輯\n
        \n
        Boss 有更複雜的 AI 行為模式，可以在整個關卡中自由移動\n
        \n
        參數:\n
        player: 玩家物件\n
        """
        distance_to_player = abs(player.x - self.x) + abs(player.y - self.y)

        # 決定行為模式
        if distance_to_player > self.detection_range:
            self.state = "patrol"
        elif distance_to_player < 50:
            # 近距離：考慮使用技能
            if self._should_use_skill():
                self._select_and_cast_skill(player)
            else:
                self.state = "attack"
        else:
            self.state = "chase"

        # 執行對應的行為
        if self.state == "patrol":
            self._enhanced_patrol_behavior()
        elif self.state == "chase":
            self._enhanced_chase_behavior(player)
        elif self.state == "attack":
            self._attack_behavior(player)

    def _enhanced_patrol_behavior(self):
        """
        增強的 Boss 巡邏行為\n
        \n
        Boss 在整個關卡範圍內巡邏，不受傳統巡邏範圍限制\n
        """
        # Boss 可以在整個關卡水平範圍內巡邏（0-1200）
        boss_speed = self.speed * 0.4
        
        # 巡邏方向管理
        if not hasattr(self, 'patrol_target_x'):
            self.patrol_target_x = random.randint(100, 1100)  # 隨機巡邏目標
            self.patrol_change_timer = random.randint(180, 300)  # 3-5秒後改變目標
        
        # 朝目標移動
        dx = self.patrol_target_x - self.x
        if abs(dx) > 20:
            if dx > 0:
                self.velocity_x = boss_speed
                self.facing_direction = 1
            else:
                self.velocity_x = -boss_speed
                self.facing_direction = -1
        else:
            self.velocity_x = 0
            
        # 更新巡邏目標
        self.patrol_change_timer -= 1
        if self.patrol_change_timer <= 0:
            self.patrol_target_x = random.randint(100, 1100)
            self.patrol_change_timer = random.randint(180, 300)
            
        # 如果卡在邊界，調整目標
        if self.x <= 50:
            self.patrol_target_x = random.randint(200, 600)
        elif self.x >= 1150:
            self.patrol_target_x = random.randint(600, 1000)

    def _enhanced_chase_behavior(self, player):
        """
        增強的 Boss 追蹤行為\n
        \n
        Boss 積極追蹤玩家，可以跳躍到不同平台\n
        \n
        參數:\n
        player: 玩家物件\n
        """
        # Boss 追蹤速度根據階段調整
        chase_speed = self.speed * (0.8 + 0.15 * self.phase)

        # 計算到玩家的距離
        dx = player.x - self.x
        dy = player.y - self.y

        # 水平追蹤
        if abs(dx) > 20:  # 避免過度微調
            if dx > 0:
                self.velocity_x = chase_speed
                self.facing_direction = 1
            else:
                self.velocity_x = -chase_speed  
                self.facing_direction = -1
        else:
            self.velocity_x = 0

        # 垂直追蹤（智能跳躍）
        if self.is_on_ground and dy < -30 and abs(dx) < 150:  # 玩家在上方且不太遠
            # Boss 會跳躍追蹤玩家
            if random.random() < 0.03:  # 3% 機率跳躍，避免過度跳躍
                self.velocity_y = -12  # 強力跳躍
                
        # 如果玩家在下方，Boss 會考慮跳下去（但有條件）
        elif self.is_on_ground and dy > 50 and abs(dx) < 100:
            if random.random() < 0.02:  # 2% 機率跳下，更謹慎
                # 確保不會跳得太遠離地面
                if self.y < 650:  # 不要從太高的地方跳下
                    self.velocity_x = dx / abs(dx) * chase_speed * 1.5  # 跳躍時增加水平速度

    def _attack_behavior(self, player):
        """
        Boss 攻擊行為\n
        \n
        Boss 的基礎攻擊行為，包含前搖和後搖\n
        \n
        參數:\n
        player: 玩家物件\n
        """
        # Boss 攻擊時會停止移動
        self.velocity_x = 0

        # 面向玩家
        if player.x > self.x:
            self.facing_direction = 1
        else:
            self.facing_direction = -1

        # 如果攻擊冷卻結束，執行攻擊
        if self.attack_cooldown <= 0:
            attack_result = self.attack_player(player)
            self.attack_cooldown = self.max_attack_cooldown
            
            # 啟動基礎攻擊視覺效果
            self.visual_effects["basic_attack"]["active"] = True
            self.visual_effects["basic_attack"]["timer"] = 20  # 持續時間

            # 攻擊後稍微後退
            self.velocity_x = -self.facing_direction * self.speed * 0.5

    def _should_use_skill(self) -> bool:
        """
        判斷是否應該使用特殊技能\n
        \n
        回傳:\n
        bool: 是否使用技能\n
        """
        # 根據階段和機率決定
        skill_chance = 0.02 * self.phase  # 每個階段增加 2% 機率

        # 檢查是否有技能可用
        available_skills = [
            skill
            for skill in self.attack_patterns[self.phase]
            if self.skill_cooldowns.get(skill, 0) == 0 and skill != "basic_attack"
        ]

        return len(available_skills) > 0 and random.random() < skill_chance

    def _select_and_cast_skill(self, player):
        """
        選擇並施放技能\n
        \n
        參數:\n
        player: 玩家物件\n
        """
        available_skills = [
            skill
            for skill in self.attack_patterns[self.phase]
            if self.skill_cooldowns.get(skill, 0) == 0 and skill != "basic_attack"
        ]

        if available_skills:
            selected_skill = random.choice(available_skills)
            self._start_skill_cast(selected_skill, player)

    def _start_skill_cast(self, skill_name: str, player):
        """
        開始施放技能\n
        \n
        參數:\n
        skill_name (str): 技能名稱\n
        player: 玩家物件\n
        """
        self.is_casting_skill = True
        self.current_skill = skill_name
        self.velocity_x = 0  # 施法時停止移動

        # 設定施法時間
        cast_times = {
            "area_attack": 60,  # 1秒
            "shockwave": 90,  # 1.5秒
            "charge_attack": 30,  # 0.5秒
        }

        self.cast_timer = cast_times.get(skill_name, 60)

    def _update_skill_casting(self, player):
        """
        更新技能施放狀態\n
        \n
        參數:\n
        player: 玩家物件\n
        """
        self.cast_timer -= 1

        if self.cast_timer <= 0:
            # 執行技能效果
            self._execute_skill(self.current_skill, player)

            # 重置狀態
            self.is_casting_skill = False
            self.current_skill = None

    def _execute_skill(self, skill_name: str, player):
        """
        執行技能效果\n
        \n
        參數:\n
        skill_name (str): 技能名稱\n
        player: 玩家物件\n
        """
        if skill_name == "area_attack":
            self._area_attack(player)
        elif skill_name == "shockwave":
            self._shockwave_attack(player)
        elif skill_name == "charge_attack":
            self._charge_attack(player)

        # 設定技能冷卻時間
        cooldown_times = {
            "area_attack": 300,  # 5秒
            "shockwave": 480,  # 8秒
            "charge_attack": 240,  # 4秒
        }

        self.skill_cooldowns[skill_name] = cooldown_times.get(skill_name, 300)

    def _area_attack(self, player):
        """
        範圍攻擊技能\n
        \n
        對周圍大範圍造成傷害\n
        \n
        參數:\n
        player: 玩家物件\n
        """
        attack_range = 120
        damage = self.attack_damage + 15

        # 檢查玩家是否在範圍內
        distance = math.sqrt((player.x - self.x) ** 2 + (player.y - self.y) ** 2)
        if distance <= attack_range:
            # 對玩家造成傷害（由主遊戲邏輯處理）
            self.area_attack_active = True
            self.area_attack_damage = damage
            self.area_attack_range = attack_range
        else:
            self.area_attack_active = False

        # 啟動範圍攻擊視覺效果
        self.visual_effects["area_attack"]["active"] = True
        self.visual_effects["area_attack"]["timer"] = 60  # 持續 1 秒

    def _shockwave_attack(self, player):
        """
        震波攻擊技能\n
        \n
        向玩家方向發射震波\n
        \n
        參數:\n
        player: 玩家物件\n
        """
        # 計算玩家方向
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.sqrt(dx * dx + dy * dy)

        if distance > 0:
            # 正規化方向向量
            dx /= distance
            dy /= distance

            # 創建震波效果（簡化實現）
            self.shockwave_active = True
            self.shockwave_direction = (dx, dy)
            self.shockwave_damage = self.attack_damage + 20
            
            # 啟動震波攻擊視覺效果
            self.visual_effects["shockwave"]["active"] = True
            self.visual_effects["shockwave"]["timer"] = 90  # 持續 1.5 秒
        else:
            self.shockwave_active = False

    def _charge_attack(self, player):
        """
        衝刺攻擊技能\n
        \n
        向玩家位置快速衝刺\n
        \n
        參數:\n
        player: 玩家物件\n
        """
        # 計算衝刺方向
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.sqrt(dx * dx + dy * dy)

        if distance > 0:
            # 設定衝刺速度
            charge_speed = 8
            self.velocity_x = (dx / distance) * charge_speed
            # Boss 不會垂直衝刺，避免卡在空中

            # 設定衝刺狀態
            self.charge_attack_active = True
            self.charge_attack_damage = self.attack_damage + 25
            
            # 啟動衝刺攻擊視覺效果
            self.visual_effects["charge_attack"]["active"] = True
            self.visual_effects["charge_attack"]["timer"] = 45  # 持續 0.75 秒
        else:
            self.charge_attack_active = False

    def _update_visual_effects(self):
        """
        更新所有視覺效果的計時器\n
        """
        for effect_name in self.visual_effects:
            if self.visual_effects[effect_name]["active"]:
                self.visual_effects[effect_name]["timer"] -= 1
                
                # 當計時器歸零時停用效果
                if self.visual_effects[effect_name]["timer"] <= 0:
                    self.visual_effects[effect_name]["active"] = False

    def update_ai(self, player, platforms=None):
        """
        Boss AI 更新（實現抽象方法）\n
        \n
        此方法在 update 中已被重寫，這裡提供基本實現\n
        \n
        參數:\n
        player: 玩家物件\n
        """
        # Boss 的 AI 邏輯已在 _update_ai_logic 中實現
        self._update_ai_logic(player)

    def attack_player(self, player) -> dict:
        """
        Boss 攻擊玩家（實現抽象方法）\n
        \n
        執行對玩家的攻擊，包含基礎攻擊和特殊技能\n
        \n
        參數:\n
        player: 玩家物件\n
        \n
        回傳:\n
        dict: 攻擊結果資訊\n
        """
        attack_info = {
            "damage": self.attack_damage,
            "hit": False,
            "special_effects": [],
        }

        # 使用更精確的碰撞檢測（矩形碰撞）
        boss_rect = self.get_collision_rect()
        player_rect = player.get_collision_rect()
        
        # 擴展Boss攻擊範圍（向面對方向延伸）
        attack_range_x = 60
        attack_range_y = 40
        
        # 根據面對方向調整攻擊範圍
        if self.facing_direction == 1:  # 面向右
            attack_rect = pygame.Rect(
                boss_rect.x, 
                boss_rect.y - attack_range_y//2, 
                boss_rect.width + attack_range_x, 
                boss_rect.height + attack_range_y
            )
        else:  # 面向左
            attack_rect = pygame.Rect(
                boss_rect.x - attack_range_x, 
                boss_rect.y - attack_range_y//2, 
                boss_rect.width + attack_range_x, 
                boss_rect.height + attack_range_y
            )
        
        # 檢查攻擊範圍內是否有玩家
        if attack_rect.colliderect(player_rect):
            attack_info["hit"] = True

            # 根據當前技能狀態增加特殊效果
            if hasattr(self, "area_attack_active") and self.area_attack_active:
                attack_info["damage"] += 15
                attack_info["special_effects"].append("area_damage")

            if hasattr(self, "charge_attack_active") and self.charge_attack_active:
                attack_info["damage"] += 25
                attack_info["special_effects"].append("knockback")

        return attack_info

    def render(self, screen: pygame.Surface, camera_y: float):
        """
        繪製 Boss（實現抽象方法）\n
        \n
        參數:\n
        screen: pygame 畫面物件\n
        camera_y: 攝影機 y 偏移\n
        """
        # 直接呼叫已實現的 draw 方法
        self.draw(screen, 0, camera_y)

    def draw(self, screen, camera_x=0, camera_y=0):
        """
        繪製 Boss\n
        \n
        包含階段效果和技能視覺效果\n
        \n
        參數:\n
        screen: pygame 畫面物件\n
        camera_x (int): 攝影機 x 偏移\n
        camera_y (int): 攝影機 y 偏移\n
        """
        # 計算正確的螢幕座標（與其他遊戲物件一致）
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y + screen.get_height() // 2

        # 檢查是否在螢幕範圍內
        if (
            screen_x < -100
            or screen_x > screen.get_width() + 100
            or screen_y < -100
            or screen_y > screen.get_height() + 100
        ):
            return

        # 繪製技能效果
        self._draw_skill_effects(screen, camera_x, camera_y)

        # 繪製 Boss 主體（使用快取圖片）
        if hasattr(self, 'boss_image_cache') and self.boss_image_cache.get(self.phase):
            # 選擇正確的圖片方向
            if hasattr(self, 'facing_direction') and self.facing_direction == -1:
                boss_image = self.boss_image_cache[self.phase]["flipped"].copy()
            else:
                boss_image = self.boss_image_cache[self.phase]["normal"].copy()
            
            # 施法時的視覺效果
            if self.is_casting_skill:
                flash_intensity = abs(math.sin(pygame.time.get_ticks() * 0.02)) * 100
                flash_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                flash_surface.fill((int(flash_intensity), int(flash_intensity), int(flash_intensity), 50))
                boss_image.blit(flash_surface, (0, 0))
            
            # 繪製Boss圖片
            screen.blit(boss_image, (screen_x, screen_y))
        else:
            # 如果沒有快取圖片，使用原本的矩形繪製
            boss_color = self.boss_color
            
            # 施法時的視覺效果
            if self.is_casting_skill:
                # 閃爍效果
                flash_intensity = abs(math.sin(pygame.time.get_ticks() * 0.02)) * 100
                boss_color = tuple(min(255, c + flash_intensity) for c in boss_color)

            # 繪製 Boss 外框（更粗的邊框）
            pygame.draw.rect(
                screen,
                (255, 255, 255),
                (screen_x - 2, screen_y - 2, self.width + 4, self.height + 4),
            )

            # 繪製 Boss 主體
            pygame.draw.rect(
                screen, boss_color, (screen_x, screen_y, self.width, self.height)
            )

        # 繪製階段標記
        self._draw_phase_indicators(screen, screen_x, screen_y)

        # 繪製血量條（比普通敵人大）
        self._draw_boss_health_bar(screen, screen_x, screen_y)

    def _draw_skill_effects(self, screen, camera_x, camera_y):
        """
        繪製技能特效\n
        \n
        參數:\n
        screen: pygame 畫面物件\n
        camera_x (int): 攝影機 x 偏移\n
        camera_y (int): 攝影機 y 偏移\n
        """
        # 計算 Boss 中心的螢幕座標
        center_x = self.x + self.width // 2 - camera_x
        center_y = self.y + self.height // 2 - camera_y + screen.get_height() // 2

        # 基礎攻擊效果：劍氣斬擊
        if self.visual_effects["basic_attack"]["active"]:
            timer = self.visual_effects["basic_attack"]["timer"]
            max_timer = 20
            
            # 劍氣效果，根據面向方向
            slash_length = 80
            slash_width = 8
            progress = (max_timer - timer) / max_timer
            
            # 計算劍氣位置
            if self.facing_direction == 1:
                start_x = center_x + 20
                end_x = center_x + 20 + slash_length * progress
            else:
                start_x = center_x - 20
                end_x = center_x - 20 - slash_length * progress
                
            start_y = center_y - 30
            end_y = center_y + 30
            
            # 繪製劍氣斬擊（黃白色）
            alpha = int(255 * (timer / max_timer))
            slash_surface = pygame.Surface((abs(end_x - start_x) + slash_width, 60), pygame.SRCALPHA)
            pygame.draw.line(slash_surface, (255, 255, 150, alpha), 
                           (slash_width//2, 0), (abs(end_x - start_x), 60), slash_width)
            screen.blit(slash_surface, (min(start_x, end_x) - slash_width//2, start_y))

        # 範圍攻擊效果：多重爆炸圓環
        if self.visual_effects["area_attack"]["active"]:
            timer = self.visual_effects["area_attack"]["timer"]
            max_timer = 60
            progress = (max_timer - timer) / max_timer
            
            # 繪製多重爆炸圓環
            for i in range(3):
                ring_progress = max(0, progress - i * 0.2)
                if ring_progress > 0:
                    ring_radius = int(30 + ring_progress * 90)
                    ring_alpha = int(150 * (1 - ring_progress) * (timer / max_timer))
                    
                    # 創建半透明表面
                    ring_surface = pygame.Surface((ring_radius * 2, ring_radius * 2), pygame.SRCALPHA)
                    ring_color = [255, 100 - i * 30, 0, ring_alpha]  # 從橙色漸變到紅色
                    
                    pygame.draw.circle(ring_surface, ring_color, (ring_radius, ring_radius), ring_radius, 5)
                    screen.blit(ring_surface, (center_x - ring_radius, center_y - ring_radius))

        # 震波攻擊效果：電磁波動
        if self.visual_effects["shockwave"]["active"] and hasattr(self, "shockwave_direction"):
            timer = self.visual_effects["shockwave"]["timer"]
            max_timer = 90
            progress = (max_timer - timer) / max_timer
            
            # 計算震波傳播距離
            wave_distance = progress * 200
            end_x = center_x + self.shockwave_direction[0] * wave_distance
            end_y = center_y + self.shockwave_direction[1] * wave_distance
            
            # 繪製主震波線
            alpha = int(255 * (timer / max_timer))
            pygame.draw.line(screen, (0, 255, 255, alpha), (center_x, center_y), (end_x, end_y), 8)
            
            # 繪製側邊波動效果
            perpendicular_x = -self.shockwave_direction[1] * 15
            perpendicular_y = self.shockwave_direction[0] * 15
            
            for i in range(5):
                wave_pos = progress * (i + 1) / 5
                if wave_pos <= 1:
                    wave_x = center_x + self.shockwave_direction[0] * wave_distance * wave_pos
                    wave_y = center_y + self.shockwave_direction[1] * wave_distance * wave_pos
                    
                    # 側邊波動
                    side_alpha = int(alpha * 0.6)
                    pygame.draw.line(screen, (100, 200, 255, side_alpha),
                                   (wave_x + perpendicular_x, wave_y + perpendicular_y),
                                   (wave_x - perpendicular_x, wave_y - perpendicular_y), 3)

        # 衝刺攻擊效果：雷電軌跡
        if self.visual_effects["charge_attack"]["active"]:
            timer = self.visual_effects["charge_attack"]["timer"]
            max_timer = 45
            
            # 在 Boss 周圍繪製雷電效果
            alpha = int(255 * (timer / max_timer))
            
            # 繪製多條隨機雷電
            for i in range(6):
                angle = (i * 60 + pygame.time.get_ticks() // 10) % 360
                lightning_length = 40 + random.randint(-10, 10)
                
                end_x = center_x + math.cos(math.radians(angle)) * lightning_length
                end_y = center_y + math.sin(math.radians(angle)) * lightning_length
                
                # 雷電顏色（紫白色）
                lightning_color = (200, 150, 255, alpha)
                pygame.draw.line(screen, lightning_color, (center_x, center_y), (end_x, end_y), 3)
                
            # 中心發光效果
            glow_surface = pygame.Surface((80, 80), pygame.SRCALPHA)
            glow_alpha = int(alpha * 0.3)
            pygame.draw.circle(glow_surface, (255, 255, 255, glow_alpha), (40, 40), 40)
            screen.blit(glow_surface, (center_x - 40, center_y - 40))

    def _draw_phase_indicators(self, screen, screen_x, screen_y):
        """
        繪製階段指示器\n
        \n
        在 Boss 上方顯示當前階段\n
        \n
        參數:\n
        screen: pygame 畫面物件\n
        screen_x (int): Boss 螢幕 x 位置\n
        screen_y (int): Boss 螢幕 y 位置\n
        """
        for i in range(self.phase):
            star_x = screen_x + self.width // 2 - (self.max_phases * 8) // 2 + i * 16
            star_y = screen_y - 20

            # 繪製階段星星
            points = []
            for angle in range(0, 360, 72):  # 5角星
                outer_radius = 6
                inner_radius = 3

                outer_angle = math.radians(angle)
                inner_angle = math.radians(angle + 36)

                points.append(
                    (
                        star_x + outer_radius * math.cos(outer_angle),
                        star_y + outer_radius * math.sin(outer_angle),
                    )
                )
                points.append(
                    (
                        star_x + inner_radius * math.cos(inner_angle),
                        star_y + inner_radius * math.sin(inner_angle),
                    )
                )

            pygame.draw.polygon(screen, (255, 215, 0), points)

    def _draw_boss_health_bar(self, screen, screen_x, screen_y):
        """
        繪製 Boss 血量條\n
        \n
        比普通敵人更大更顯眼的血量條\n
        \n
        參數:\n
        screen: pygame 畫面物件\n
        screen_x (int): Boss 螢幕 x 位置\n
        screen_y (int): Boss 螢幕 y 位置\n
        """
        bar_width = self.width + 20
        bar_height = 8
        bar_x = screen_x - 10
        bar_y = screen_y - 15

        # 計算血量比例
        health_ratio = max(0, self.health / self.max_health)

        # 繪製背景
        pygame.draw.rect(screen, (60, 60, 60), (bar_x, bar_y, bar_width, bar_height))

        # 繪製血量條
        health_color = (255, 0, 0)
        if health_ratio > 0.6:
            health_color = (255, 255, 0)  # 黃色
        elif health_ratio > 0.3:
            health_color = (255, 165, 0)  # 橙色

        pygame.draw.rect(
            screen, health_color, (bar_x, bar_y, bar_width * health_ratio, bar_height)
        )

        # 繪製邊框
        pygame.draw.rect(
            screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 1
        )

