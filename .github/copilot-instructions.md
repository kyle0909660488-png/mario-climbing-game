````instructions
# Mario Climbing Game — AI 開發指引

這是一個基於 pygame 的垂直攀爬遊戲，採用模組化架構。本指引旨在讓 AI 開發代理能立即理解專案結構並高效產出。

## 🏗️ 核心架構

### 主要組件

- **MarioClimbingGame** (`main.py`): 遊戲主控制器，管理遊戲循環 (handle_events → update → render, 60 FPS)
- **Player** (`src/characters/player.py`): 角色系統，包含物理運算、輸入處理、套裝技能
- **LevelManager** (`src/levels/level_manager.py`): 關卡管理，動態生成 6 關挑戰（含 Boss 戰）
- **EquipmentManager** (`src/equipment/equipment_manager.py`): 4 套裝系統，從 1-4 件套效果遞增
- **PotionDropManager** (`src/equipment/potion.py`): 處理藥水掉落和收集邏輯
- **GamePerformanceMonitor** (`main.py`): 內建效能監控系統，追蹤 FPS 和記憶體使用

### 數據流向

```
Input → Player.handle_input() → Physics Update → Collision Detection →
Equipment Effects → Enemy AI → Trap Updates → Rendering → UI Display
Enemy Death → PotionDropManager.try_drop_item() → Player Pickup → Equipment Effects
```

### 關鍵管理器交互模式

```
Main Game Loop (main.py):
├── handle_events()                           # 輸入處理（含除錯快捷鍵）
├── update() 階段：
│   ├── Player.handle_input() + Player.update()  # 玩家物理和狀態
│   ├── LevelManager.update()                     # 關卡陷阱和敵人
│   ├── EquipmentManager.update()                 # 套裝效果持續作用
│   ├── FireballManager/IceballManager.update()  # 彈道物件管理
│   └── PotionDropManager.update()               # 藥水掉落物管理
└── render()                                  # 畫面渲染 + UI 顯示

Manager Dependencies (dependency injection pattern):
- Player 初始化時需要注入：equipment_manager, fireball_manager, iceball_manager, sound_manager
- 所有管理器透過 player 物件共享狀態
- 管理器使用統一的 .clear_all() 介面進行重置
```

### 基類架構 & 抽象介面

- **BaseEnemy** (`src/enemies/base_enemy.py`): 敵人基類，子類必須實作 `update_ai()`, `render()`, `attack_player()` + 呼叫 `_update_base_properties()`
- **BaseTrap** (`src/traps/base_trap.py`): 陷阱基類，子類必須實作 `update()`, `render()`, `_trigger_effect()` + 呼叫 `_update_base_properties()`

## 📋 開發規範

### 代碼風格

- **語言**: 所有註解、docstring 使用繁體中文，函式說明用 `\n` 分行
- **命名**: 變數/函式 `snake_case`，類別 `PascalCase`，常數 `UPPER_CASE`
- **Docstring**: 必須包含功能說明、參數、回傳值（用 `\n` 分行）
- **時間單位**: 所有計時器以幀數計算（60 幀 ≈ 1 秒）
- **主程式**: 檔案結尾直接呼叫 `main()`，不使用 `if __name__ == "__main__":`

### 模組組織原則

- **基類優先**: 新功能先檢查是否有對應基類（`BaseEnemy`, `BaseTrap`）
- **管理器模式**: 複雜系統使用專用管理器（`EquipmentManager`, `FireballManager`）
- **統一介面**: 所有遊戲物件實作 `get_collision_rect()` 和 `render(screen, camera_y)`
- **狀態分離**: UI、物理、邏輯分別處理，避免耦合

### 核心接口規範

```python
# 所有遊戲物件必須實作
def get_collision_rect() -> pygame.Rect
def render(screen: pygame.Surface, camera_y: float)

# 陷阱子類別必須呼叫基類方法
def update(self):
    # ... 子類邏輯 ...
    self._update_base_properties()  # 必須呼叫

# 敵人子類別必須呼叫基類方法
def update(self, player):
    # ... 子類邏輯 ...
    self._update_base_properties()  # 必須呼叫

# 攝影機系統一致性 - 所有渲染方法必須遵循
camera_y = player.y - SCREEN_HEIGHT // 2
screen_y = object.y - camera_y + SCREEN_HEIGHT // 2

# 畫面剔除優化 - 避免畫面外物件浪費效能
def is_in_screen_bounds(self, screen, camera_y):
    screen_y = self.y - camera_y + screen.get_height() // 2
    return -50 <= screen_y <= screen.get_height() + 50

# Manager 依賴注入模式 - Player 需要管理器引用
player.set_equipment_manager(equipment_manager)
player.set_fireball_manager(fireball_manager)
player.set_iceball_manager(iceball_manager)
player.set_sound_manager(sound_manager)
```

## 🎯 常見開發模式

### 新增陷阱

1. 繼承 `BaseTrap`，實作 `update()`, `render()`, `_trigger_effect()`
2. 在 `update()` 中呼叫 `self._update_base_properties()`
3. 在 `LevelManager._create_level_N()` 中加入實例

### 新增敵人

1. 繼承 `BaseEnemy`，實作 `update_ai()`, `render()`, `attack_player()`
2. 在關卡的 `enemies` 清單中加入實例
3. 死亡掉落在 `main._handle_enemy_drops()` 自動處理

### 彈道系統管理

所有發射物件統一由專門管理器處理：

- `FireballManager`: 管理火焰套裝技能發射的火球
- `IceballManager`: 管理冰霜套裝技能發射的冰球
- 在 `main.update()` 中統一更新所有管理器
- 彈道碰撞檢測和傷害計算在管理器內部處理

### 新增投射物

1. 繼承基礎投射物類別，實作 `update()`, `render()`, `check_collision()`
2. 在對應管理器中加入實例生成和更新邏輯
3. 套裝技能透過管理器的 `add_projectile()` 方法發射

### 藥水掉落流程

```
Enemy Death → PotionDropManager.try_drop_item() → PotionItem
→ Player Pickup → PotionDropManager.check_pickup() → Player.use_potion()
```

## 🔧 除錯與測試

### 快速啟動

```powershell
pip install pygame==2.5.2
python main.py
```

### 除錯快捷鍵（開發必備）

**關卡控制**:
- `F1-F6`: 直接跳轉到指定關卡
- `Q`: 重置當前關卡
- `ESC`: 返回主選單

**系統測試**:
- `F12`: 開啟/關閉效能監控器（FPS/記憶體顯示）
- `F10`: 強制掉落測試藥水（治療/護盾/攻擊各一）

**遊戲操作**:
- `WASD/方向鍵`: 移動
- `空白鍵/W`: 跳躍（推薦用空白鍵避免衝突）
- `S`: 蹲下
- `R`: 加速衝刺
- `C`: 攻擊
- `1-4`: 套裝技能（需對應套裝）
- `1-3`: 使用藥水（攻擊/護盾/治療）

### 除錯技巧

- **跳過關卡**: 修改 `LevelManager.current_level_number` 或用 F1-F6
- **無敵模式**: 設定 `player.invulnerability_time = 999`
- **快速測試**: 暫時註解 `performance_monitor.tick(FPS)` 加速執行
- **碰撞可視化**: 在 render 方法中繪製 `get_collision_rect()`
- **相機除錯**: 調整 `camera_smoothing` 值（0.05-0.2）控制跟隨平滑度

### 角色能力速查（CHARACTER_CONFIGS）

- **角色 0**: 平衡瑪莉歐 (血量 130, 速度 6, 跳躍 16, 攻擊 25)
- **角色 1**: 跳跳瑪莉歐 (血量 100, 速度 4, 跳躍 17, 攻擊 20, **二段跳能力**)
- **角色 2**: 坦克瑪莉歐 (血量 150, 速度 5, 跳躍 15, 攻擊 28)

注意：目前只有 3 種角色可選（0-2）

## ⚠️ 重要注意事項

### 碰撞系統

- 所有遊戲物件的碰撞檢測基於 `get_collision_rect()`
- 玩家蹲下時碰撞矩形高度縮小為一半
- 平台碰撞優先處理垂直方向，再處理水平方向

### 套裝系統整合

- 套裝效果在 `EquipmentManager.update()` 中持續作用
- 技能快捷鍵：數字鍵 1-4 對應火焰、冰霜、影子、坦克套裝
- 套裝顏色會影響角色渲染外觀
- 套裝效果從 1 件套開始生效，最高 4 件套

### 性能考量

- **渲染優化**: 先檢查 `is_in_screen_bounds()` 避免畫面外物件浪費效能
- **AI 優化**: 敵人 AI 距離檢測使用平方距離避免開方運算
- **動畫優化**: 動畫幀數定期重置防止數值溢出
- **效能監控**: F12 開啟內建監控器，會在效能問題時顯示警告

## 🎮 遊戲特色實作

### Boss 戰機制（第 6 關）

- **地面決戰**: Boss 位於地面左側與玩家正面對決
- **雜兵護衛**: Boss 配備多層次護衛部隊，必須全部擊敗才能勝利
- **多階段攻擊**: 範圍攻擊、召喚小兵、震波攻擊等特殊技能
- **血量觸發**: 血量變化觸發不同 AI 行為模式
- **保證獎勵**: 100% 掉落率保證獎勵

### 跳躍緩衝系統

- **緩衝機制**: 按下跳躍鍵時提供 8 幀緩衝時間 (`jump_buffer_time = 8`)
- **操作優化**: 配合 `previous_jump_key_pressed` 實現單次觸發
- **組合技能**: 加速 + 跳躍 = 跳躍高度提升 30% (`jump_boost_multiplier = 1.3`)

### 相機系統設計

- **平滑跟隨**: 使用線性插值避免相機抖動 (`camera_smoothing = 0.08`)
- **死區機制**: 5 像素死區減少微抖動
- **攝影機同步**: 所有 render 方法統一使用 `camera_y + SCREEN_HEIGHT // 2` 計算螢幕座標
- **立即更新**: 關卡切換和重置時立即設定相機位置，避免跳躍

### 效能監控系統

- **內建監控**: `GamePerformanceMonitor` 類別監控 FPS 和記憶體使用
- **即時顯示**: 按 `F12` 切換顯示，即時查看效能資訊和警告
- **問題檢測**: 自動檢測效能問題（FPS < 45, 記憶體 > 200MB）
- **歷史記錄**: 3 秒歷史記錄用於計算平均效能指標

### 難度系統

- **簡單模式**: 到達關卡頂部即可過關，無需擊敗所有敵人
- **困難模式**: 必須擊敗所有敵人才能過關，完整戰鬥體驗

### 藥水系統

- **三種藥水**: 治療（綠）、護盾（藍）、攻擊（紅）
- **快捷使用**: 數字鍵 1-3 使用對應藥水
- **測試功能**: 按 F10 強制掉落三種藥水進行測試
- **效果疊加**: 藥水效果與玩家狀態緊密整合，支援疊加和時限

## 💡 AI 開發最佳實務

### 快速理解程式碼

1. 先看 `main.py` 了解整體流程
2. 查看 `CHARACTER_CONFIGS` 了解角色設定
3. 檢查基類 `BaseEnemy`, `BaseTrap` 了解擴展模式
4. 使用除錯快捷鍵快速測試功能

### 新增功能流程

1. **確認基類**: 檢查是否有對應的基類可繼承
2. **實作抽象方法**: 確保實作所有必要的抽象方法
3. **呼叫基類方法**: 在 update() 中呼叫 `_update_base_properties()`
4. **註冊到系統**: 將新物件加入相應的管理器或關卡中
5. **測試驗證**: 使用快捷鍵快速跳轉測試

### 除錯策略

1. **效能問題**: 使用 F12 檢查效能監控器
2. **碰撞問題**: 在 render 中繪製碰撞框進行視覺化除錯
3. **邏輯問題**: 使用 F1-F6 快速跳轉到特定關卡測試
4. **狀態問題**: 檢查管理器的依賴注入是否正確

當需要擴展功能時，優先查閱對應的基類和管理器，遵循既有模式可確保系統整合性。

````
