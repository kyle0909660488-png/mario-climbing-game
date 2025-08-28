######################載入套件######################
import pygame
import random
from typing import Dict, List, Optional


######################裝備管理系統######################
class EquipmentManager:
    """
    裝備系統管理器\n
    \n
    負責管理遊戲中的套裝系統：\n
    1. 套裝的獲得和裝備\n
    2. 套裝效果的啟用和管理\n
    3. 套裝組合效果計算\n
    4. 裝備的掉落和收集機制\n
    \n
    套裝類型:\n
    - 火焰套裝：可發射火球攻擊\n
    - 冰霜套裝：攻擊可減速敵人\n
    - 影子套裝：短時間隱身能力\n
    - 坦克套裝：增加血量與防禦力\n
    \n
    屬性:\n
    equipped_sets (Dict): 當前裝備的套裝\n
    available_sets (Dict): 可用的套裝清單\n
    set_effects (Dict): 各套裝的效果配置\n
    """

    def __init__(self):
        """
        初始化裝備管理系統\n
        \n
        設定套裝資料和效果配置\n
        """
        # 當前裝備的套裝（套裝名稱 -> 件數）
        self.equipped_sets = {}

        # 玩家擁有的套裝件數（套裝名稱 -> 件數）
        self.owned_sets = {"fire": 0, "ice": 0, "shadow": 0, "tank": 0}

        # 套裝效果配置
        self.set_effects = {
            "fire": {
                "name": "火焰套裝",
                "color": (255, 100, 0),
                "effects": {
                    1: {"attack_bonus": 5, "description": "攻擊力 +5"},
                    2: {"fire_attack": True, "description": "攻擊附帶火焰傷害"},
                    3: {"fire_immunity": True, "description": "火焰免疫"},
                    4: {"fire_ball_skill": True, "description": "可發射火球"},
                },
            },
            "ice": {
                "name": "冰霜套裝",
                "color": (100, 200, 255),
                "effects": {
                    1: {"speed_bonus": 1, "description": "移動速度 +1"},
                    2: {"slow_attack": True, "description": "攻擊可減速敵人"},
                    3: {"ice_immunity": True, "description": "冰面不滑"},
                    4: {"freeze_skill": True, "description": "可凍結敵人"},
                },
            },
            "shadow": {
                "name": "影子套裝",
                "color": (80, 80, 80),
                "effects": {
                    1: {"jump_bonus": 2, "description": "跳躍力 +2"},
                    2: {"stealth_walk": True, "description": "移動時更安靜"},
                    3: {"damage_reduction": 0.2, "description": "受傷減少 20%"},
                    4: {"invisibility_skill": True, "description": "短時間隱身"},
                },
            },
            "tank": {
                "name": "坦克套裝",
                "color": (150, 150, 150),
                "effects": {
                    1: {"health_bonus": 25, "description": "最大血量 +25"},
                    2: {"defense_bonus": 0.1, "description": "物理傷害減少 10%"},
                    3: {"knockback_resistance": True, "description": "擊退抗性"},
                    4: {"shield_skill": True, "description": "護盾技能"},
                },
            },
        }

        # 套裝技能冷卻時間
        self.skill_cooldowns = {
            "fire_ball": 0,
            "freeze": 0,
            "invisibility": 0,
            "shield": 0,
        }

        # 當前啟用的效果
        self.active_effects = {}

        # 技能狀態
        self.invisibility_timer = 0
        self.shield_timer = 0

    def add_set_piece(self, set_name: str) -> bool:
        """
        添加套裝件數\n
        \n
        當玩家獲得套裝時調用此方法\n
        \n
        參數:\n
        set_name (str): 套裝名稱\n
        \n
        回傳:\n
        bool: 是否成功添加\n
        """
        if set_name in self.owned_sets and self.owned_sets[set_name] < 4:
            self.owned_sets[set_name] += 1
            self._update_equipped_effects()
            return True
        return False

    def _update_equipped_effects(self):
        """
        更新裝備效果\n
        \n
        根據當前套裝件數計算啟用的效果\n
        """
        self.active_effects.clear()

        for set_name, count in self.owned_sets.items():
            if count > 0 and set_name in self.set_effects:
                set_config = self.set_effects[set_name]

                # 根據件數啟用對應效果
                for pieces_needed in range(1, count + 1):
                    if pieces_needed in set_config["effects"]:
                        effect_data = set_config["effects"][pieces_needed]

                        # 將效果加入啟用清單
                        for effect_name, effect_value in effect_data.items():
                            if effect_name != "description":
                                if effect_name not in self.active_effects:
                                    self.active_effects[effect_name] = effect_value
                                else:
                                    # 數值型效果疊加
                                    if isinstance(effect_value, (int, float)):
                                        self.active_effects[effect_name] += effect_value

    def apply_effects_to_player(self, player):
        """
        將套裝效果應用到玩家身上\n
        \n
        修改玩家的屬性以反映套裝效果\n
        \n
        參數:\n
        player: 玩家物件\n
        """
        # 攻擊力加成
        if "attack_bonus" in self.active_effects:
            player.base_attack = getattr(player, "base_attack", player.attack_damage)
            player.attack_damage = (
                player.base_attack + self.active_effects["attack_bonus"]
            )

        # 速度加成
        if "speed_bonus" in self.active_effects:
            player.base_speed = getattr(player, "base_speed", player.speed)
            player.speed = player.base_speed + self.active_effects["speed_bonus"]

        # 跳躍力加成
        if "jump_bonus" in self.active_effects:
            player.base_jump_power = getattr(
                player, "base_jump_power", player.jump_power
            )
            player.jump_power = (
                player.base_jump_power + self.active_effects["jump_bonus"]
            )

        # 血量加成（只在第一次應用時增加）
        if "health_bonus" in self.active_effects:
            if not hasattr(player, "base_max_health"):
                player.base_max_health = player.max_health
                player.max_health += self.active_effects["health_bonus"]
                player.health += self.active_effects["health_bonus"]  # 同時恢復血量

    def process_attack_effects(self, player, target_enemy) -> Dict:
        """
        處理攻擊時的套裝效果\n
        \n
        當玩家攻擊敵人時觸發的特殊效果\n
        \n
        參數:\n
        player: 玩家物件\n
        target_enemy: 被攻擊的敵人\n
        \n
        回傳:\n
        Dict: 攻擊效果資訊\n
        """
        effects = {"additional_damage": 0, "special_effects": []}

        # 火焰攻擊效果
        if "fire_attack" in self.active_effects:
            effects["additional_damage"] += 10
            effects["special_effects"].append("burn_damage")

        # 冰霜攻擊效果
        if "slow_attack" in self.active_effects:
            if hasattr(target_enemy, "apply_slow_effect"):
                target_enemy.apply_slow_effect(120)  # 2秒減速
            effects["special_effects"].append("slow_effect")

        return effects

    def process_damage_reduction(self, incoming_damage: int) -> int:
        """
        處理傷害減免效果\n
        \n
        計算套裝提供的傷害減免\n
        \n
        參數:\n
        incoming_damage (int): 原始傷害\n
        \n
        回傳:\n
        int: 減免後的傷害\n
        """
        damage = incoming_damage

        # 物理傷害減免
        if "defense_bonus" in self.active_effects:
            damage = int(damage * (1 - self.active_effects["defense_bonus"]))

        # 影子套裝傷害減免
        if "damage_reduction" in self.active_effects:
            damage = int(damage * (1 - self.active_effects["damage_reduction"]))

        # 護盾技能啟用時
        if self.shield_timer > 0:
            damage = max(1, damage // 2)  # 傷害減半，最少1點

        return max(0, damage)

    def use_skill(self, skill_name: str, player) -> bool:
        """
        使用套裝技能\n
        \n
        觸發特殊技能效果\n
        \n
        參數:\n
        skill_name (str): 技能名稱\n
        player: 玩家物件\n
        \n
        回傳:\n
        bool: 是否成功使用技能\n
        """
        # 檢查冷卻時間
        if skill_name in self.skill_cooldowns and self.skill_cooldowns[skill_name] > 0:
            return False

        if skill_name == "fire_ball" and "fire_ball_skill" in self.active_effects:
            return self._use_fire_ball_skill(player)
        elif skill_name == "freeze" and "freeze_skill" in self.active_effects:
            return self._use_freeze_skill(player)
        elif (
            skill_name == "invisibility" and "invisibility_skill" in self.active_effects
        ):
            return self._use_invisibility_skill(player)
        elif skill_name == "shield" and "shield_skill" in self.active_effects:
            return self._use_shield_skill(player)

        return False

    def _use_fire_ball_skill(self, player) -> bool:
        """
        使用火球技能\n
        \n
        發射火球攻擊，傷害基於玩家攻擊力\n
        """
        # 確認火球管理器存在
        if hasattr(player, "fireball_manager") and player.fireball_manager:
            # 決定發射方向
            if hasattr(player, "last_facing_direction"):
                direction = player.last_facing_direction
            elif abs(player.velocity_x) > 0.1:
                direction = 1 if player.velocity_x > 0 else -1
            else:
                direction = 1  # 預設向右

            # 計算發射位置
            launch_x = player.x + player.width // 2
            launch_y = player.y + player.height // 2

            # 發射火球（使用玩家攻擊力）
            player.fireball_manager.create_fireball(
                launch_x, launch_y, direction, player.attack_damage
            )

            self.skill_cooldowns["fire_ball"] = 180  # 3秒冷卻
            return True

        return False

    def _use_freeze_skill(self, player) -> bool:
        """
        使用冰凍技能\n
        \n
        發射冰球攻擊，傷害基於玩家攻擊力\n
        """
        # 確認冰球管理器存在
        if hasattr(player, "iceball_manager") and player.iceball_manager:
            # 決定發射方向
            if hasattr(player, "last_facing_direction"):
                direction = player.last_facing_direction
            elif abs(player.velocity_x) > 0.1:
                direction = 1 if player.velocity_x > 0 else -1
            else:
                direction = 1  # 預設向右

            # 計算發射位置
            launch_x = player.x + player.width // 2
            launch_y = player.y + player.height // 2

            # 發射冰球（使用玩家攻擊力）
            player.iceball_manager.create_iceball(
                launch_x, launch_y, direction, player.attack_damage
            )

            self.skill_cooldowns["freeze"] = 300  # 5秒冷卻
            return True

        return False

    def _use_invisibility_skill(self, player) -> bool:
        """
        使用隱身技能\n
        \n
        讓玩家短時間隱身\n
        """
        self.invisibility_timer = 180  # 3秒隱身
        self.skill_cooldowns["invisibility"] = 600  # 10秒冷卻
        return True

    def _use_shield_skill(self, player) -> bool:
        """
        使用護盾技能\n
        \n
        啟用護盾效果\n
        """
        self.shield_timer = 300  # 5秒護盾
        self.skill_cooldowns["shield"] = 480  # 8秒冷卻
        return True

    def update(self, player):
        """
        更新裝備系統狀態\n
        \n
        每幀更新技能冷卻、效果計時器等\n
        \n
        參數:\n
        player: 玩家物件\n
        """
        # 更新技能冷卻時間
        for skill_name in self.skill_cooldowns:
            if self.skill_cooldowns[skill_name] > 0:
                self.skill_cooldowns[skill_name] -= 1

        # 更新技能效果計時器
        if self.invisibility_timer > 0:
            self.invisibility_timer -= 1

        if self.shield_timer > 0:
            self.shield_timer -= 1

        # 應用持續效果
        self.apply_effects_to_player(player)

    def is_invisible(self) -> bool:
        """
        檢查玩家是否處於隱身狀態\n
        \n
        回傳:\n
        bool: 是否隱身中\n
        """
        return self.invisibility_timer > 0

    def has_shield(self) -> bool:
        """
        檢查玩家是否有護盾保護\n
        \n
        回傳:\n
        bool: 是否有護盾\n
        """
        return self.shield_timer > 0

    def get_equipment_info(self) -> Dict:
        """
        取得裝備資訊\n
        \n
        回傳當前套裝狀態和效果\n
        \n
        回傳:\n
        Dict: 裝備資訊\n
        """
        info = {
            "owned_sets": self.owned_sets.copy(),
            "active_effects": self.active_effects.copy(),
            "skill_cooldowns": {k: v for k, v in self.skill_cooldowns.items() if v > 0},
            "active_skills": {
                "invisibility": self.invisibility_timer,
                "shield": self.shield_timer,
            },
        }
        return info

    def reset_equipment(self):
        """
        重置裝備系統\n
        \n
        清空所有套裝和效果，用於遊戲重新開始\n
        """
        self.owned_sets = {set_name: 0 for set_name in self.owned_sets}
        self.active_effects.clear()
        self.skill_cooldowns = {skill: 0 for skill in self.skill_cooldowns}
        self.invisibility_timer = 0
        self.shield_timer = 0

    def generate_random_drop(self) -> Optional[str]:
        """
        生成隨機套裝掉落\n
        \n
        當擊敗敵人時可能掉落套裝件\n
        \n
        回傳:\n
        Optional[str]: 掉落的套裝名稱，None 表示無掉落\n
        """
        # 30% 機率掉落套裝
        if random.random() < 0.3:
            # 優先掉落件數較少的套裝
            available_sets = [
                (name, count) for name, count in self.owned_sets.items() if count < 4
            ]

            if available_sets:
                # 根據已有件數的反比重加權
                weights = [5 - count for name, count in available_sets]
                total_weight = sum(weights)

                rand_num = random.uniform(0, total_weight)
                current_weight = 0

                for i, (set_name, count) in enumerate(available_sets):
                    current_weight += weights[i]
                    if rand_num <= current_weight:
                        return set_name

        return None
