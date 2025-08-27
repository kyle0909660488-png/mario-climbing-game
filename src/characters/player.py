######################載入套件######################
import pygame
from typing import List, Tuple, Dict

######################角色能力設定######################
# 各種角色的基礎能力數值
CHARACTER_CONFIGS = {
    0: {  # 平衡型角色
        "name": "平衡瑪莉歐",
        "max_health": 100,
        "speed": 5,
        "jump_power": 15,
        "has_double_jump": False,
        "attack_damage": 20,
        "color": (255, 0, 0),  # 紅色
    },
    1: {  # 速度型角色
        "name": "疾速瑪莉歐",
        "max_health": 80,
        "speed": 8,
        "jump_power": 12,
        "has_double_jump": False,
        "attack_damage": 15,
        "color": (0, 255, 0),  # 綠色
    },
    2: {  # 跳躍型角色
        "name": "跳跳瑪莉歐",
        "max_health": 90,
        "speed": 4,
        "jump_power": 18,
        "has_double_jump": True,
        "attack_damage": 18,
        "color": (0, 0, 255),  # 藍色
    },
    3: {  # 坦克型角色
        "name": "坦克瑪莉歐",
        "max_health": 150,
        "speed": 3,
        "jump_power": 10,
        "has_double_jump": False,
        "attack_damage": 25,
        "color": (128, 0, 128),  # 紫色
    },
}


######################玩家類別定義######################
class Player:
    """
    玩家角色控制類別\n
    \n
    負責管理玩家角色的所有行為和狀態，包括：\n
    1. 角色移動和物理運算（重力、碰撞）\n
    2. 輸入處理（WASD 操作和攻擊）\n
    3. 角色能力系統（不同角色的特殊技能）\n
    4. 狀態管理（血量、位置、動作狀態）\n
    \n
    屬性:\n
    x, y (float): 角色當前位置座標\n
    velocity_x, velocity_y (float): 角色當前速度\n
    health (int): 當前血量\n
    max_health (int): 最大血量\n
    character_type (int): 角色類型編號\n
    is_on_ground (bool): 是否站在地面上\n
    can_double_jump (bool): 是否還能二段跳\n
    is_crouching (bool): 是否處於蹲下狀態\n
    \n
    操作說明:\n
    - W/空白鍵: 跳躍（有二段跳能力的角色可以在空中再跳一次，蹲下時無法跳躍）\n
    - A/左方向鍵: 向左移動\n
    - S/下方向鍵: 蹲下（減少碰撞體積，某些陷阱可能躲過，蹲下時無法跳躍）\n
    - D/右方向鍵: 向右移動\n
    - C: 攻擊（近戰攻擊，對附近敵人造成傷害）\n
    - R: 加速衝刺（提高移動速度，配合跳躍可增加跳躍高度）\n
    \n
    組合技能:\n
    - R+W/空白鍵: 加速跳躍，跳躍高度提升 30%\n
    """

    def __init__(self, start_x: float, start_y: float, character_type: int = 0):
        """
        初始化玩家角色\n
        \n
        根據角色類型設定對應的能力數值和初始狀態\n
        \n
        參數:\n
        start_x (float): 起始 X 座標\n
        start_y (float): 起始 Y 座標\n
        character_type (int): 角色類型，範圍 0-3\n
        """
        # 基本位置和物理狀態
        self.x = float(start_x)
        self.y = float(start_y)
        self.velocity_x = 0.0
        self.velocity_y = 0.0

        # 根據角色類型設定能力
        self.character_type = character_type
        config = CHARACTER_CONFIGS[character_type]

        # 角色基本屬性
        self.name = config["name"]
        self.max_health = config["max_health"]
        self.health = self.max_health  # 開始時血量滿格
        self.speed = config["speed"]
        self.jump_power = config["jump_power"]
        self.has_double_jump_ability = config["has_double_jump"]
        self.attack_damage = config["attack_damage"]
        self.color = config["color"]

        # 角色尺寸（用於碰撞檢測）
        self.width = 30
        self.height = 40

        # 移動狀態
        self.is_on_ground = False
        self.can_double_jump = self.has_double_jump_ability  # 每次落地重置
        self.is_crouching = False
        self.is_sprinting = False  # 是否正在加速衝刺

        # 速度調節係數
        self.base_speed = self.speed  # 保存原始速度
        self.sprint_multiplier = 1.5  # 加速時的速度倍率
        self.jump_boost_multiplier = 1.3  # 加速跳躍時的額外高度倍率

        # 攻擊狀態
        self.attack_cooldown = 0  # 攻擊冷卻時間，避免連續攻擊
        self.is_attacking = False

        # 無敵時間（受傷後短暫無法再受傷）
        self.invulnerability_time = 0

        # 按鍵狀態記錄（用於實現單次觸發和跳躍緩衝）
        self.previous_jump_key_pressed = False
        self.jump_buffer_time = 0  # 跳躍緩衝時間，提高反應靈敏度

        # 裝備管理器引用
        self.equipment_manager = None

    def handle_input(self, keys, platforms: List = None):
        """
        處理玩家輸入\n
        \n
        根據按鍵狀態更新玩家的移動意圖，實際移動在 update 方法中處理\n
        支援多種按鍵配置以避免鍵盤衝突問題\n
        \n
        參數:\n
        keys (dict): pygame.key.get_pressed() 回傳的按鍵狀態字典\n
        \n
        支援的按鍵配置:\n
        - 移動: WASD 或 方向鍵\n
        - 跳躍: W 或 空白鍵（避免與移動鍵衝突）\n
        - 加速: R 鍵\n
        - 攻擊: C 鍵\n
        \n
        新增控制:\n
        - R: 加速衝刺（提高移動速度）\n
        - 跳躍緩衝機制：按下跳躍鍵後有短暫緩衝時間，提高反應靈敏度\n
        - 加速+跳躍組合技：跳躍高度提升\n
        - 蹲下時無法跳躍\n
        """
        # 檢查是否正在加速（R 鍵）
        self.is_sprinting = keys[pygame.K_r]

        # 根據加速狀態調整移動速度
        current_speed = self.base_speed
        if self.is_sprinting:
            current_speed = self.base_speed * self.sprint_multiplier

        # 左右移動（A/D 鍵 或 左右方向鍵）
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.velocity_x = -current_speed  # 向左移動
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.velocity_x = current_speed  # 向右移動
        else:
            # 沒按移動鍵就逐漸停下來（模擬摩擦力）
            self.velocity_x *= 0.8
            if abs(self.velocity_x) < 0.1:  # 速度太小就直接設為0
                self.velocity_x = 0

        # 跳躍（W 鍵或空白鍵）- 改良的反應機制
        jump_key_pressed = keys[pygame.K_w] or keys[pygame.K_SPACE]

        # 跳躍緩衝機制：當玩家按下跳躍鍵時，給予一個短暫的緩衝時間
        if jump_key_pressed and not self.previous_jump_key_pressed:
            self.jump_buffer_time = 8  # 8幀的緩衝時間（約0.13秒）

        # 如果有跳躍緩衝且不在蹲下狀態，嘗試跳躍
        if self.jump_buffer_time > 0 and not self.is_crouching:
            if self._try_jump():  # 如果跳躍成功，清除緩衝
                self.jump_buffer_time = 0

        # 更新緩衝時間
        if self.jump_buffer_time > 0:
            self.jump_buffer_time -= 1

        self.previous_jump_key_pressed = jump_key_pressed  # 記錄當前幀的按鍵狀態

        # 蹲下（S 鍵或下方向鍵）- 改良版本，正確處理位置調整
        self._handle_crouch_input(keys[pygame.K_s] or keys[pygame.K_DOWN], platforms)

        # 攻擊（C 鍵）
        if keys[pygame.K_c] and self.attack_cooldown <= 0:
            self._perform_attack()

        # 裝備技能快捷鍵（數字鍵 1-4）
        if hasattr(self, "equipment_manager") and self.equipment_manager:
            if keys[pygame.K_1]:
                self.equipment_manager.use_skill("fire_ball", self)
            elif keys[pygame.K_2]:
                self.equipment_manager.use_skill("freeze", self)
            elif keys[pygame.K_3]:
                self.equipment_manager.use_skill("invisibility", self)
            elif keys[pygame.K_4]:
                self.equipment_manager.use_skill("shield", self)

    def _try_jump(self):
        """
        嘗試執行跳躍（改良的反應機制）\n
        \n
        根據當前狀態決定是否能跳躍：\n
        - 在地面上：直接跳躍，重置二段跳能力\n
        - 在空中且有二段跳能力：執行二段跳，消耗二段跳次數\n
        - 其他情況：無法跳躍\n
        \n
        新增跳躍緩衝機制：\n
        - 當玩家按下跳躍鍵時，提供短暫的緩衝時間\n
        - 即使按鍵時機稍有偏差，也能成功跳躍\n
        - 提高操作的靈敏度和容錯性\n
        \n
        回傳:\n
        bool: 跳躍是否成功執行\n
        \n
        組合技能：\n
        - 加速+跳躍：跳躍高度提升 30%\n
        """
        # 計算跳躍力量，加速時有額外加成
        jump_force = self.jump_power
        if self.is_sprinting:
            jump_force = self.jump_power * self.jump_boost_multiplier

        if self.is_on_ground:
            # 在地面上，直接跳躍
            self.velocity_y = -jump_force  # 負數表示向上
            self.is_on_ground = False
            # 重置二段跳能力
            if self.has_double_jump_ability:
                self.can_double_jump = True
            return True  # 跳躍成功

        elif self.can_double_jump and self.has_double_jump_ability:
            # 在空中且有二段跳能力，執行二段跳
            # 二段跳力量稍微弱一點，但同樣受加速影響
            second_jump_force = jump_force * 0.8
            self.velocity_y = -second_jump_force
            self.can_double_jump = False  # 用掉二段跳機會
            return True  # 二段跳成功

        return False  # 無法跳躍

    def _handle_crouch_input(self, crouch_key_pressed: bool, platforms: List = None):
        """
        處理蹲下輸入並調整玩家位置\n
        \n
        正確處理蹲下和站起來時的位置調整，確保玩家的腳部位置保持一致\n
        避免蹲下後站起來時身體卡在地板裡或穿透地板的問題\n
        \n
        參數:\n
        crouch_key_pressed (bool): 是否按下蹲下鍵\n
        \n
        邏輯說明:\n
        - 從站立變為蹲下：Y座標向下移動 (height - height//2)，保持腳部位置不變\n
        - 從蹲下變為站立：Y座標向上移動 (height - height//2)，恢復原始高度\n
        - 站起來時會檢查頭部空間，如果上方有障礙物會阻止站起來\n
        """
        was_crouching = self.is_crouching
        want_to_crouch = crouch_key_pressed

        # 如果狀態沒有改變，直接回傳
        if was_crouching == want_to_crouch:
            return

        # 計算高度差異
        height_difference = self.height - self.height // 2  # 站立高度 - 蹲下高度

        if not was_crouching and want_to_crouch:
            # 從站立變為蹲下
            # 向下調整Y座標，讓腳部位置保持不變
            self.y += height_difference
            self.is_crouching = True

        elif was_crouching and not want_to_crouch:
            # 從蹲下變為站立
            # 需要檢查頭部上方是否有空間站起來
            if self._can_stand_up(platforms):
                # 向上調整Y座標，恢復站立高度
                self.y -= height_difference
                self.is_crouching = False
            # 如果無法站起來，保持蹲下狀態

    def _can_stand_up(self, platforms: List = None) -> bool:
        """
        檢查玩家是否能從蹲下狀態站起來\n
        \n
        檢查玩家頭部上方是否有足夠空間站立，避免站起來時頭部卡在天花板或平台裡\n
        \n
        參數:\n
        platforms (List): 平台物件清單，用於碰撞檢測\n
        \n
        回傳:\n
        bool: 是否能夠站起來\n
        """
        if platforms is None:
            return True  # 如果沒有平台資料，預設允許站起來

        # 計算站立時的碰撞矩形
        height_difference = self.height - self.height // 2
        standing_rect = pygame.Rect(
            self.x,
            self.y - height_difference,  # 站立時Y座標會向上移動
            self.width,
            self.height,  # 完整高度
        )

        # 檢查是否與任何平台碰撞
        for platform in platforms:
            platform_rect = platform.get_collision_rect()
            if standing_rect.colliderect(platform_rect):
                return False  # 有碰撞，無法站起來

        return True  # 沒有碰撞，可以站起來

    def _perform_attack(self):
        """
        執行攻擊動作\n
        \n
        觸發近戰攻擊，對附近的敵人造成傷害\n
        設定攻擊冷卻時間避免連續攻擊\n
        """
        self.is_attacking = True
        self.attack_cooldown = 20  # 20 幀的冷卻時間

    def update(self, platforms: List, traps: List):
        """
        更新玩家狀態\n
        \n
        執行每幀的狀態更新，包括：\n
        1. 物理運算（重力、移動）\n
        2. 碰撞檢測（平台、陷阱）\n
        3. 狀態計時器更新\n
        \n
        參數:\n
        platforms (List): 當前關卡的平台清單\n
        traps (List): 當前關卡的陷阱清單\n
        """
        # 更新各種計時器
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        if self.invulnerability_time > 0:
            self.invulnerability_time -= 1

        # 重力作用（除非站在地面上）
        if not self.is_on_ground:
            self.velocity_y += 0.8  # 重力加速度

        # 限制最大下墜速度，避免穿過平台（更嚴格的限制）
        if self.velocity_y > 12:
            self.velocity_y = 12

        # 分別處理水平和垂直移動，避免高速穿透
        self._update_horizontal_movement(platforms)
        self._update_vertical_movement(platforms)

        # 碰撞檢測陷阱
        self._check_trap_collisions(traps)

        # 重置攻擊狀態
        if self.attack_cooldown <= 0:
            self.is_attacking = False

    def _update_horizontal_movement(self, platforms: List):
        """
        更新水平移動並檢查碰撞\n
        \n
        將水平移動和碰撞檢測分開處理，避免高速移動時穿透問題\n
        \n
        參數:\n
        platforms (List): 平台物件清單\n
        """
        if abs(self.velocity_x) < 0.01:  # 水平速度很小時直接設為 0
            self.velocity_x = 0
            return

        # 儲存原始位置
        original_x = self.x

        # 嘗試移動
        self.x += self.velocity_x

        # 建立玩家碰撞矩形
        player_rect = self._get_current_collision_rect()

        # 檢查與平台的水平碰撞
        for platform in platforms:
            platform_rect = platform.get_collision_rect()

            if player_rect.colliderect(platform_rect):
                # 發生碰撞，根據移動方向調整位置
                if self.velocity_x > 0:  # 向右移動，撞到平台左側
                    self.x = platform_rect.left - self.width
                else:  # 向左移動，撞到平台右側
                    self.x = platform_rect.right

                self.velocity_x = 0  # 停止水平移動
                break

    def _update_vertical_movement(self, platforms: List):
        """
        更新垂直移動並檢查碰撞\n
        \n
        將垂直移動和碰撞檢測分開處理，避免高速下降時穿透平台\n
        \n
        參數:\n
        platforms (List): 平台物件清單\n
        """
        # 先假設不在地面上
        was_on_ground = self.is_on_ground
        self.is_on_ground = False

        if abs(self.velocity_y) < 0.01:  # 垂直速度很小時直接設為 0
            self.velocity_y = 0
            # 如果速度很小但之前在地面上，檢查是否還在地面上
            if was_on_ground:
                self._check_ground_contact(platforms)
            return

        # 儲存原始位置
        original_y = self.y

        # 嘗試移動
        self.y += self.velocity_y

        # 建立玩家碰撞矩形
        player_rect = self._get_current_collision_rect()

        # 檢查與平台的垂直碰撞
        for platform in platforms:
            platform_rect = platform.get_collision_rect()

            if player_rect.colliderect(platform_rect):
                if self.velocity_y > 0:  # 正在下降，可能落在平台上
                    # 確認玩家之前在平台上方
                    current_height = (
                        self.height if not self.is_crouching else self.height // 2
                    )
                    player_bottom_before = original_y + current_height

                    # 使用更嚴格的檢查，確保玩家確實從上方下來
                    if (
                        player_bottom_before <= platform_rect.top + 3
                    ):  # 減少容錯範圍到3像素
                        # 玩家確實是從上方落到平台上
                        new_y = platform_rect.top - current_height

                        # 驗證新位置的有效性
                        if self._is_valid_position(new_y, platforms, platform):
                            self.y = new_y
                            self.velocity_y = 0
                            self.is_on_ground = True

                            # 恢復二段跳能力（只有在真正著地時）
                            if self.has_double_jump_ability:
                                self.can_double_jump = True
                        else:
                            # 如果新位置無效，稍微調整
                            self.y = original_y
                            self.velocity_y = 1  # 給一點小速度繼續下降

                        break

                elif self.velocity_y < 0:  # 正在上升，撞到平台下方
                    # 確認玩家之前在平台下方
                    player_top_before = original_y
                    if player_top_before >= platform_rect.bottom - 3:  # 減少容錯範圍
                        # 玩家確實是從下方撞到平台底部
                        new_y = platform_rect.bottom

                        # 驗證新位置的有效性
                        if self._is_valid_position(new_y, platforms, platform):
                            self.y = new_y
                            self.velocity_y = 0
                        else:
                            # 如果新位置無效，稍微調整
                            self.y = original_y
                            self.velocity_y = -1  # 給一點小速度繼續上升

                        break

    def _check_ground_contact(self, platforms: List):
        """
        檢查玩家是否還與地面接觸\n
        \n
        當玩家垂直速度很小時，檢查是否還站在平台上\n
        \n
        參數:\n
        platforms (List): 平台物件清單\n
        """
        current_height = self.height if not self.is_crouching else self.height // 2

        # 建立一個稍微向下延伸的檢測矩形
        ground_check_rect = pygame.Rect(
            self.x + 2,  # 左右各縮進2像素，更精確檢測
            self.y + current_height,
            self.width - 4,
            3,  # 向下延伸3像素檢查地面
        )

        for platform in platforms:
            platform_rect = platform.get_collision_rect()
            if ground_check_rect.colliderect(platform_rect):
                self.is_on_ground = True
                return

    def _is_valid_position(
        self, new_y: float, platforms: List, current_platform
    ) -> bool:
        """
        驗證新位置是否有效\n
        \n
        檢查調整後的位置是否會與其他平台產生不合理的碰撞\n
        \n
        參數:\n
        new_y (float): 新的Y座標\n
        platforms (List): 平台物件清單\n
        current_platform: 當前碰撞的平台（排除檢查）\n
        \n
        回傳:\n
        bool: 位置是否有效\n
        """
        # 建立新位置的碰撞矩形
        test_rect = pygame.Rect(
            self.x,
            new_y,
            self.width,
            self.height if not self.is_crouching else self.height // 2,
        )

        # 檢查是否與其他平台重疊
        for platform in platforms:
            if platform == current_platform:
                continue  # 跳過當前碰撞的平台

            if test_rect.colliderect(platform.get_collision_rect()):
                return False  # 與其他平台重疊，位置無效

        return True  # 位置有效

    def _get_current_collision_rect(self) -> pygame.Rect:
        """
        取得當前玩家的碰撞矩形（考慮蹲下狀態）\n
        \n
        回傳:\n
        pygame.Rect: 當前碰撞矩形\n
        """
        height = self.height if not self.is_crouching else self.height // 2
        return pygame.Rect(self.x, self.y, self.width, height)

    def _check_trap_collisions(self, traps: List):
        """
        檢查與陷阱的碰撞\n
        \n
        檢測玩家是否觸發陷阱，不同陷阱有不同效果：\n
        - 尖刺：造成傷害\n
        - 火焰：持續傷害\n
        - 移動平台：跟隨移動\n
        \n
        參數:\n
        traps (List): 陷阱物件清單\n
        """
        if self.invulnerability_time > 0:
            return  # 無敵時間內不會受到陷阱傷害

        player_rect = pygame.Rect(
            self.x,
            self.y,
            self.width,
            self.height if not self.is_crouching else self.height // 2,
        )

        for trap in traps:
            if trap.is_active and player_rect.colliderect(trap.get_collision_rect()):
                # 觸發陷阱效果
                damage = trap.get_damage()
                self.take_damage(damage)

                # 某些陷阱可能有擊退效果
                knockback = trap.get_knockback()
                if knockback:
                    self.velocity_x += knockback[0]
                    self.velocity_y += knockback[1]

    def take_damage(self, damage: int):
        """
        角色受到傷害\n
        \n
        減少角色血量，觸發無敵時間防止連續受傷\n
        \n
        參數:\n
        damage (int): 受到的傷害數值\n
        """
        if self.invulnerability_time <= 0:
            self.health -= damage
            self.invulnerability_time = 60  # 60 幀的無敵時間（1秒）

            # 血量不能低於 0
            if self.health < 0:
                self.health = 0

    def heal(self, amount: int):
        """
        角色恢復血量\n
        \n
        增加角色血量，不能超過最大值\n
        \n
        參數:\n
        amount (int): 恢復的血量數值\n
        """
        self.health += amount
        if self.health > self.max_health:
            self.health = self.max_health

    def get_attack_rect(self) -> pygame.Rect:
        """
        取得攻擊範圍的矩形\n
        \n
        回傳玩家攻擊時的有效範圍，用於檢測攻擊到的敵人\n
        \n
        回傳:\n
        pygame.Rect: 攻擊範圍矩形\n
        """
        # 攻擊範圍比角色稍微大一些
        attack_width = self.width + 20
        attack_height = self.height
        attack_x = self.x - 10  # 攻擊範圍向左右延伸
        attack_y = self.y

        return pygame.Rect(attack_x, attack_y, attack_width, attack_height)

    def get_collision_rect(self) -> pygame.Rect:
        """
        取得角色的碰撞矩形\n
        \n
        回傳角色當前的碰撞範圍，蹲下時高度會縮小\n
        \n
        回傳:\n
        pygame.Rect: 碰撞範圍矩形\n
        """
        height = self.height if not self.is_crouching else self.height // 2
        return pygame.Rect(self.x, self.y, self.width, height)

    def render(self, screen: pygame.Surface, camera_y: float):
        """
        繪製玩家角色\n
        \n
        在螢幕上繪製角色，包括角色本體和狀態指示\n
        \n
        參數:\n
        screen (pygame.Surface): 要繪製到的畫面\n
        camera_y (float): 攝影機 Y 軸偏移（用於卷軸效果）\n
        """
        # 計算在螢幕上的繪製位置（考慮攝影機位置）
        screen_x = int(self.x)
        screen_y = int(self.y - camera_y + screen.get_height() // 2)

        # 角色顏色（受傷時會閃爍，加速時會變亮）
        color = self.color

        # 受傷閃爍效果
        if self.invulnerability_time > 0 and (self.invulnerability_time // 5) % 2:
            # 無敵時間內每 5 幀閃爍一次（變成半透明）
            color = tuple(c // 2 for c in self.color)

        # 加速時的亮度增強效果
        if self.is_sprinting:
            color = tuple(min(255, c + 50) for c in color)  # 每個顏色通道增加亮度

        # 繪製角色矩形（蹲下時高度縮小）
        height = self.height if not self.is_crouching else self.height // 2
        pygame.draw.rect(screen, color, (screen_x, screen_y, self.width, height))

        # 繪製角色邊框（加速時邊框變粗）
        border_width = 3 if self.is_sprinting else 2
        pygame.draw.rect(
            screen, (0, 0, 0), (screen_x, screen_y, self.width, height), border_width
        )

        # 加速時繪製速度線條效果
        if self.is_sprinting and abs(self.velocity_x) > 0.5:
            # 在角色後方畫幾條速度線
            line_direction = -1 if self.velocity_x > 0 else 1  # 速度線方向相反
            for i in range(3):
                line_x = screen_x + self.width // 2 + (line_direction * (15 + i * 5))
                line_y1 = screen_y + 5 + i * 3
                line_y2 = screen_y + height - 5 - i * 3

                # 確保線條在螢幕範圍內
                if 0 <= line_x < screen.get_width():
                    pygame.draw.line(
                        screen, (255, 255, 255), (line_x, line_y1), (line_x, line_y2), 2
                    )

        # 如果正在攻擊，繪製攻擊範圍
        if self.is_attacking:
            attack_rect = self.get_attack_rect()
            attack_screen_x = int(attack_rect.x)
            attack_screen_y = int(attack_rect.y - camera_y + screen.get_height() // 2)
            pygame.draw.rect(
                screen,
                (255, 255, 0),
                (
                    attack_screen_x,
                    attack_screen_y,
                    attack_rect.width,
                    attack_rect.height,
                ),
                3,
            )

        # 繪製血量條（在角色上方）
        self._draw_health_bar(screen, screen_x, screen_y - 10)

    def _draw_health_bar(self, screen: pygame.Surface, x: int, y: int):
        """
        繪製血量條\n
        \n
        在指定位置繪製角色的血量狀態\n
        \n
        參數:\n
        screen (pygame.Surface): 要繪製到的畫面\n
        x (int): 血量條 X 座標\n
        y (int): 血量條 Y 座標\n
        """
        bar_width = self.width
        bar_height = 6

        # 血量條背景（灰色）
        pygame.draw.rect(screen, (100, 100, 100), (x, y, bar_width, bar_height))

        # 血量條前景（根據血量比例決定顏色）
        health_ratio = self.health / self.max_health
        health_width = int(bar_width * health_ratio)

        # 血量顏色：綠→黃→紅
        if health_ratio > 0.6:
            health_color = (0, 255, 0)  # 綠色
        elif health_ratio > 0.3:
            health_color = (255, 255, 0)  # 黃色
        else:
            health_color = (255, 0, 0)  # 紅色

        if health_width > 0:
            pygame.draw.rect(screen, health_color, (x, y, health_width, bar_height))

    def set_equipment_manager(self, equipment_manager):
        """
        設置裝備管理器引用\n
        \n
        讓玩家能夠使用裝備技能\n
        \n
        參數:\n
        equipment_manager: 裝備管理器物件\n
        """
        self.equipment_manager = equipment_manager
