# Mario Climbing Game — AI 開發指引

這是一個基於 pygame 的垂直攀爬遊戲，採用模組化架構。本指引旨在讓 AI 開發代理能立即理解專案結構並高效產出。

## 🏗️ 核心架構

### 主要組件

- **MarioClimbingGame** (`main.py`): 遊戲主控制器，管理遊戲循環 (handle_events → update → render, 60 FPS)
- **Player** (`src/characters/player.py`): 角色系統，包含物理運算、輸入處理、套裝技能
- **LevelManager** (`src/levels/level_manager.py`): 關卡管理，動態生成 5 關挑戰
- **EquipmentManager** (`src/equipment/equipment_manager.py`): 4 套裝系統，從 1-4 件套效果遞增

### 數據流向

```
Input → Player.handle_input() → Physics Update → Collision Detection →
Equipment Effects → Enemy AI → Trap Updates → Rendering → UI Display
```

## 📋 開發規範

### 代碼風格

- **語言**: 所有註解、docstring 使用繁體中文
- **命名**: 變數/函式 `snake_case`，類別 `PascalCase`，常數 `UPPER_CASE`
- **Docstring**: 必須包含功能說明、參數、回傳值（用 `\n` 分行）
- **時間單位**: 所有計時器以幀數計算（60 幀 ≈ 1 秒）
- **主程式**: 檔案結尾直接呼叫 `main()`，不使用 `if __name__ == "__main__":`

### 核心接口規範

```python
# 所有遊戲物件必須實作
def get_collision_rect() -> pygame.Rect
def render(screen: pygame.Surface, camera_y: float)

# 陷阱子類別必須呼叫基類方法
def update(self):
    # ... 子類邏輯 ...
    self._update_base_properties()  # 必須呼叫

# 攝影機系統一致性
camera_y = player.y - SCREEN_HEIGHT // 2
screen_y = object.y - camera_y + SCREEN_HEIGHT // 2
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

### 裝備掉落流程

```
Enemy Death → EquipmentDropManager.try_drop_item() → EquipmentItem
→ Player Pickup → EquipmentManager.add_set_piece() → Effect Updates
```

## 🔧 除錯與測試

### 快速啟動

```powershell
pip install pygame==2.5.2
python main.py
```

### 除錯技巧

- **跳過關卡**: 修改 `LevelManager.current_level_number`
- **無敵模式**: 設定 `player.invulnerability_time = 999`
- **快速測試**: 暫時註解 `clock.tick(FPS)` 加速執行
- **碰撞可視化**: 在 render 方法中繪製 `get_collision_rect()`

### 角色能力速查

- **角色 0**: 平衡型 (血量 100, 速度 5, 跳躍 15, 攻擊 20)
- **角色 1**: 速度型 (血量 80, 速度 8, 跳躍 12, 攻擊 15)
- **角色 2**: 跳躍型 (血量 90, 速度 4, 跳躍 18, 攻擊 18, 二段跳)
- **角色 3**: 坦克型 (血量 150, 速度 3, 跳躍 10, 攻擊 25)

## ⚠️ 重要注意事項

### 碰撞系統

- 所有遊戲物件的碰撞檢測基於 `get_collision_rect()`
- 玩家蹲下時碰撞矩形高度縮小為一半
- 平台碰撞優先處理垂直方向，再處理水平方向

### 套裝系統整合

- 套裝效果在 `EquipmentManager.update()` 中持續作用
- 技能快捷鍵：數字鍵 1-4 對應火焰、冰霜、影子、坦克套裝
- 套裝顏色會影響角色渲染外觀

### 性能考量

- 渲染前檢查 `is_in_screen_bounds()` 避免畫面外物件浪費效能
- 敵人 AI 距離檢測使用平方距離避免開方運算
- 動畫幀數定期重置防止數值溢出

## 🎮 遊戲特色實作

### 組合技能系統

- 加速 + 跳躍 = 跳躍高度提升 30% (`jump_boost_multiplier = 1.3`)
- 跳躍緩衝機制：8 幀容錯時間提高操作手感

### Boss 戰機制

- Boss 位於第 5 關，具備多階段攻擊模式
- 範圍攻擊、召喚小兵、震波攻擊等特殊技能
- 血量變化觸發不同 AI 行為模式

當需要擴展功能時，優先查閱對應的基類和管理器，遵循既有模式可確保系統整合性。
