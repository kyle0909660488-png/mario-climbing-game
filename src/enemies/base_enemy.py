######################載入套件######################
import pygame
import math
import random
from typing import Tuple, Optional
from abc import ABC, abstractmethod


######################敵人基礎抽象類別######################
class BaseEnemy(ABC):
    """
    所有敵人的基礎抽象類別\n
    \n
    定義敵人的共通介面和基本行為：\n
    1. 敵人的基本屬性（位置、血量、攻擊力）\n
    2. AI 行為模式（巡邏、追蹤、攻擊）\n
    3. 狀態管理（存活、受傷、攻擊狀態）\n
    4. 抽象方法強制子類別實作特定行為\n
    \n
    屬性:\n
    x, y (float): 敵人當前位置\n
    health (int): 當前血量\n
    max_health (int): 最大血量\n
    attack_damage (int): 攻擊傷害\n
    speed (float): 移動速度\n
    ai_state (str): 當前 AI 狀態\n
    \n
    子類別需要實作:\n
    - update_ai(): AI 行為邏輯\n
    - render(): 繪製敵人外觀\n
    - attack_player(): 攻擊玩家的行為\n
    """

    def __init__(
        self,
        x: float,
        y: float,
        health: int = 50,
        attack_damage: int = 15,
        speed: float = 1.0,
    ):
        """
        初始化基礎敵人\n
        \n
        設定敵人的基本屬性和狀態\n
        \n
        參數:\n
        x (float): 敵人起始 X 座標\n
        y (float): 敵人起始 Y 座標\n
        health (int): 敵人血量\n
        attack_damage (int): 敵人攻擊傷害\n
        speed (float): 敵人移動速度\n
        """
        # 基本位置和物理屬性
        self.x = float(x)
        self.y = float(y)
        self.start_x = float(x)  # 記住起始位置
        self.start_y = float(y)

        # 戰鬥屬性
        self.health = health
        self.max_health = health
        self.attack_damage = attack_damage
        self.speed = speed

        # 碰撞和尺寸
        self.width = 25
        self.height = 30

        # AI 狀態機
        self.ai_state = "patrol"  # 'patrol', 'chase', 'attack', 'dead'
        self.target_player = None
        self.last_known_player_pos = None

        # 移動和物理
        self.velocity_x = 0.0
        self.velocity_y = 0.0
        self.is_on_ground = False
        self.facing_direction = 1  # 1: 向右, -1: 向左
        self.standing_on_moving_platform = None  # 追蹤當前站立的移動平台

        # 巡邏行為
        self.patrol_center_x = x
        self.patrol_range = 100  # 巡邏範圍
        self.patrol_direction = 1

        # 戰鬥狀態
        self.attack_cooldown = 0
        self.max_attack_cooldown = 60  # 1秒攻擊間隔
        self.detection_range = 120  # 偵測玩家的距離
        self.attack_range = 40  # 攻擊距離

        # 受傷和死亡效果
        self.damage_flash_timer = 0
        self.is_dead = False
        self.death_timer = 0

        # 燃燒狀態效果
        self.is_burning = False
        self.burn_timer = 0  # 燃燒剩餘時間
        self.burn_damage_timer = 0  # 燃燒傷害計時器
        self.burn_damage_interval = 60  # 燃燒傷害間隔（1秒 = 60幀）
        self.burn_particle_timer = 0  # 燃燒粒子效果計時器

        # 暈眩狀態效果
        self.is_stunned = False
        self.stunned_time = 0  # 暈眩剩餘時間（幀數）
        self.original_ai_state = None  # 記錄暈眩前的 AI 狀態

        # 視覺效果
        self.animation_frame = 0
        self.sprite_flip = False

        # 追蹤激活狀態 - 只有被玩家碰到後才會開始追蹤
        self.has_been_touched = False

    @abstractmethod
    def update_ai(self, player, platforms=None):
        """
        更新 AI 行為（抽象方法）\n
        \n
        子類別必須實作此方法，定義敵人的智能行為\n
        \n
        參數:\n
        player: 玩家物件\n
        platforms (list): 平台列表，用於移動和碰撞檢測\n
        """
        pass

    @abstractmethod
    def render(self, screen: pygame.Surface, camera_y: float):
        """
        繪製敵人（抽象方法）\n
        \n
        子類別必須實作此方法，定義敵人的外觀\n
        \n
        參數:\n
        screen (pygame.Surface): 螢幕表面\n
        camera_y (float): 攝影機偏移\n
        """
        pass

    @abstractmethod
    def attack_player(self, player) -> dict:
        """
        攻擊玩家（抽象方法）\n
        \n
        子類別必須實作此方法，定義攻擊行為\n
        \n
        參數:\n
        player: 玩家物件\n
        \n
        回傳:\n
        dict: 攻擊結果資訊\n
        """
        pass

    def update(self, player, platforms=None):
        """
        更新敵人狀態\n
        \n
        每幀更新敵人的所有狀態和行為\n
        \n
        參數:\n
        player: 玩家物件\n
        platforms (list): 當前關卡的平台列表，用於碰撞檢測\n
        """
        if self.is_dead:
            self._update_death_animation()
            return

        # 更新基本屬性
        self._update_base_properties()

        # 只有不在暈眩狀態時才更新 AI 行為
        if not self.is_stunned:
            self.update_ai(player, platforms)

        # 應用物理效果（傳入平台資料）
        self._apply_physics(platforms)

        # 更新動畫
        self._update_animation()

    def _update_base_properties(self):
        """
        更新基礎屬性\n
        \n
        處理所有敵人共通的狀態更新\n
        """
        # 更新攻擊冷卻
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        # 更新受傷閃爍效果
        if self.damage_flash_timer > 0:
            self.damage_flash_timer -= 1

        # 更新燃燒狀態
        self._update_burn_effect()

        # 更新暈眩狀態
        self._update_stun_effect()

        # 更新動畫幀
        self.animation_frame += 1
        if self.animation_frame >= 1000:
            self.animation_frame = 0

        # 更新重置保護時間
        if hasattr(self, "reset_protection_time") and self.reset_protection_time > 0:
            self.reset_protection_time -= 1
            if self.reset_protection_time <= 0:
                self.is_emergency_resetting = False

    def _apply_physics(self, platforms=None):
        """
        應用物理效果\n
        \n
        處理重力、移動和與平台的碰撞檢測\n
        同時處理移動平台的跟隨移動\n
        \n
        參數:\n
        platforms (list): 當前關卡的平台列表，用於碰撞檢測\n
        """
        # 如果站在移動平台上，先跟隨平台移動
        if self.standing_on_moving_platform:
            # 檢查是否還站在平台上
            if self._is_still_on_moving_platform(self.standing_on_moving_platform):
                # 跟隨移動平台
                platform_vel_x, platform_vel_y = (
                    self.standing_on_moving_platform.get_platform_velocity()
                )
                self.x += platform_vel_x
                # 垂直方向只有當平台向上移動時才跟隨
                if platform_vel_y < 0:  # 向上移動
                    self.y += platform_vel_y
            else:
                # 已經離開平台
                self.standing_on_moving_platform = None

        # 應用重力（除非在地面上）
        if not self.is_on_ground:
            self.velocity_y += 0.5  # 重力加速度

        # 限制下墜速度
        if self.velocity_y > 10:
            self.velocity_y = 10

        # 暫存舊位置用於碰撞回退
        old_x = self.x
        old_y = self.y

        # 應用水平移動
        self.x += self.velocity_x

        # 檢查水平碰撞（與平台的邊緣碰撞）
        if platforms:
            if self._check_horizontal_collision(platforms):
                self.x = old_x  # 撞到東西就回到原位
                self.velocity_x = 0  # 停止水平移動

        # 應用垂直移動
        self.y += self.velocity_y

        # 檢查垂直碰撞（著陸在平台上或撞到頭）
        if platforms:
            collision_result = self._check_vertical_collision(platforms)
            if collision_result:
                if collision_result == "landing":
                    # 著陸在平台上
                    self.velocity_y = 0
                    self.is_on_ground = True
                elif collision_result == "ceiling":
                    # 撞到天花板
                    self.y = old_y
                    self.velocity_y = 0
        else:
            # 沒有平台資料時使用簡化版本（向下兼容）
            self._apply_simple_physics()

        # 重置地面狀態（如果沒踩到任何平台）
        if not self._is_standing_on_platform(platforms):
            self.is_on_ground = False
            self.standing_on_moving_platform = None  # 清除移動平台狀態
            # 追蹤空中時間
            if not hasattr(self, "air_time"):
                self.air_time = 0
            self.air_time += 1
        else:
            # 重置空中時間
            if hasattr(self, "air_time"):
                self.air_time = 0

        # 死亡保護機制：根據不同情況設定觸發條件
        # 1. 如果掉得太低（超過起始位置300像素或低於地面水平）
        # 2. 如果在空中太久（可能卡在無限掉落循環）
        if (
            self.y > self.start_y + 300
            or self.y > 800  # 一般地面高度
            or (
                not self.is_on_ground
                and hasattr(self, "air_time")
                and self.air_time > 300
            )
        ):
            self._emergency_reset()

    def _apply_simple_physics(self):
        """
        簡化版物理系統（向下兼容）\n
        \n
        當沒有平台資料時使用，讓敵人回到起始高度\n
        """
        # 簡單的地面檢測（假設敵人都在地面上）
        if self.y > self.start_y:
            self.y = self.start_y
            self.velocity_y = 0
            self.is_on_ground = True
        else:
            self.is_on_ground = False

    def _check_horizontal_collision(self, platforms) -> bool:
        """
        檢查水平碰撞\n
        \n
        檢查敵人是否在水平移動時撞到平台的邊緣\n
        \n
        參數:\n
        platforms (list): 平台列表\n
        \n
        回傳:\n
        bool: 是否發生水平碰撞\n
        """
        if not platforms:
            return False

        enemy_rect = self.get_collision_rect()

        for platform in platforms:
            platform_rect = pygame.Rect(
                platform.x, platform.y, platform.width, platform.height
            )

            # 檢查是否與平台重疊
            if enemy_rect.colliderect(platform_rect):
                # 檢查是否是側面碰撞（不是從上方踩到）
                if (
                    abs(enemy_rect.centery - platform_rect.centery)
                    < platform_rect.height // 2
                ):
                    return True

        return False

    def _check_vertical_collision(self, platforms):
        """
        檢查垂直碰撞\n
        \n
        檢查敵人是否著陸在平台上或撞到天花板\n
        同時處理移動平台的跟隨移動\n
        \n
        參數:\n
        platforms (list): 平台列表\n
        \n
        回傳:\n
        str: 碰撞類型 ('landing', 'ceiling') 或 None\n
        """
        if not platforms:
            return None

        enemy_rect = self.get_collision_rect()

        for platform in platforms:
            platform_rect = pygame.Rect(
                platform.x, platform.y, platform.width, platform.height
            )

            if enemy_rect.colliderect(platform_rect):
                # 判斷是從上方還是下方碰撞
                if self.velocity_y > 0:  # 向下移動
                    # 檢查是否是從上方著陸
                    if enemy_rect.bottom - self.velocity_y <= platform_rect.top + 5:
                        # 將敵人放在平台正上方
                        self.y = platform_rect.top - self.height

                        # 如果是移動平台，讓敵人跟隨平台移動
                        if hasattr(platform, "get_platform_velocity"):
                            platform_vel_x, platform_vel_y = (
                                platform.get_platform_velocity()
                            )
                            # 只在水平方向跟隨移動平台，垂直方向由重力處理
                            self.x += platform_vel_x
                            # 記錄站在移動平台上的狀態
                            self.standing_on_moving_platform = platform
                        else:
                            self.standing_on_moving_platform = None

                        return "landing"
                elif self.velocity_y < 0:  # 向上移動
                    # 檢查是否撞到天花板
                    if enemy_rect.top - self.velocity_y >= platform_rect.bottom - 5:
                        return "ceiling"

        return None

    def _is_standing_on_platform(self, platforms) -> bool:
        """
        檢查敵人是否站在某個平台上\n
        \n
        用於更新 is_on_ground 狀態\n
        \n
        參數:\n
        platforms (list): 平台列表\n
        \n
        回傳:\n
        bool: 是否站在平台上\n
        """
        if not platforms:
            return False

        # 創建一個稍微向下延伸的檢測矩形
        check_rect = pygame.Rect(
            self.x + 2, self.y + self.height - 2, self.width - 4, 4
        )

        for platform in platforms:
            platform_rect = pygame.Rect(
                platform.x, platform.y, platform.width, platform.height
            )
            if check_rect.colliderect(platform_rect):
                return True

        return False

    def _is_still_on_moving_platform(self, platform) -> bool:
        """
        檢查敵人是否還站在指定的移動平台上\n
        \n
        用於判斷敵人是否應該繼續跟隨平台移動\n
        \n
        參數:\n
        platform: 移動平台物件\n
        \n
        回傳:\n
        bool: 是否還站在平台上\n
        """
        if not platform:
            return False

        # 創建檢測矩形（稍微向下延伸）
        check_rect = pygame.Rect(
            self.x + 2, self.y + self.height - 2, self.width - 4, 6
        )

        platform_rect = pygame.Rect(
            platform.x, platform.y, platform.width, platform.height
        )

        # 檢查水平重疊和垂直接觸
        horizontal_overlap = (
            check_rect.right > platform_rect.left
            and check_rect.left < platform_rect.right
        )
        vertical_contact = abs(check_rect.bottom - platform_rect.top) <= 5

        return horizontal_overlap and vertical_contact

    def _update_animation(self):
        """
        更新動畫狀態\n
        \n
        根據移動方向和狀態更新動畫\n
        """
        # 根據移動方向更新面向
        if self.velocity_x > 0:
            self.facing_direction = 1
            self.sprite_flip = False
        elif self.velocity_x < 0:
            self.facing_direction = -1
            self.sprite_flip = True

    def _update_burn_effect(self):
        """
        更新燃燒狀態效果\n
        \n
        處理敵人燃燒時的持續傷害和視覺效果\n
        """
        if not self.is_burning or self.is_dead:
            return

        # 減少燃燒剩餘時間
        if self.burn_timer > 0:
            self.burn_timer -= 1

            # 更新燃燒傷害計時器
            self.burn_damage_timer += 1

            # 每隔一定時間造成燃燒傷害
            if self.burn_damage_timer >= self.burn_damage_interval:
                # 造成燃燒傷害（不會觸發額外的受傷效果）
                self._apply_burn_damage()
                self.burn_damage_timer = 0  # 重置傷害計時器

            # 更新燃燒粒子效果計時器
            self.burn_particle_timer += 1
        else:
            # 燃燒時間結束，移除燃燒狀態
            self.is_burning = False
            self.burn_damage_timer = 0
            self.burn_particle_timer = 0

    def _apply_burn_damage(self):
        """
        施加燃燒傷害\n
        \n
        對敵人造成燃燒的持續傷害，不觸發額外效果\n
        """
        burn_damage = 3  # 每次燃燒傷害

        # 直接減少血量，不觸發 take_damage 的額外效果
        self.health -= burn_damage

        # 血量不能低於 0
        if self.health <= 0:
            self.health = 0
            self.is_dead = True
            self.ai_state = "dead"
            self.is_burning = False  # 死亡時移除燃燒狀態

        # 輕微的視覺反饋（較短的閃爍）
        self.damage_flash_timer = 5  # 燃燒傷害的閃爍時間較短

    def _update_stun_effect(self):
        """
        更新暈眩狀態效果\n
        \n
        處理敵人暈眩時的狀態管理\n
        """
        if not self.is_stunned or self.is_dead:
            return

        # 減少暈眩剩餘時間
        if self.stunned_time > 0:
            self.stunned_time -= 1

            # 暈眩期間停止移動
            self.velocity_x = 0
        else:
            # 暈眩時間結束，恢復正常狀態
            self.is_stunned = False
            # 恢復之前的 AI 狀態（如果有記錄的話）
            if self.original_ai_state:
                self.ai_state = self.original_ai_state
                self.original_ai_state = None

    def apply_stun(self, duration: int):
        """
        施加暈眩效果\n
        \n
        讓敵人進入暈眩狀態，暫停 AI 行為\n
        \n
        參數:\n
        duration (int): 暈眩持續時間（幀數）\n
        """
        if self.is_dead:
            return

        # 記錄當前 AI 狀態（如果不是已經在暈眩中）
        if not self.is_stunned:
            self.original_ai_state = self.ai_state

        # 設定暈眩狀態
        self.is_stunned = True
        self.stunned_time = max(self.stunned_time, duration)  # 使用較長的持續時間

        # 立即停止移動
        self.velocity_x = 0
        """
        更新死亡動畫\n
        \n
        處理敵人死亡後的視覺效果\n
        """
        self.death_timer += 1

    def _update_death_animation(self):
        """
        更新死亡動畫\n
        \n
        處理敵人死亡後的視覺效果\n
        """
        self.death_timer += 1

        # 死亡後逐漸消失
        if self.death_timer > 120:  # 2秒後完全消失
            # 這裡可以標記為可以從遊戲中移除
            pass

    def get_collision_rect(self) -> pygame.Rect:
        """
        取得敵人的碰撞矩形\n
        \n
        回傳:\n
        pygame.Rect: 用於碰撞檢測的矩形\n
        """
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def get_distance_to_player(self, player) -> float:
        """
        計算到玩家的距離\n
        \n
        參數:\n
        player: 玩家物件\n
        \n
        回傳:\n
        float: 到玩家的直線距離\n
        """
        dx = player.x - self.x
        dy = player.y - self.y
        return math.sqrt(dx * dx + dy * dy)

    def can_see_player(self, player) -> bool:
        """
        檢查是否能看見玩家\n
        \n
        只有在被玩家碰到過後才會開始追蹤玩家\n
        簡化的視線檢查，實際遊戲可能需要射線檢測\n
        \n
        參數:\n
        player: 玩家物件\n
        \n
        回傳:\n
        bool: 是否在視線範圍內且已被激活追蹤\n
        """
        # 如果還沒有被玩家碰到過，就看不見玩家（不會追蹤）
        if not self.has_been_touched:
            return False

        distance = self.get_distance_to_player(player)
        return distance <= self.detection_range

    def can_attack_player(self, player) -> bool:
        """
        檢查是否能攻擊玩家\n
        \n
        參數:\n
        player: 玩家物件\n
        \n
        回傳:\n
        bool: 是否在攻擊範圍內且冷卻結束\n
        """
        if self.attack_cooldown > 0:
            return False

        # 掉落中的敵人不能攻擊
        if not self.is_on_ground:
            return False

        # 正在進行緊急重置的敵人不能攻擊
        if hasattr(self, "is_emergency_resetting") and self.is_emergency_resetting:
            return False

        distance = self.get_distance_to_player(player)
        return distance <= self.attack_range

    def take_damage(self, damage: int):
        """
        受到傷害\n
        \n
        處理敵人受傷邏輯\n
        \n
        參數:\n
        damage (int): 受到的傷害數值\n
        """
        self.health -= damage
        self.damage_flash_timer = 10  # 受傷閃爍 10 幀

        # 血量不能低於 0
        if self.health <= 0:
            self.health = 0
            self.is_dead = True
            self.ai_state = "dead"

        # 受傷時切換到追蹤狀態（如果不是死亡）
        if not self.is_dead and self.ai_state == "patrol":
            self.ai_state = "chase"

    def move_towards_player(self, player):
        """
        朝玩家方向移動\n
        \n
        計算並設定朝向玩家的移動速度\n
        \n
        參數:\n
        player: 玩家物件\n
        """
        dx = player.x - self.x

        # 只考慮水平移動（簡化處理）
        if abs(dx) > 5:  # 避免過度微調
            if dx > 0:
                self.velocity_x = self.speed
            else:
                self.velocity_x = -self.speed
        else:
            self.velocity_x = 0

    def patrol_movement(self, platforms=None):
        """
        巡邏移動邏輯\n
        \n
        在指定範圍內來回移動，並避免掉下懸崖\n
        \n
        參數:\n
        platforms (list): 平台列表，用於懸崖檢測\n
        """
        # 首先檢查前方是否有懸崖（最高優先級）
        if platforms and self._is_cliff_ahead(platforms):
            # 前方是懸崖，立即轉向並停止當前移動
            self.patrol_direction *= -1
            self.velocity_x = 0  # 立即停止移動
            return  # 這回合不移動，避免衝出平台

        # 檢查是否到達巡邏邊界
        if self.x <= self.patrol_center_x - self.patrol_range:
            self.patrol_direction = 1
        elif self.x >= self.patrol_center_x + self.patrol_range:
            self.patrol_direction = -1

        # 設定巡邏速度
        self.velocity_x = self.patrol_direction * self.speed * 0.5  # 巡邏時慢一些

    def _is_cliff_ahead(self, platforms) -> bool:
        """
        檢查前方是否有懸崖\n
        \n
        檢測敵人前方一小段距離內是否還有平台支撐\n
        \n
        參數:\n
        platforms (list): 平台列表\n
        \n
        回傳:\n
        bool: 前方是否是懸崖\n
        """
        if not platforms:
            return False

        # 檢測前方距離（考慮敵人的寬度和速度）
        check_distance = max(self.width + 10, 40)  # 至少40像素，或敵人寬度+10

        # 計算檢測位置（敵人前方邊緣外一點）
        if self.patrol_direction > 0:  # 向右移動
            check_x = self.x + self.width + 5  # 右邊緣外5像素
        else:  # 向左移動
            check_x = self.x - 5  # 左邊緣外5像素

        # 檢測腳底位置（稍微往下一點確保能檢測到平台）
        check_y = self.y + self.height + 2

        # 創建較大的檢測矩形，確保不會漏檢
        check_rect = pygame.Rect(check_x - 2, check_y - 2, 10, 10)

        # 檢查是否有平台支撐這個檢測區域
        for platform in platforms:
            platform_rect = pygame.Rect(
                platform.x, platform.y, platform.width, platform.height
            )
            if check_rect.colliderect(platform_rect):
                return False  # 有平台，不是懸崖

        return True  # 沒有平台，是懸崖

    def _emergency_reset(self):
        """
        緊急重置敵人位置\n
        \n
        當敵人掉出地圖或遇到嚴重問題時，將其重置到安全位置\n
        """
        # 標記正在重置，避免攻擊
        self.is_emergency_resetting = True

        # 重置到起始位置
        self.x = self.start_x
        self.y = self.start_y

        # 清空所有移動狀態
        self.velocity_x = 0
        self.velocity_y = 0
        self.is_on_ground = True

        # 重置巡邏方向，避免再次掉下
        self.patrol_direction = 1

        # 重置空中時間
        if hasattr(self, "air_time"):
            self.air_time = 0

        # 稍微減少血量作為懲罰
        if self.health > 10:
            self.health -= 5

        # 短暫的重置保護時間（2秒）
        self.reset_protection_time = 120

    def reset(self):
        """
        重置敵人狀態\n
        \n
        將敵人恢復到初始狀態，用於關卡重置\n
        """
        self.x = self.start_x
        self.y = self.start_y
        self.health = self.max_health
        self.is_dead = False
        self.ai_state = "patrol"
        self.velocity_x = 0
        self.velocity_y = 0
        self.attack_cooldown = 0
        self.damage_flash_timer = 0
        self.death_timer = 0
        self.animation_frame = 0
        self.facing_direction = 1
        self.patrol_direction = 1

        # 重置燃燒狀態
        self.is_burning = False
        self.burn_timer = 0
        self.burn_damage_timer = 0
        self.burn_particle_timer = 0

        # 重置追蹤激活狀態
        self.has_been_touched = False

    def adjust_patrol_range_for_platforms(self, platforms):
        """
        根據平台調整巡邏範圍\n
        \n
        檢查當前巡邏範圍是否會導致敵人掉下平台，如果會就縮小範圍\n
        \n
        參數:\n
        platforms (list): 當前關卡的平台列表\n
        """
        if not platforms:
            return

        # 找到敵人當前站立的平台
        current_platform = None
        enemy_rect = self.get_collision_rect()

        for platform in platforms:
            platform_rect = pygame.Rect(
                platform.x, platform.y, platform.width, platform.height
            )
            # 檢查敵人是否在這個平台上（稍微放寬檢測範圍）
            enemy_foot_rect = pygame.Rect(
                self.x, self.y + self.height - 5, self.width, 10
            )
            if enemy_foot_rect.colliderect(platform_rect):
                current_platform = platform
                break

        if current_platform:
            # 計算安全的巡邏範圍
            platform_left = current_platform.x
            platform_right = current_platform.x + current_platform.width

            # 保留一些邊距，避免走到平台邊緣
            margin = max(self.width, 20)
            safe_left = platform_left + margin
            safe_right = platform_right - margin - self.width

            # 計算從敵人位置到平台邊界的最大安全距離
            max_left_range = max(0, self.x - safe_left)
            max_right_range = max(0, safe_right - self.x)

            # 取兩邊的最小值作為對稱的巡邏範圍
            safe_patrol_range = min(max_left_range, max_right_range, self.patrol_range)

            # 確保最小巡邏範圍不會太小
            safe_patrol_range = max(safe_patrol_range, 30)

            if safe_patrol_range < self.patrol_range:
                self.patrol_range = safe_patrol_range
                # 也要更新巡邏中心點，確保敵人不會超出安全範圍
                self.patrol_center_x = self.x

    def is_in_screen_bounds(self, screen: pygame.Surface, camera_y: float) -> bool:
        """
        檢查敵人是否在螢幕可見範圍內\n
        \n
        用於優化渲染效能\n
        \n
        參數:\n
        screen (pygame.Surface): 螢幕表面\n
        camera_y (float): 攝影機偏移\n
        \n
        回傳:\n
        bool: 是否在可見範圍內\n
        """
        screen_y = self.y - camera_y + screen.get_height() // 2

        return (
            -self.height < screen_y < screen.get_height() + self.height
            and -self.width < self.x < screen.get_width() + self.width
        )
