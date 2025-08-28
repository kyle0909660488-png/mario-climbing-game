######################載入套件######################
import pygame
import sys
from typing import Dict, List, Tuple
from src.characters.player import Player
from src.levels.level_manager import LevelManager
from src.ui.game_ui import GameUI
from src.equipment.equipment_manager import EquipmentManager
from src.equipment.equipment_item import EquipmentDropManager
from src.projectiles.fireball import FireballManager
from src.projectiles.iceball import IceballManager

######################遊戲設定常數######################
# 畫面設定
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60

# 遊戲顏色
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 100, 200)
GREEN = (0, 200, 0)
RED = (200, 0, 0)

# 物理設定
GRAVITY = 0.8
MAX_FALL_SPEED = 15


######################主要遊戲類別######################
class MarioClimbingGame:
    """
    瑪莉歐攀爬遊戲主控制器\n
    \n
    負責管理整個遊戲的運行，包括：\n
    1. 遊戲初始化和資源載入\n
    2. 主遊戲循環管理\n
    3. 各個系統的協調（角色、關卡、UI、裝備）\n
    4. 遊戲狀態管理（選單、遊戲中、暫停、結束）\n
    \n
    屬性:\n
    screen (pygame.Surface): 主要顯示畫面\n
    clock (pygame.time.Clock): 遊戲時鐘，控制幀率\n
    running (bool): 遊戲是否持續運行\n
    game_state (str): 當前遊戲狀態（'menu', 'playing', 'paused', 'game_over', 'victory'）\n
    player (Player): 玩家角色物件\n
    level_manager (LevelManager): 關卡管理器\n
    ui (GameUI): 使用者介面管理器\n
    equipment_manager (EquipmentManager): 裝備系統管理器\n
    \n
    遊戲流程:\n
    1. 初始化 → 2. 角色選擇 → 3. 遊戲進行 → 4. 結算\n
    """

    def __init__(self):
        """
        初始化遊戲系統\n
        \n
        設定 pygame 基本環境、建立視窗、初始化各個遊戲系統模組
        """
        # pygame 系統初始化
        pygame.init()

        # 建立遊戲視窗
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("瑪莉歐攀爬遊戲")

        # 時鐘物件用來控制遊戲幀率
        self.clock = pygame.time.Clock()

        # 遊戲狀態控制
        self.running = True
        self.game_state = "menu"  # 一開始先顯示選單畫面

        # 初始化各個遊戲系統（先設為 None，等選角完成後才建立）
        self.player = None
        self.level_manager = LevelManager()
        self.ui = GameUI(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.equipment_manager = EquipmentManager()
        self.equipment_drop_manager = EquipmentDropManager()
        self.fireball_manager = FireballManager()  # 火球管理系統
        self.iceball_manager = IceballManager()  # 冰球管理系統

        # 選角相關變數
        self.selected_character_index = 0  # 目前選中的角色編號

        # 相機系統變數
        self.camera_y = 0  # 當前相機 Y 位置
        self.camera_smoothing = (
            0.08  # 相機平滑跟隨速度（0.05-0.2 之間，數值越小越平滑但反應越慢）
        )

    def handle_events(self):
        """
        處理所有使用者輸入事件\n
        \n
        根據不同遊戲狀態處理對應的事件：\n
        - 選單狀態：角色選擇、開始遊戲\n
        - 遊戲狀態：玩家操作、暫停\n
        - 暫停狀態：繼續遊戲、返回選單\n
        \n
        按鍵對應:\n
        - ESC: 暫停/離開遊戲\n
        - WASD/方向鍵: 玩家移動（遊戲中）\n
        - 空白鍵: 跳躍（推薦，避免按鍵衝突）\n
        - R: 加速衝刺（遊戲中）\n
        - C: 攻擊（遊戲中）\n
        - 方向鍵: 角色選擇（選單中）\n
        - ENTER: 確認選擇（選單中）\n
        """
        for event in pygame.event.get():
            # 點擊關閉按鈕就結束遊戲
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                # ESC 鍵按下回到選單（若在選單則不變）
                if event.key == pygame.K_ESCAPE:
                    # 如果在遊戲中或暫停或結束畫面，回到選單
                    self._return_to_menu()
                    continue

                # Q 鍵按下在遊戲中重置當前關卡
                if event.key == pygame.K_q:
                    if self.game_state == "playing" and self.player:
                        self._reset_current_level()
                    # 如果在遊戲結束畫面，也接受 Q 重新開始當前關卡
                    elif self.game_state == "game_over":
                        self._reset_current_level()
                    continue
                else:
                    # 選單狀態的按鍵處理
                    if self.game_state == "menu":
                        if event.key == pygame.K_LEFT:
                            # 選擇前一個角色（循環選擇）
                            self.selected_character_index = (
                                self.selected_character_index - 1
                            ) % 3
                        elif event.key == pygame.K_RIGHT:
                            # 選擇下一個角色（循環選擇）
                            self.selected_character_index = (
                                self.selected_character_index + 1
                            ) % 3
                        elif event.key == pygame.K_RETURN:
                            # 按 Enter 開始遊戲，建立選定的角色
                            self.start_game_with_character(
                                self.selected_character_index
                            )

                    # 暫停狀態的按鍵處理
                    elif self.game_state == "paused":
                        if event.key == pygame.K_SPACE:
                            self.game_state = "playing"  # 空白鍵繼續遊戲

                    # 勝利畫面的按鍵處理
                    elif self.game_state == "victory":
                        if event.key == pygame.K_SPACE:
                            self.restart_game()  # 重新開始遊戲
                        elif event.key == pygame.K_ESCAPE:
                            self.game_state = "menu"  # 回到主選單

    def start_game_with_character(self, character_type: int):
        """
        使用選定的角色開始遊戲\n
        \n
        根據角色類型建立對應的玩家物件，每種角色有不同的基礎能力：\n
        0: 平衡型角色（標準速度和跳躍）\n
        1: 跳躍型角色（二段跳能力）\n
        2: 坦克型角色（血量多，移動慢）\n
        \n
        參數:\n
        character_type (int): 角色類型編號，範圍 0-2\n
        """
        # 建立選定的角色
        start_x = SCREEN_WIDTH // 2
        start_y = SCREEN_HEIGHT - 100  # 從畫面底部開始
        self.player = Player(start_x, start_y, character_type)

        # 初始化相機位置到玩家位置，避免開始時的跳躍
        self.camera_y = self.player.y - SCREEN_HEIGHT // 2

        # 讓玩家能夠使用裝備系統和投射物攻擊
        self.player.set_equipment_manager(self.equipment_manager)
        self.player.set_fireball_manager(self.fireball_manager)
        self.player.set_iceball_manager(self.iceball_manager)

        # 重置關卡管理器到第一關
        self.level_manager.reset_to_first_level()

        # 清空裝備，重新開始
        self.equipment_manager.reset_equipment()
        self.equipment_drop_manager.clear_all()
        self.fireball_manager.clear_all()  # 清空所有火球
        self.iceball_manager.clear_all()  # 清空所有冰球

        # 切換到遊戲狀態
        self.game_state = "playing"

    def _return_to_menu(self):
        """
        將遊戲狀態切換回選單，並重置部分暫存狀態
        """
        # 停止遊戲進行，回到選單畫面
        self.game_state = "menu"

        # 清除玩家物件（選單中不需要持續玩家狀態）
        self.player = None

        # 可選：清空掉落與裝備（保持玩家選擇狀態）
        self.equipment_drop_manager.clear_all()
        self.fireball_manager.clear_all()  # 回到選單時清空火球
        self.iceball_manager.clear_all()  # 回到選單時清空冰球

    def _reset_current_level(self):
        """
        重置目前的關卡並將玩家重置到該關卡的起始位置與初始狀態
        """
        # 取得當前關卡物件
        current_level = self.level_manager.get_current_level()

        # 重置關卡結構與狀態
        current_level.reset()

        # 如果玩家不存在（例如從遊戲結束畫面按下 Q），建立新玩家並放置在起點
        if not self.player:
            start_x = current_level.player_start_x
            start_y = current_level.player_start_y
            # 使用先前選定的角色索引，若不存在則使用 0
            character_index = getattr(self, "selected_character_index", 0)
            self.player = Player(start_x, start_y, character_index)
            self.player.set_equipment_manager(self.equipment_manager)
            self.player.set_fireball_manager(self.fireball_manager)  # 設定火球管理器
            self.player.set_iceball_manager(self.iceball_manager)  # 設定冰球管理器
        else:
            # 將玩家位置、速度與狀態重置
            self.player.x = current_level.player_start_x
            self.player.y = current_level.player_start_y
            self.player.velocity_x = 0
            self.player.velocity_y = 0
            self.player.is_on_ground = False
            self.player.can_double_jump = self.player.has_double_jump_ability
            self.player.is_crouching = False
            self.player.is_sprinting = False
            self.player.attack_cooldown = 0
            self.player.is_attacking = False
            self.player.invulnerability_time = 0
            self.player.previous_jump_key_pressed = False  # 重置按鍵狀態
            self.player.jump_buffer_time = 0  # 重置跳躍緩衝

        # 重置相機位置到玩家新位置，避免重置後的跳躍
        self.camera_y = self.player.y - SCREEN_HEIGHT // 2

        # 重置裝備掉落（保留玩家已裝備的套裝，但清空場上的掉落物）
        self.equipment_drop_manager.clear_all()
        self.fireball_manager.clear_all()  # 重置時清空所有火球
        self.iceball_manager.clear_all()  # 重置時清空所有冰球

    def update(self):
        """
        更新遊戲邏輯\n
        \n
        根據當前遊戲狀態執行對應的更新邏輯：\n
        - 選單狀態：只更新 UI 動畫\n
        - 遊戲狀態：更新所有遊戲物件\n
        - 暫停狀態：暫停所有更新\n
        \n
        遊戲物件更新順序:\n
        1. 玩家輸入和移動\n
        2. 重力和碰撞檢測\n
        3. 敵人和陷阱更新\n
        4. 裝備效果更新\n
        5. UI 資訊更新\n
        """
        if self.game_state == "playing" and self.player:
            # 取得當前按住的按鍵狀態
            keys = pygame.key.get_pressed()

            # 取得當前關卡資料
            current_level = self.level_manager.get_current_level()

            # 讓玩家根據按鍵狀態更新（傳遞平台資料用於蹲下碰撞檢測）
            self.player.handle_input(keys, current_level.platforms)

            # 更新玩家物理狀態（移動、重力、碰撞）
            # 建立包含移動平台的完整平台清單
            all_platforms = current_level.platforms.copy()

            # 把移動平台也加入平台清單，讓玩家可以站在上面
            from src.traps.moving_platform import MovingPlatform

            for trap in current_level.traps:
                if isinstance(trap, MovingPlatform):
                    all_platforms.append(trap)

            self.player.update(all_platforms, current_level.traps)

            # 更新當前關卡（敵人移動、陷阱動作）
            self.level_manager.update(self.player)

            # 更新火球系統（火球會自動處理與敵人的碰撞和傷害）
            self.fireball_manager.update(
                all_platforms, current_level.enemies, SCREEN_WIDTH
            )

            # 更新冰球系統（冰球會自動處理與敵人的碰撞、傷害和暈眩）
            self.iceball_manager.update(
                all_platforms, current_level.enemies, SCREEN_WIDTH
            )

            # 更新裝備效果
            self.equipment_manager.update(self.player)

            # 更新裝備掉落物品
            self.equipment_drop_manager.update()

            # 檢查玩家撿拾裝備
            picked_items = self.equipment_drop_manager.check_pickup(
                self.player.x + self.player.width // 2,  # 玩家中心點
                self.player.y + self.player.height // 2,
                self.equipment_manager,
            )

            # 如果撿到裝備，顯示提示訊息
            if picked_items:
                for item_info in picked_items:
                    print(
                        f"獲得 {item_info['set_display_name']} ({item_info['rarity_display_name']})!"
                    )

            # 處理敵人死亡掉落
            self._handle_enemy_drops()

            # 檢查是否需要切換關卡或遊戲結束
            self._check_level_transition()
            self._check_game_over()

            # 更新相機位置（平滑跟隨玩家）
            self._update_camera()

    def _update_camera(self):
        """
        更新相機位置 - 平滑跟隨玩家\n
        \n
        使用線性插值(lerp)讓相機平滑地跟隨玩家移動，\n
        避免直接跟隨造成的上下抖動問題\n
        \n
        相機跟隨算法:\n
        - 計算目標相機位置（玩家 Y 座標 - 螢幕高度的一半）\n
        - 加入死區機制，小幅移動不觸發相機跟隨\n
        - 使用線性插值逐步移動相機到目標位置\n
        - 平滑係數決定跟隨的反應速度\n
        """
        if self.player:
            # 計算理想的相機位置（讓玩家保持在畫面中央）
            target_camera_y = self.player.y - SCREEN_HEIGHT // 2

            # 計算相機與目標位置的距離
            distance = target_camera_y - self.camera_y

            # 設定死區，小幅移動不觸發相機跟隨（減少微抖動）
            dead_zone = 5  # 像素，可根據需要調整

            # 只有當距離超過死區時才移動相機
            if abs(distance) > dead_zone:
                # 使用線性插值平滑移動相機到目標位置
                # camera_smoothing 越小相機越平滑但反應越慢
                # camera_smoothing 越大相機反應越快但可能抖動
                self.camera_y += distance * self.camera_smoothing

    def _handle_enemy_drops(self):
        """
        處理敵人死亡時的裝備掉落\n
        \n
        檢查當前關卡中死亡的敵人，在其死亡位置嘗試掉落裝備\n
        """
        current_level = self.level_manager.get_current_level()

        # 檢查所有敵人，找出剛死亡的
        for enemy in current_level.enemies[:]:  # 使用複本避免修改時出錯
            if enemy.health <= 0:
                # 敵人死亡，嘗試掉落裝備
                drop_x = enemy.x + enemy.width // 2
                drop_y = enemy.y + enemy.height // 2

                # 根據敵人類型決定掉落機率
                enemy_type = getattr(enemy, "boss_type", None)
                if enemy_type:
                    drop_source = "boss"
                elif hasattr(enemy, "is_elite") and enemy.is_elite:
                    drop_source = "elite_enemy"
                else:
                    drop_source = "basic_enemy"

                # 嘗試掉落裝備
                self.equipment_drop_manager.try_drop_item(drop_x, drop_y, drop_source)

                # 從關卡中移除死亡的敵人
                current_level.enemies.remove(enemy)

    def _check_level_transition(self):
        """
        檢查關卡切換條件\n
        \n
        檢查玩家是否到達關卡目標位置或完成特定任務，\n
        符合條件就切換到下一關\n
        """
        current_level = self.level_manager.get_current_level()

        # 如果玩家到達關卡頂部，就進入下一關
        if self.player.y < current_level.level_completion_height:
            # 檢查是否為最終關卡（第六關）
            if self.level_manager.current_level_number == 6:
                # 第六關：檢查是否所有 Boss 都被擊敗了
                if self._all_bosses_defeated():
                    self.game_state = "victory"
                    return
                else:
                    # 如果還有 Boss 存活，不允許完成關卡，將玩家推回
                    self.player.y = current_level.level_completion_height + 50
                    return

            # 非最終關卡的正常切換邏輯
            success = self.level_manager.advance_to_next_level()
            if success:
                # 重新定位玩家到新關卡的起始位置
                new_level = self.level_manager.get_current_level()
                self.player.x = new_level.player_start_x
                self.player.y = new_level.player_start_y

                # 立即更新相機位置到新位置，避免切換關卡時的跳躍
                self.camera_y = self.player.y - SCREEN_HEIGHT // 2

    def _all_bosses_defeated(self) -> bool:
        """
        檢查所有 Boss 是否都被擊敗\n
        \n
        回傳:\n
        bool: 是否所有 Boss 都已被擊敗\n
        """
        current_level = self.level_manager.get_current_level()

        # 檢查關卡中是否還有存活的 Boss
        from src.enemies.boss import Boss

        for enemy in current_level.enemies:
            if isinstance(enemy, Boss) and enemy.health > 0:
                return False
        return True

    def _check_game_over(self):
        """
        檢查遊戲結束條件\n
        \n
        檢查玩家是否死亡（血量歸零、掉出地圖等），\n
        遊戲結束就切換到結束畫面\n
        """
        if self.player.health <= 0:
            self.game_state = "game_over"
        elif self.player.y > SCREEN_HEIGHT + 100:  # 掉出畫面底部
            self.game_state = "game_over"

    def render(self):
        """
        繪製遊戲畫面\n
        \n
        根據當前遊戲狀態繪製對應的畫面：\n
        - 選單狀態：角色選擇介面\n
        - 遊戲狀態：完整遊戲畫面\n
        - 暫停狀態：遊戲畫面 + 暫停選單\n
        - 結束狀態：遊戲結束畫面\n
        \n
        繪製順序:\n
        1. 背景 → 2. 關卡元素 → 3. 遊戲物件 → 4. UI 介面\n
        """
        # 清空畫面，填上天空色
        self.screen.fill(BLUE)

        if self.game_state == "menu":
            # 繪製角色選擇選單
            self.ui.draw_character_selection(self.screen, self.selected_character_index)

        elif self.game_state == "playing" and self.player:
            # 繪製遊戲中的所有物件
            current_level = self.level_manager.get_current_level()

            # 先畫背景和關卡結構（使用平滑的相機位置）
            current_level.render(
                self.screen, self.camera_y + SCREEN_HEIGHT // 2
            )  # 傳入玩家高度做視角調整

            # 畫裝備掉落物品（使用平滑的相機位置）
            self.equipment_drop_manager.draw(self.screen, 0, self.camera_y)

            # 畫火球（使用平滑的相機位置）
            self.fireball_manager.render_all(
                self.screen, self.camera_y + SCREEN_HEIGHT // 2
            )

            # 畫冰球（使用平滑的相機位置）
            self.iceball_manager.render_all(
                self.screen, self.camera_y + SCREEN_HEIGHT // 2
            )

            # 畫玩家角色（使用平滑的相機位置）
            self.player.render(
                self.screen, self.camera_y + SCREEN_HEIGHT // 2
            )  # 傳入視角偏移

            # 畫 UI 資訊（血量、分數、關卡資訊）
            self.ui.draw_game_ui(
                self.screen, self.player, self.level_manager.current_level_number
            )

        elif self.game_state == "paused":
            # 暫停時先畫遊戲畫面（但不更新），再畫暫停選單
            if self.player:
                current_level = self.level_manager.get_current_level()
                current_level.render(self.screen, self.camera_y + SCREEN_HEIGHT // 2)
                self.player.render(self.screen, self.camera_y + SCREEN_HEIGHT // 2)
                self.ui.draw_game_ui(
                    self.screen, self.player, self.level_manager.current_level_number
                )

            # 在遊戲畫面上方畫暫停選單
            self.ui.draw_pause_menu(self.screen)

        elif self.game_state == "game_over":
            # 繪製遊戲結束畫面
            self.ui.draw_game_over(self.screen)

        elif self.game_state == "victory":
            # 繪製勝利畫面
            self.ui.draw_victory_screen(self.screen)

        # 更新顯示（把準備好的畫面顯示到螢幕）
        pygame.display.flip()

    def run(self):
        """
        主遊戲循環\n
        \n
        持續執行遊戲的核心循環：\n
        1. 處理使用者輸入\n
        2. 更新遊戲邏輯\n
        3. 繪製畫面\n
        4. 控制幀率\n
        \n
        這個方法會一直執行到遊戲結束\n
        """
        while self.running:
            # 1. 處理所有輸入事件
            self.handle_events()

            # 2. 更新遊戲狀態
            self.update()

            # 3. 繪製畫面
            self.render()

            # 4. 限制幀率，確保遊戲穩定運行
            self.clock.tick(FPS)

        # 遊戲結束後清理資源
        pygame.quit()
        sys.exit()


######################主程式進入點######################
def main():
    """
    主程式進入點\n
    \n
    建立遊戲實例並開始執行遊戲循環\n
    """
    game = MarioClimbingGame()
    game.run()


# 直接執行主程式
main()
