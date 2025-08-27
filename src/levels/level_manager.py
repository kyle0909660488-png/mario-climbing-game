######################載入套件######################
import pygame
from typing import List, Tuple
from src.levels.level import Level
from src.levels.platform import Platform
from src.traps.spike import Spike
from src.traps.fire_wall import FireWall
from src.traps.moving_platform import MovingPlatform
from src.enemies.basic_enemy import BasicEnemy
from src.enemies.boss import Boss


######################關卡管理器類別######################
class LevelManager:
    """
    關卡管理系統\n
    \n
    負責管理遊戲中所有關卡的載入、切換和狀態維護：\n
    1. 關卡資料儲存和載入\n
    2. 關卡間的切換邏輯\n
    3. 關卡進度追蹤\n
    4. 動態生成關卡元素\n
    \n
    屬性:\n
    current_level_number (int): 當前關卡編號\n
    levels (List[Level]): 所有關卡物件的清單\n
    max_level (int): 最高關卡數\n
    \n
    關卡設計概念:\n
    - 每個關卡都是垂直向上的結構\n
    - 玩家需要從底部攀爬到頂部\n
    - 隨著關卡增加，難度逐漸提升\n
    """

    def __init__(self):
        """
        初始化關卡管理器\n
        \n
        建立所有關卡的基本資料和配置\n
        """
        self.current_level_number = 1
        self.levels = []
        self.max_level = 5  # 目前設計 5 個關卡

        # 建立所有關卡
        self._create_all_levels()

    def _create_all_levels(self):
        """
        建立所有關卡資料\n
        \n
        根據設計規格建立每個關卡的平台、陷阱、敵人配置\n
        """
        # 第一關：基礎教學關卡
        level_1 = self._create_level_1()
        self.levels.append(level_1)

        # 第二關：引入陷阱
        level_2 = self._create_level_2()
        self.levels.append(level_2)

        # 第三關：移動平台挑戰
        level_3 = self._create_level_3()
        self.levels.append(level_3)

        # 第四關：敵人關卡
        level_4 = self._create_level_4()
        self.levels.append(level_4)

        # 第五關：Boss 戰
        level_5 = self._create_level_5()
        self.levels.append(level_5)

    def _create_level_1(self) -> Level:
        """
        建立第一關：基礎教學關卡\n
        \n
        簡單的跳躍練習，讓玩家熟悉操作\n
        \n
        回傳:\n
        Level: 第一關關卡物件\n
        """
        platforms = [
            # 起始平台（地面）
            Platform(0, 750, 1200, 50),
            # 簡單的跳躍平台
            Platform(200, 650, 150, 20),
            Platform(450, 550, 150, 20),
            Platform(700, 450, 150, 20),
            Platform(200, 350, 150, 20),
            Platform(450, 250, 150, 20),
            Platform(700, 150, 150, 20),
            # 終點平台
            Platform(400, 50, 200, 30),
        ]

        # 第一關沒有陷阱，專注於跳躍練習
        traps = []

        # 第一關沒有敵人
        enemies = []

        return Level(
            level_number=1,
            platforms=platforms,
            traps=traps,
            enemies=enemies,
            player_start_x=100,
            player_start_y=700,
            level_completion_height=30,  # 到達高度 30 就算完成
            background_color=(135, 206, 235),  # 天空藍
        )

    def _create_level_2(self) -> Level:
        """
        建立第二關：陷阱入門\n
        \n
        引入尖刺陷阱和初級敵人，教玩家如何避開危險和戰鬥基礎\n
        \n
        回傳:\n
        Level: 第二關關卡物件\n
        """
        platforms = [
            # 起始區域
            Platform(0, 750, 1200, 50),
            Platform(100, 650, 200, 20),
            # 有尖刺的區域
            Platform(400, 550, 100, 20),
            Platform(600, 550, 100, 20),
            Platform(800, 450, 150, 20),
            # 中段休息平台
            Platform(200, 350, 200, 20),
            # 更多尖刺挑戰
            Platform(500, 250, 100, 20),
            Platform(700, 150, 150, 20),
            # 終點
            Platform(350, 50, 200, 30),
        ]

        traps = [
            # 地面尖刺
            Spike(300, 730, 50, 20),
            Spike(900, 730, 100, 20),
            # 平台間的尖刺
            Spike(520, 530, 60, 20),
            Spike(320, 330, 80, 20),
            Spike(600, 130, 70, 20),
        ]

        # 第二關引入基本敵人，讓玩家熟悉戰鬥機制
        enemies = [
            # 地面巡邏的溫和敵人，教學用途
            BasicEnemy(700, 730, patrol_range=120),
            # 平台上的敵人，需要跳上去才會遭遇
            BasicEnemy(150, 630, patrol_range=80),
        ]

        return Level(
            level_number=2,
            platforms=platforms,
            traps=traps,
            enemies=enemies,
            player_start_x=50,
            player_start_y=700,
            level_completion_height=30,
            background_color=(100, 149, 237),  # 深一點的藍色
        )

    def _create_level_3(self) -> Level:
        """
        建立第三關：移動平台挑戰\n
        \n
        引入移動平台和火焰陷阱，配合更多敵人增加動態挑戰\n
        \n
        回傳:\n
        Level: 第三關關卡物件\n
        """
        platforms = [
            # 起始區域
            Platform(0, 750, 1200, 50),
            Platform(50, 650, 150, 20),
            # 靜態平台和移動平台混合
            Platform(300, 550, 100, 20),
            Platform(700, 450, 120, 20),
            Platform(100, 350, 100, 20),
            Platform(900, 250, 150, 20),
            # 終點區域
            Platform(400, 50, 200, 30),
        ]

        traps = [
            # 火焰牆
            FireWall(400, 600, 30, 100),
            FireWall(500, 400, 30, 150),
            FireWall(300, 200, 30, 120),
            # 一些尖刺
            Spike(200, 530, 80, 20),
            Spike(800, 230, 90, 20),
        ]

        # 移動平台（也算是一種陷阱）
        moving_platforms = [
            MovingPlatform(500, 500, 100, 20, 500, 650, 2),  # 水平移動
            MovingPlatform(250, 300, 80, 20, 250, 300, 1, True),  # 垂直移動
            MovingPlatform(600, 200, 100, 20, 600, 800, 1.5),  # 水平移動
        ]

        # 把移動平台加入陷阱清單（它們有特殊行為）
        traps.extend(moving_platforms)

        # 第三關增加敵人配置，搭配移動平台增加挑戰難度
        enemies = [
            # 地面守衛，阻擋玩家前進
            BasicEnemy(450, 730, patrol_range=150),
            BasicEnemy(950, 730, patrol_range=100),
            # 平台上的敵人，需要配合移動平台作戰
            BasicEnemy(350, 530, patrol_range=60),
            # 高處狙擊手，給玩家攀爬時的壓力
            BasicEnemy(950, 230, patrol_range=90),
        ]

        return Level(
            level_number=3,
            platforms=platforms,
            traps=traps,
            enemies=enemies,
            player_start_x=100,
            player_start_y=700,
            level_completion_height=30,
            background_color=(70, 130, 180),  # 鋼青色
        )

    def _create_level_4(self) -> Level:
        """
        建立第四關：敵人關卡\n
        \n
        大量敵人出現，玩家需要熟練使用攻擊功能和閃避技巧\n
        \n
        回傳:\n
        Level: 第四關關卡物件\n
        """
        platforms = [
            # 起始區域
            Platform(0, 750, 1200, 50),
            Platform(100, 650, 200, 20),
            # 敵人活動區域
            Platform(400, 550, 300, 20),
            Platform(150, 450, 200, 20),
            Platform(600, 350, 250, 20),
            Platform(200, 250, 150, 20),
            Platform(700, 150, 200, 20),
            # 終點
            Platform(400, 50, 200, 30),
        ]

        traps = [
            # 混合各種陷阱增加難度
            Spike(50, 730, 40, 20),
            Spike(1100, 730, 80, 20),
            FireWall(500, 450, 30, 100),
            Spike(400, 230, 60, 20),
            # 新增更多陷阱挑戰
            Spike(300, 630, 50, 20),
            FireWall(150, 350, 30, 100),
        ]

        enemies = [
            # 地面多層防守線
            BasicEnemy(800, 730, patrol_range=200),
            BasicEnemy(300, 730, patrol_range=150),
            BasicEnemy(600, 730, patrol_range=100),  # 新增地面敵人
            # 平台守衛軍團
            BasicEnemy(500, 530, patrol_range=120),  # 增加巡邏範圍
            BasicEnemy(250, 430, patrol_range=80),
            BasicEnemy(150, 430, patrol_range=60),  # 新增平台敵人
            BasicEnemy(700, 330, patrol_range=120),
            BasicEnemy(800, 330, patrol_range=100),  # 新增平台敵人
            # 高處狙擊部隊
            BasicEnemy(750, 130, patrol_range=100),
            BasicEnemy(250, 230, patrol_range=80),  # 新增狙擊手
            BasicEnemy(800, 130, patrol_range=90),  # 新增狙擊手
        ]

        return Level(
            level_number=4,
            platforms=platforms,
            traps=traps,
            enemies=enemies,
            player_start_x=50,
            player_start_y=700,
            level_completion_height=30,
            background_color=(25, 25, 112),  # 深夜藍
        )

    def _create_level_5(self) -> Level:
        """
        建立第五關：Boss 戰\n
        \n
        最終 Boss 關卡，集合所有挑戰元素，多階段戰鬥體驗\n
        \n
        回傳:\n
        Level: 第五關關卡物件\n
        """
        platforms = [
            # Boss 戰鬥場地
            Platform(0, 750, 1200, 50),
            Platform(100, 650, 150, 20),
            Platform(550, 650, 150, 20),
            Platform(950, 650, 150, 20),
            # Boss 平台周圍的戰術平台
            Platform(200, 450, 100, 20),
            Platform(500, 350, 200, 30),  # Boss 主要活動平台
            Platform(800, 450, 100, 20),
            # 逃生和戰術移動路線
            Platform(50, 250, 100, 20),
            Platform(350, 200, 150, 20),  # 新增中間平台
            Platform(1050, 250, 100, 20),
            # 勝利平台
            Platform(450, 50, 300, 40),
        ]

        traps = [
            # Boss 戰區域的環境危險
            Spike(300, 730, 60, 20),
            Spike(850, 730, 60, 20),
            FireWall(100, 550, 30, 100),
            FireWall(1070, 550, 30, 100),
            # 動態危險增加戰鬥複雜度
            MovingPlatform(350, 550, 80, 20, 350, 750, 2),
            # 新增更多陷阱挑戰
            Spike(150, 630, 40, 20),
            Spike(1000, 630, 40, 20),
            FireWall(750, 300, 30, 150),  # Boss 區域附近的火焰
        ]

        enemies = [
            # Boss 前哨部隊 - 第一波挑戰
            BasicEnemy(150, 730, patrol_range=100),
            BasicEnemy(1000, 730, patrol_range=100),
            BasicEnemy(600, 730, patrol_range=80),  # 新增地面守衛
            # 中層防禦線 - 阻礙玩家接近 Boss
            BasicEnemy(250, 430, patrol_range=50),
            BasicEnemy(850, 430, patrol_range=50),
            BasicEnemy(150, 630, patrol_range=60),  # 新增側翼守衛
            BasicEnemy(1000, 630, patrol_range=60),  # 新增側翼守衛
            # Boss 精英護衛 - Boss 周圍的強化敵人
            BasicEnemy(400, 330, patrol_range=40),  # Boss 平台左側護衛
            BasicEnemy(700, 330, patrol_range=40),  # Boss 平台右側護衛
            # 主要 Boss 敵人 - 最終挑戰
            Boss(550, 320, boss_type="fire_lord"),  # 調整 Boss 位置到平台上
        ]

        return Level(
            level_number=5,
            platforms=platforms,
            traps=traps,
            enemies=enemies,
            player_start_x=600,
            player_start_y=700,
            level_completion_height=30,
            background_color=(139, 0, 139),  # 紫色（Boss 戰氣氛）
        )

    def get_current_level(self) -> Level:
        """
        取得當前關卡物件\n
        \n
        回傳:\n
        Level: 當前關卡的完整資料\n
        """
        return self.levels[self.current_level_number - 1]

    def advance_to_next_level(self) -> bool:
        """
        前進到下一關\n
        \n
        檢查是否還有下一關，有的話就切換過去\n
        \n
        回傳:\n
        bool: 是否成功前進到下一關\n
        """
        if self.current_level_number < self.max_level:
            self.current_level_number += 1
            return True
        return False  # 已經是最後一關了

    def reset_to_first_level(self):
        """
        重置到第一關\n
        \n
        遊戲重新開始時使用\n
        """
        self.current_level_number = 1

        # 重置所有關卡的狀態
        for level in self.levels:
            level.reset()

    def is_final_level(self) -> bool:
        """
        檢查是否為最後一關\n
        \n
        回傳:\n
        bool: 是否為最終關卡\n
        """
        return self.current_level_number >= self.max_level

    def update(self, player):
        """
        更新關卡狀態\n
        \n
        更新當前關卡中所有動態元素（敵人、陷阱、移動平台等）\n
        \n
        參數:\n
        player: 玩家物件（用於敵人 AI 和某些陷阱的觸發判斷）\n
        """
        current_level = self.get_current_level()
        current_level.update(player)

    def get_level_info(self) -> dict:
        """
        取得當前關卡資訊\n
        \n
        回傳關卡基本資訊，用於 UI 顯示\n
        \n
        回傳:\n
        dict: 包含關卡編號、名稱、進度等資訊\n
        """
        current_level = self.get_current_level()
        return {
            "number": self.current_level_number,
            "max_level": self.max_level,
            "name": f"第 {self.current_level_number} 關",
            "progress": f"{self.current_level_number}/{self.max_level}",
            "is_final": self.is_final_level(),
        }
