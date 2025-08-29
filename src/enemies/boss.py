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
        self.special_skills = ["area_attack", "summon_minions", "shockwave"]
        self.skill_cooldowns = {
            "area_attack": 0,
            "summon_minions": 0,
            "shockwave": 0,
            "charge_attack": 0,
        }

        # Boss 專屬狀態
        self.is_casting_skill = False
        self.cast_timer = 0
        self.current_skill = None

        # 小兵管理
        self.minions = []
        self.max_minions = 4

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
            2: ["basic_attack", "area_attack", "summon_minions"],
            3: [
                "basic_attack",
                "area_attack",
                "summon_minions",
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

        # 除錯資訊：印出Boss座標和狀態
        if hasattr(self, 'debug_timer'):
            self.debug_timer += 1
        else:
            self.debug_timer = 0
            
        # 每秒印出一次除錯資訊（60幀 = 1秒）
        if self.debug_timer % 60 == 0:
            ground_status = "在地面上" if self.is_on_ground else "在空中"
            platform_status = f"站在移動平台: {self.standing_on_moving_platform is not None}" if hasattr(self, 'standing_on_moving_platform') else "無移動平台資訊"
            print(f"[Boss除錯] 位置: ({self.x:.1f}, {self.y:.1f}), 速度: ({self.velocity_x:.1f}, {self.velocity_y:.1f}), 狀態: {ground_status}, {platform_status}")
            
            # 檢查Boss腳下是否有平台
            if platforms:
                boss_bottom = self.y + self.height
                boss_center_x = self.x + self.width // 2
                nearby_platforms = []
                for platform in platforms:
                    if (platform.x <= boss_center_x <= platform.x + platform.width and 
                        abs(boss_bottom - platform.y) < 10):
                        nearby_platforms.append(f"平台({platform.x}, {platform.y}, {platform.width}x{platform.height})")
                
                if nearby_platforms:
                    print(f"[Boss除錯] 腳下平台: {', '.join(nearby_platforms)}")
                else:
                    print(f"[Boss除錯] 腳下無平台，Boss底部Y: {boss_bottom:.1f}")

        # 更新動畫
        self._update_animation()

        # 除錯資訊：印出Boss座標和狀態
        if hasattr(self, '_debug_timer'):
            self._debug_timer += 1
        else:
            self._debug_timer = 0
            
        # 每60幀（約1秒）印出一次Boss狀態
        if self._debug_timer % 60 == 0:
            print(f"Boss座標: ({self.x:.1f}, {self.y:.1f}), 是否在地面: {self.is_on_ground}, 垂直速度: {self.velocity_y:.2f}")
            
            # 檢查Boss是否在平台範圍內
            if platforms:
                boss_rect = self.get_collision_rect()
                on_platform = False
                for i, platform in enumerate(platforms):
                    platform_rect = pygame.Rect(platform.x, platform.y, platform.width, platform.height)
                    # 檢查Boss腳部是否接觸平台頂部
                    boss_bottom = boss_rect.bottom
                    platform_top = platform_rect.top
                    if (boss_rect.centerx >= platform_rect.left and 
                        boss_rect.centerx <= platform_rect.right and 
                        abs(boss_bottom - platform_top) <= 10):
                        print(f"  -> Boss站在平台 {i}: ({platform.x}, {platform.y}, {platform.width}x{platform.height})")
                        on_platform = True
                        break
                        
                if not on_platform:
                    print(f"  -> Boss沒有站在任何平台上！最近的平台距離:")
                    for i, platform in enumerate(platforms[:3]):  # 只顯示前3個平台
                        platform_rect = pygame.Rect(platform.x, platform.y, platform.width, platform.height)
                        distance = abs(boss_rect.centery - platform_rect.centery)
                        print(f"    平台 {i}: 距離 {distance:.1f} 像素")

        # 更新小兵
        self._update_minions(player, platforms)

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
            "summon_minions": 120,  # 2秒
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
        elif skill_name == "summon_minions":
            self._summon_minions()
        elif skill_name == "shockwave":
            self._shockwave_attack(player)
        elif skill_name == "charge_attack":
            self._charge_attack(player)

        # 設定技能冷卻時間
        cooldown_times = {
            "area_attack": 300,  # 5秒
            "summon_minions": 600,  # 10秒
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
            self.area_attack_timer = 30  # 顯示效果持續 0.5 秒
        else:
            self.area_attack_active = False

    def _summon_minions(self):
        """
        召喚小兵技能\n
        \n
        在 Boss 周圍生成小兵\n
        """
        # 如果小兵數量未滿，召喚新的小兵
        minions_to_summon = min(2, self.max_minions - len(self.minions))

        for i in range(minions_to_summon):
            # 在 Boss 周圍隨機位置生成小兵
            offset_x = random.randint(-80, 80)
            offset_y = random.randint(-40, 40)

            minion_x = self.x + offset_x
            minion_y = self.y + offset_y

            minion = BossMinion(minion_x, minion_y)
            self.minions.append(minion)

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
            self.shockwave_timer = 60  # 1秒持續時間
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
            self.charge_attack_timer = 45  # 0.75秒衝刺時間
            self.charge_attack_damage = self.attack_damage + 25
        else:
            self.charge_attack_active = False

    def _update_minions(self, player, platforms=None):
        """
        更新所有小兵狀態\n
        \n
        參數:\n
        player: 玩家物件\n
        platforms (list): 平台列表，用於小兵的碰撞檢測\n
        """
        for minion in self.minions[:]:  # 使用複本避免修改時出錯
            minion.update(player, platforms)

            # 移除死亡的小兵
            if minion.health <= 0:
                self.minions.remove(minion)

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
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y

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

        # 繪製小兵
        for minion in self.minions:
            minion.draw(screen, camera_x, camera_y)

    def _draw_skill_effects(self, screen, camera_x, camera_y):
        """
        繪製技能特效\n
        \n
        參數:\n
        screen: pygame 畫面物件\n
        camera_x (int): 攝影機 x 偏移\n
        camera_y (int): 攝影機 y 偏移\n
        """
        # 範圍攻擊效果
        if hasattr(self, "area_attack_active") and self.area_attack_active:
            if hasattr(self, "area_attack_timer") and self.area_attack_timer > 0:
                self.area_attack_timer -= 1

                center_x = self.x + self.width // 2 - camera_x
                center_y = self.y + self.height // 2 - camera_y

                # 繪製範圍攻擊圈
                alpha = int((self.area_attack_timer / 30) * 100)
                attack_surface = pygame.Surface(
                    (self.area_attack_range * 2, self.area_attack_range * 2),
                    pygame.SRCALPHA,
                )
                pygame.draw.circle(
                    attack_surface,
                    (255, 0, 0, alpha),
                    (self.area_attack_range, self.area_attack_range),
                    self.area_attack_range,
                )
                screen.blit(
                    attack_surface,
                    (
                        center_x - self.area_attack_range,
                        center_y - self.area_attack_range,
                    ),
                )
            else:
                self.area_attack_active = False

        # 震波攻擊效果
        if hasattr(self, "shockwave_active") and self.shockwave_active:
            if hasattr(self, "shockwave_timer") and self.shockwave_timer > 0:
                self.shockwave_timer -= 1

                # 繪製震波（簡化為線條）
                start_x = self.x + self.width // 2 - camera_x
                start_y = self.y + self.height // 2 - camera_y

                wave_length = (60 - self.shockwave_timer) * 8
                end_x = start_x + self.shockwave_direction[0] * wave_length
                end_y = start_y + self.shockwave_direction[1] * wave_length

                pygame.draw.line(
                    screen, (255, 100, 0), (start_x, start_y), (end_x, end_y), 5
                )
            else:
                self.shockwave_active = False

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


######################Boss 小兵類別######################
class BossMinion(BaseEnemy):
    """
    Boss 召喚的小兵\n
    \n
    比普通敵人弱但數量多的小兵：\n
    1. 較低的血量和攻擊力\n
    2. 較快的移動速度\n
    3. 簡單的 AI 行為\n
    4. 有限的存在時間\n
    """

    def __init__(self, x, y):
        """
        初始化小兵\n
        \n
        參數:\n
        x (int): 初始 x 位置\n
        y (int): 初始 y 位置\n
        """
        # 呼叫父類初始化，使用小兵級的屬性
        super().__init__(x, y, health=50, attack_damage=15, speed=2)

        # 小兵尺寸
        self.width = 30
        self.height = 30
        self.detection_range = 100

        # 存在時間（30秒後消失）
        self.lifetime = 1800

        # 小兵顏色（較淡的紅色）
        self.color = (100, 50, 50)

    def update(self, player, platforms=None):
        """
        更新小兵狀態\n
        \n
        包含簡化的 AI 和存在時間倒數\n
        \n
        參數:\n
        player: 玩家物件\n
        platforms (list): 平台列表，用於碰撞檢測\n
        """
        # 減少存在時間
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.health = 0  # 標記為死亡

        # 簡單的追擊 AI
        distance_to_player = abs(player.x - self.x) + abs(player.y - self.y)

        if distance_to_player < self.detection_range:
            if distance_to_player < 40:
                self.state = "attack"
            else:
                self.state = "chase"
        else:
            self.state = "patrol"

        # 呼叫父類更新
        super().update(player, platforms)

    def draw(self, screen, camera_x=0, camera_y=0):
        """
        繪製小兵\n
        \n
        使用較小的尺寸和不同顏色區別於普通敵人\n
        """
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y

        # 檢查是否在螢幕範圍內
        if (
            screen_x < -50
            or screen_x > screen.get_width() + 50
            or screen_y < -50
            or screen_y > screen.get_height() + 50
        ):
            return

        # 存在時間不足時閃爍
        if self.lifetime < 300:  # 最後 5 秒
            if (self.lifetime // 10) % 2 == 0:  # 每 1/6 秒閃爍
                return

        # 繪製小兵主體
        pygame.draw.rect(
            screen, self.color, (screen_x, screen_y, self.width, self.height)
        )

        # 繪製簡單的血量指示
        if self.health < self.max_health:
            bar_width = self.width
            bar_height = 4
            bar_y = screen_y - 6

            health_ratio = self.health / self.max_health
            pygame.draw.rect(
                screen,
                (255, 0, 0),
                (screen_x, bar_y, bar_width * health_ratio, bar_height),
            )

    def update_ai(self, player, platforms=None):
        """
        小兵 AI 更新（實現抽象方法）\n
        \n
        簡單的追擊玩家邏輯\n
        \n
        參數:\n
        player: 玩家物件\n
        """
        # 小兵 AI 已在 update 方法中實現
        distance_to_player = abs(player.x - self.x) + abs(player.y - self.y)

        if distance_to_player < self.detection_range:
            if distance_to_player < 40:
                self.state = "attack"
            else:
                self.state = "chase"
                # 向玩家移動
                if player.x < self.x:
                    self.velocity_x = -self.speed
                else:
                    self.velocity_x = self.speed
        else:
            self.state = "patrol"
            self.velocity_x = 0

    def attack_player(self, player) -> dict:
        """
        小兵攻擊玩家（實現抽象方法）\n
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

        # 使用矩形碰撞檢測，比距離檢測更精確
        minion_rect = self.get_collision_rect()
        player_rect = player.get_collision_rect()
        
        # 擴展小兵攻擊範圍
        attack_range_x = 35
        attack_range_y = 20
        
        attack_rect = pygame.Rect(
            minion_rect.x - attack_range_x//2, 
            minion_rect.y - attack_range_y//2, 
            minion_rect.width + attack_range_x, 
            minion_rect.height + attack_range_y
        )
        
        if attack_rect.colliderect(player_rect):
            attack_info["hit"] = True

        return attack_info

    def render(self, screen: pygame.Surface, camera_y: float):
        """
        繪製小兵（實現抽象方法）\n
        \n
        參數:\n
        screen: pygame 畫面物件\n
        camera_y: 攝影機 y 偏移\n
        """
        # 直接呼叫已實現的 draw 方法
        self.draw(screen, 0, camera_y)
