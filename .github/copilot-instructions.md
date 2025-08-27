# Mario Climbing Game - AI 開發指南

## 專案架構概覽

這是一個基於 pygame 的垂直攀爬遊戲，採用模組化設計。核心架構：

### 系統組件關係

```
MarioClimbingGame (main.py) - 主遊戲控制器
├── Player (src/characters/) - 角色控制與狀態，CHARACTER_CONFIGS 定義4種角色類型
├── LevelManager (src/levels/) - 5關卡進度管理，關卡配置在 _create_level_N() 方法
├── EquipmentManager (src/equipment/) - 4套裝系統，掉落與收集機制
├── EquipmentDropManager (src/equipment/) - 裝備掉落物理系統
├── GameUI (src/ui/) - 完整 UI 系統（選單、遊戲內、暫停畫面）
├── 陷阱系統 (src/traps/) - BaseTrap 抽象基類 + 具體陷阱實作
└── 敵人系統 (src/enemies/) - BaseEnemy 抽象基類 + Boss 戰機制
```

### 資料流向與狀態管理

1. **主迴圈**: `handle_events()` → `update()` → `render()` (60 FPS)
2. **遊戲狀態**: `menu` → `playing` → `paused`/`game_over` (字串狀態控制)
3. **角色選擇**: CHARACTER_CONFIGS 字典定義 4 種角色 (0-3 索引)
4. **裝備系統**:
   - `_handle_enemy_drops()` → `EquipmentDropManager.try_drop_item()`
   - → `check_pickup()` → `EquipmentManager.apply_effects()`
5. **攝影機系統**: `camera_y = player.y - SCREEN_HEIGHT // 2` 的簡單跟隨

## 核心開發模式

### 程式碼風格 (嚴格遵循)

- **命名規則**: 變數用 `snake_case`，類別用 `PascalCase`，常數用 `UPPER_CASE`
- **註解風格**: 區塊用 `######################`，行內用繁體中文白話說明
- **文檔字串**: 使用三引號，必須包含功能、參數、回傳值說明，用 `\n` 分行
- **不使用** `if __name__ == "__main__":` 慣例，直接呼叫 `main()`
- **繁體中文優先**: 所有註解、變數說明、UI 文字都用繁體中文

### 關鍵設計模式

- **抽象基類模式**: `BaseTrap`、`BaseEnemy` 定義共通介面，強制子類實作 `update()`, `render()`, 特殊方法
  - `BaseTrap._trigger_effect()` - 陷阱觸發特效
  - `BaseEnemy.update_ai()`, `attack_player()` - AI 行為和攻擊邏輯
- **字典配置驅動**:
  - `CHARACTER_CONFIGS` (4 種角色配置)
  - 套裝效果字典 `set_effects` (火焰、冰霜、影子、坦克)
  - 關卡數據在 `LevelManager._create_level_N()` 方法中
- **狀態集中管理**: 遊戲狀態由 `game_state` 字串控制，避免複雜狀態機
- **系統協調模式**: 各系統透過 `main.py` 的 `MarioClimbingGame` 統一管理，避免跨模組直接引用
- **優雅降級**: 錯誤處理偏好預設值替代而非拋出異常

## 開發工作流程

### 運行與測試

```bash
# 直接運行遊戲 (無需虛擬環境)
python main.py

# 依賴安裝
pip install pygame==2.5.2
```

### 新增功能步驟

1. **建立基類**: 先建立或擴充對應的基類 (`src/traps/base_trap.py`, `src/enemies/base_enemy.py`)
2. **實作具體類**: 在適當模組建立具體實作，必須實作所有抽象方法
3. **更新關卡配置**: 在 `LevelManager._create_level_N()` 方法中加入新物件
4. **系統整合**: 確保新物件在 `main.py` 的 `update()` 和 `render()` 循環中正確運行
5. **測試後清理**: 功能測試完畢要移除測試檔案

### 關鍵開發細節

- **抽象方法實作**: 繼承 `BaseTrap`/`BaseEnemy` 時必須實作所有 `@abstractmethod`
- **基類更新呼叫**: 子類的 `update()` 方法要呼叫 `self._update_base_properties()`
- **角色配置**: 新角色需更新 `CHARACTER_CONFIGS` 字典（索引 0-3）
- **套裝效果**: 套裝配置在 `EquipmentManager.set_effects` 字典中
- **關卡元素**: 所有陷阱/敵人透過 `LevelManager._create_level_N()` 方法配置

### 重要約定

- **座標系統**: 螢幕左上角為原點，Y 軸向下為正
- **攝影機跟隨**: 基於玩家 Y 位置的簡單偏移 (`player.y - SCREEN_HEIGHT // 2`)
- **碰撞檢測**: 基於矩形邊界，每個物件提供 `get_collision_rect()` 方法
- **幀率控制**: 固定 60 FPS，所有計時用幀數而非秒數
- **資源管理**: 目前僅用幾何形狀和顏色，不依賴圖片檔案
- **主程式執行**: 不使用 `if __name__ == "__main__":` 慣例，直接呼叫 `main()`

## 關鍵整合點

### 裝備系統整合

- `EquipmentDropManager.try_drop_item()` - 敵人死亡時觸發
- `EquipmentManager.apply_effects()` - 在玩家 `update()` 中生效
- 套裝件數決定效果強度 (1-4 件不同效果)
- 裝備收集: `_handle_enemy_drops()` → `check_pickup()` → 效果啟用

### 關卡切換機制

- 玩家到達 `level.level_completion_height` 觸發下一關
- `LevelManager.advance_to_next_level()` 重置玩家位置
- 關卡配置在 `level_manager.py` 的 `_create_level_N()` 方法
- 每關都有獨立的平台、陷阱、敵人配置

### UI 系統分工

- `GameUI.draw_character_selection()` - 選角畫面（4 種角色選擇）
- `GameUI.draw_game_ui()` - 遊戲中 HUD（血量條、關卡資訊）
- `GameUI.draw_pause_menu()` - 暫停選單
- `GameUI.draw_game_over()` - 遊戲結束畫面

### Boss 戰特殊機制

- Boss 類別擁有多種攻擊模式和階段變化
- 基於血量觸發不同行為 (`update_behavior_based_on_health()`)
- 召喚小兵、範圍攻擊、震波等特殊技能

## 程式碼示例模式

### 新陷阱實作範例

```python
class NewTrap(BaseTrap):
    def __init__(self, x, y):
        super().__init__(x, y, width=50, height=20, damage=15)
        self.special_property = 100  # 用簡單的話說明這個數值的用途

    def update(self):
        # 每幀都要做的事情，比如移動、計時
        self._update_base_properties()  # 必須呼叫基類更新方法
        pass

    def render(self, screen, camera_y):
        # 在螢幕上畫出陷阱的樣子
        pygame.draw.rect(screen, (255, 0, 0),
                        (self.x, self.y - camera_y, self.width, self.height))

    def _trigger_effect(self, player):
        # 陷阱被觸發時的特殊效果
        return {"effect_type": "damage", "knockback": (0, -5)}
```

### 錯誤處理模式

專案偏好優雅降級而非拋出異常，例如載入失敗時用預設值或幾何形狀替代。

## 開發注意事項

- **繁體中文優先**: 所有註解、變數說明都用繁體中文
- **模組獨立性**: 每個 `src/` 子目錄都是獨立功能模組
- **測試後清理**: 功能測試完畢要移除測試檔案
- **不建置文檔**: 除 README.md 外不需額外說明文件
- **系統 Python**: 直接使用系統 Python，不建立虛擬環境
