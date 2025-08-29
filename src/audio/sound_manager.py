import pygame
import os
from typing import Optional, Dict

######################音效管理器######################

class SoundManager:
    """
    遊戲音效管理器 - 統一管理所有音效的播放和優先順序\n
    \n
    功能:\n
    1. 音效檔案載入和管理\n
    2. 優先順序控制（殘血 > 特效 > 狀態變化 > 背景音樂）\n
    3. 背景音樂循環播放\n
    4. 音效重複播放防護\n
    \n
    優先順序定義:\n
    - 1: 殘血警告（最高優先）\n
    - 2: 技能特效（發射火/冰）\n
    - 3: 狀態變化（死亡、Boss死亡、勝利）\n
    - 4: 背景音樂（最低優先）\n
    """

    def __init__(self, assets_path: str = "assets/sounds"):
        """
        初始化音效管理器\n
        \n
        參數:\n
        assets_path (str): 音效檔案資料夾路徑\n
        """
        self.assets_path = assets_path
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.current_bgm = None  # 目前播放的背景音樂
        self.current_bgm_channel = None  # 背景音樂頻道
        self.last_played_sound = None  # 防止重複播放同一個音效
        self.last_played_time = 0
        
        # 優先順序定義（數字越小優先順序越高）
        self.sound_priorities = {
            "殘血": 1,
            "發射火": 2,
            "發射冰": 2,
            "玩家死掉": 3,
            "boss死掉": 3,
            "勝利": 3,
            "選角色": 3,
            "第一關": 4,
            "第二關": 4,
            "第三關": 4,
            "第四關": 4,
            "第五關": 4,
            "第六關": 4,
        }
        
        self.current_priority = 999  # 目前播放音效的優先順序
        self.is_low_health_playing = False  # 殘血音效是否正在播放
        
        # 初始化pygame音效系統
        try:
            pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=512)
            pygame.mixer.init()
            self._load_all_sounds()
        except pygame.error as e:
            print(f"音效系統初始化失敗: {e}")

    def _load_all_sounds(self):
        """
        載入所有音效檔案到記憶體中\n
        \n
        遍歷音效資料夾，載入所有 .mp3 檔案\n
        建立檔案名稱到 Sound 物件的對應表\n
        """
        if not os.path.exists(self.assets_path):
            print(f"音效資料夾不存在: {self.assets_path}")
            return
        
        for filename in os.listdir(self.assets_path):
            if filename.endswith('.mp3'):
                sound_name = filename.replace('.mp3', '')  # 移除副檔名作為音效名稱
                try:
                    sound_path = os.path.join(self.assets_path, filename)
                    sound = pygame.mixer.Sound(sound_path)
                    self.sounds[sound_name] = sound
                    print(f"成功載入音效: {sound_name}")
                except pygame.error as e:
                    print(f"載入音效失敗 {filename}: {e}")

    def play_sound(self, sound_name: str, force: bool = False, loop: bool = False):
        """
        播放指定音效\n
        \n
        參數:\n
        sound_name (str): 音效名稱（不含副檔名）\n
        force (bool): 是否強制播放，忽略優先順序\n
        loop (bool): 是否循環播放（用於背景音樂）\n
        \n
        回傳:\n
        bool: 是否成功播放音效\n
        """
        if sound_name not in self.sounds:
            print(f"找不到音效: {sound_name}")
            return False
        
        current_time = pygame.time.get_ticks()
        sound_priority = self.sound_priorities.get(sound_name, 999)
        
        # 防止短時間內重複播放相同音效
        if (self.last_played_sound == sound_name and 
            current_time - self.last_played_time < 500):  # 0.5秒內不重複
            return False
        
        # 檢查優先順序（除非強制播放）
        if not force and sound_priority > self.current_priority:
            return False
        
        try:
            sound = self.sounds[sound_name]
            
            # 如果是背景音樂
            if sound_name.startswith("第") and sound_name.endswith("關"):
                self._play_background_music(sound_name, sound)
            else:
                # 一般音效播放
                if sound_priority <= 3:  # 高優先音效，停止其他音效
                    pygame.mixer.stop()
                
                sound.play()
                self.current_priority = sound_priority
                self.last_played_sound = sound_name
                self.last_played_time = current_time
                
                # 殘血音效特殊處理
                if sound_name == "殘血":
                    self.is_low_health_playing = True
            
            return True
            
        except pygame.error as e:
            print(f"播放音效失敗 {sound_name}: {e}")
            return False

    def _play_background_music(self, sound_name: str, sound: pygame.mixer.Sound):
        """
        播放背景音樂（循環播放）\n
        \n
        參數:\n
        sound_name (str): 音效名稱\n
        sound (pygame.mixer.Sound): 音效物件\n
        """
        # 停止目前的背景音樂
        if self.current_bgm_channel:
            self.current_bgm_channel.stop()
        
        # 播放新的背景音樂（無限循環）
        self.current_bgm_channel = sound.play(loops=-1)
        self.current_bgm = sound_name
        print(f"開始播放背景音樂: {sound_name}")

    def play_level_music(self, level_number: int):
        """
        播放關卡背景音樂\n
        \n
        參數:\n
        level_number (int): 關卡編號（1-6）\n
        """
        level_names = ["第一關", "第二關", "第三關", "第四關", "第五關", "第六關"]
        
        if 1 <= level_number <= 6:
            sound_name = level_names[level_number - 1]
            self.play_sound(sound_name, force=True, loop=True)

    def play_low_health_warning(self, health: int, max_health: int):
        """
        播放低血量警告音效\n
        \n
        參數:\n
        health (int): 當前血量\n
        max_health (int): 最大血量\n
        """
        # 血量低於20時播放殘血音效
        if health <= 20 and not self.is_low_health_playing:
            if self.play_sound("殘血", force=True):
                print(f"血量過低！({health}/{max_health})")
        elif health > 20:
            self.is_low_health_playing = False

    def stop_all_sounds(self):
        """停止所有音效播放"""
        pygame.mixer.stop()
        self.current_priority = 999
        self.is_low_health_playing = False
        self.current_bgm = None
        self.current_bgm_channel = None

    def stop_background_music(self):
        """停止背景音樂"""
        if self.current_bgm_channel:
            self.current_bgm_channel.stop()
            self.current_bgm = None
            self.current_bgm_channel = None

    def update(self):
        """
        更新音效系統狀態\n
        \n
        定期檢查音效播放狀態，重置優先順序\n
        """
        # 檢查是否有音效正在播放
        if not pygame.mixer.get_busy():
            # 沒有音效播放時，重置優先順序
            if self.current_priority < 4:  # 不是背景音樂
                self.current_priority = 999
        
        # 檢查殘血音效是否播放完畢
        if self.is_low_health_playing and not pygame.mixer.get_busy():
            self.is_low_health_playing = False

    def get_current_bgm(self) -> Optional[str]:
        """
        取得目前播放的背景音樂名稱\n
        \n
        回傳:\n
        str or None: 背景音樂名稱，沒有則回傳 None\n
        """
        return self.current_bgm

    def is_sound_loaded(self, sound_name: str) -> bool:
        """
        檢查音效是否已載入\n
        \n
        參數:\n
        sound_name (str): 音效名稱\n
        \n
        回傳:\n
        bool: 音效是否已載入\n
        """
        return sound_name in self.sounds