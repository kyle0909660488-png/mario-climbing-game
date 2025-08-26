######################載入套件######################
import pygame
import sys
from typing import Dict, List, Tuple
from src.characters.player import Player
from src.levels.level_manager import LevelManager
from src.ui.game_ui import GameUI
from src.equipment.equipment_manager import EquipmentManager
from src.equipment.equipment_item import EquipmentDropManager

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
    game_state (str): 當前遊戲狀態（'menu', 'playing', 'paused', 'game_over'）\n
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

        # 選角相關變數
        self.selected_character_index = 0  # 目前選中的角色編號

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
        - ESC: 暫停/返回選單\n
        - WASD: 玩家移動（遊戲中）\n
        - C: 攻擊（遊戲中）\n
        - 方向鍵: 角色選擇（選單中）\n
        - ENTER: 確認選擇（選單中）\n
        """
        for event in pygame.event.get():
            # 點擊關閉按鈕就結束遊戲
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                # ESC 鍵在不同狀態有不同功能
                if event.key == pygame.K_ESCAPE:
                    if self.game_state == "playing":
                        self.game_state = "paused"  # 遊戲中按 ESC 就暫停
                    elif self.game_state == "paused":
                        self.game_state = "menu"  # 暫停中按 ESC 回到選單

                # 選單狀態的按鍵處理
                elif self.game_state == "menu":
                    if event.key == pygame.K_LEFT:
                        # 選擇前一個角色（循環選擇）
                        self.selected_character_index = (
                            self.selected_character_index - 1
                        ) % 4
                    elif event.key == pygame.K_RIGHT:
                        # 選擇下一個角色（循環選擇）
                        self.selected_character_index = (
                            self.selected_character_index + 1
                        ) % 4
                    elif event.key == pygame.K_RETURN:
                        # 按 Enter 開始遊戲，建立選定的角色
                        self.start_game_with_character(self.selected_character_index)

                # 暫停狀態的按鍵處理
                elif self.game_state == "paused":
                    if event.key == pygame.K_SPACE:
                        self.game_state = "playing"  # 空白鍵繼續遊戲

    def start_game_with_character(self, character_type: int):
        """
        使用選定的角色開始遊戲\n
        \n
        根據角色類型建立對應的玩家物件，每種角色有不同的基礎能力：\n
        0: 平衡型角色（標準速度和跳躍）\n
        1: 速度型角色（移動快，跳躍普通）\n
        2: 跳躍型角色（二段跳能力）\n
        3: 坦克型角色（血量多，移動慢）\n
        \n
        參數:\n
        character_type (int): 角色類型編號，範圍 0-3\n
        """
        # 建立選定的角色
        start_x = SCREEN_WIDTH // 2
        start_y = SCREEN_HEIGHT - 100  # 從畫面底部開始
        self.player = Player(start_x, start_y, character_type)

        # 讓玩家能夠使用裝備系統
        self.player.set_equipment_manager(self.equipment_manager)

        # 重置關卡管理器到第一關
        self.level_manager.reset_to_first_level()

        # 清空裝備，重新開始
        self.equipment_manager.reset_equipment()
        self.equipment_drop_manager.clear_all()

        # 切換到遊戲狀態
        self.game_state = "playing"

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

            # 讓玩家根據按鍵狀態更新
            self.player.handle_input(keys)

            # 更新玩家物理狀態（移動、重力、碰撞）
            current_level = self.level_manager.get_current_level()
            self.player.update(current_level.platforms, current_level.traps)

            # 更新當前關卡（敵人移動、陷阱動作）
            self.level_manager.update(self.player)

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
            self.level_manager.advance_to_next_level()

            # 重新定位玩家到新關卡的起始位置
            new_level = self.level_manager.get_current_level()
            self.player.x = new_level.player_start_x
            self.player.y = new_level.player_start_y

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

            # 先畫背景和關卡結構
            current_level.render(self.screen, self.player.y)  # 傳入玩家高度做視角調整

            # 畫裝備掉落物品
            camera_y = self.player.y - SCREEN_HEIGHT // 2  # 簡單的攝影機跟隨
            self.equipment_drop_manager.draw(self.screen, 0, camera_y)

            # 畫玩家角色
            self.player.render(self.screen, self.player.y)  # 傳入視角偏移

            # 畫 UI 資訊（血量、分數、關卡資訊）
            self.ui.draw_game_ui(
                self.screen, self.player, self.level_manager.current_level_number
            )

        elif self.game_state == "paused":
            # 暫停時先畫遊戲畫面（但不更新），再畫暫停選單
            if self.player:
                current_level = self.level_manager.get_current_level()
                current_level.render(self.screen, self.player.y)
                self.player.render(self.screen, self.player.y)
                self.ui.draw_game_ui(
                    self.screen, self.player, self.level_manager.current_level_number
                )

            # 在遊戲畫面上方畫暫停選單
            self.ui.draw_pause_menu(self.screen)

        elif self.game_state == "game_over":
            # 繪製遊戲結束畫面
            self.ui.draw_game_over(self.screen)

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
