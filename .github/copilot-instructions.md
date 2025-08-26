# Mario Climbing Game - AI 開發指南

## 專案架構概覽

這是一個基於 pygame 的垂直攀爬遊戲，採用模組化設計。核心架構：

### 系統組件關係

```
MarioClimbingGame (main.py)
├── Player (src/characters/) - 角色控制與狀態
├── LevelManager (src/levels/) - 關卡管理與切換
├── EquipmentManager (src/equipment/) - 裝備系統
├── GameUI (src/ui/) - 使用者介面
└── 各種遊戲物件 (traps/, enemies/)
```

### 資料流向

1. **主迴圈**: `handle_events()` → `update()` → `render()`
2. **遊戲狀態**: `menu` → `playing` → `paused`/`game_over`
3. **角色選擇**: 4 種角色類型 (平衡/速度/跳躍/坦克)
4. **裝備系統**: 敵人掉落 → 收集 → 套裝效果

## 核心開發模式

### 程式碼風格 (嚴格遵循)

- **命名規則**: 變數用 `snake_case`，類別用 `PascalCase`
- **註解風格**: 區塊用 `######################`，行內用繁體中文白話說明
- **文檔字串**: 使用三引號，必須包含功能、參數、回傳值說明，用 `\n` 分行
- **不使用** `if __name__ == "__main__":` 慣例，直接呼叫 `main()`

### 關鍵設計模式

- **抽象基類**: `BaseTrap`, `BaseEnemy` 定義共通介面
- **狀態管理**: 遊戲狀態由 `game_state` 字串控制
- **系統協調**: 各系統透過 `main.py` 的 `MarioClimbingGame` 統一管理
- **配置驅動**: 角色能力、套裝效果都用字典配置

## 開發工作流程

### 運行與測試

```bash
# 直接運行遊戲 (無需虛擬環境)
python main.py

# 依賴安裝
pip install pygame==2.5.2
```

### 新增功能步驟

1. 先建立或擴充對應的基類 (`src/traps/base_trap.py`, `src/enemies/base_enemy.py`)
2. 在適當模組建立具體實作
3. 更新 `LevelManager` 的關卡配置
4. 確保 `render()` 和 `update()` 方法完整

### 重要約定

- **座標系統**: 螢幕左上角為原點，Y 軸向下
- **攝影機跟隨**: 基於玩家 Y 位置的簡單偏移 (`player.y - SCREEN_HEIGHT // 2`)
- **碰撞檢測**: 基於矩形邊界，在各物件的 `update()` 中處理
- **資源管理**: 目前僅用幾何形狀，不使用圖片素材

## 關鍵整合點

### 裝備系統整合

- `EquipmentDropManager.try_drop_item()` - 敵人死亡時觸發
- `EquipmentManager.apply_effects()` - 在玩家 `update()` 中生效
- 套裝件數決定效果強度 (1-4 件不同效果)

### 關卡切換機制

- 玩家到達 `level.level_completion_height` 觸發下一關
- `LevelManager.advance_to_next_level()` 重置玩家位置
- 關卡配置在 `level_manager.py` 的 `_create_level_N()` 方法

### UI 系統分工

- `GameUI.draw_character_selection()` - 選角畫面
- `GameUI.draw_game_ui()` - 遊戲中 HUD
- `GameUI.draw_pause_menu()` - 暫停選單

## 程式碼示例模式

### 新陷阱實作範例

```python
class NewTrap(BaseTrap):
    def __init__(self, x, y):
        super().__init__(x, y, width=50, height=20, damage=15)
        self.special_property = 100  # 用簡單的話說明這個數值的用途

    def update(self):
        # 每幀都要做的事情，比如移動、計時
        pass

    def render(self, screen, camera_y):
        # 在螢幕上畫出陷阱的樣子
        pygame.draw.rect(screen, (255, 0, 0),
                        (self.x, self.y - camera_y, self.width, self.height))
```

### 錯誤處理模式

專案偏好優雅降級而非拋出異常，例如載入失敗時用預設值或幾何形狀替代。

## 開發注意事項

- **繁體中文優先**: 所有註解、變數說明都用繁體中文
- **模組獨立性**: 每個 `src/` 子目錄都是獨立功能模組
- **測試後清理**: 功能測試完畢要移除測試檔案
- **不建置文檔**: 除 README.md 外不需額外說明文件
- **系統 Python**: 直接使用系統 Python，不建立虛擬環境
