# Mario Climbing Game - AI 開發指南

## 專案架構概覽

這是一個基於 pygame 的垂直攀爬遊戲，採用模組化設計。核心架構：

# Mario Climbing Game — Copilot / AI 開發指引（精簡）

目標：讓 AI 開發代理能立刻在此 repo 產出、修改並測試遊戲功能。

核心概念

- 主程式：`main.py` 的 `MarioClimbingGame` 負責主迴圈（handle_events → update → render，60 FPS）。
- 模組：`src/` 下以子目錄分責（`characters`, `levels`, `traps`, `enemies`, `equipment`, `ui`）。

必讀檔案（快速索引）

- `main.py` — 遊戲流程、狀態管理、掉落處理
- `src/characters/player.py` — 輸入、物理、碰撞、攻擊
- `src/levels/level_manager.py` — 關卡建立與切換（\_create_level_N）
- `src/traps/base_trap.py` — 陷阱基類（子類需呼叫 `_update_base_properties()`）
- `src/enemies/base_enemy.py` — 敵人基類（實作 `update_ai`、`attack_player`）
- `src/equipment/equipment_manager.py` — 套裝效果與技能介面

重要慣例（請遵守）

- 語言：所有註解與 docstring 使用繁體中文。
- 命名：變數/函式 `snake_case`，類別 `PascalCase`，常數 `UPPER_CASE`。
- Docstring 要包含功能、參數、回傳（用換行 `\\n`）。
- 時間/冷卻均以「幀數」計算（60 幀 ≈ 1 秒）。
- 不使用 `if __name__ == "__main__":`；專案在檔尾直接呼叫 `main()`。

常見擴充模式（範例說明）

- 新陷阱：繼承 `BaseTrap`，實作 `update()`, `render(screen, camera_y)`, `_trigger_effect(player)`，並在 `update()` 呼叫 `self._update_base_properties()`；把實例加入 `Level(...).traps`。
- 新敵人：繼承 `BaseEnemy`，實作 `update_ai(player)`, `render(screen, camera_y)`, `attack_player(player)`；在關卡中加入實例。
- 裝備流程：敵人死亡 →`EquipmentDropManager.try_drop_item()`→`EquipmentItem`→`check_pickup()`→`EquipmentManager.add_set_piece()`→`EquipmentManager._update_equipped_effects()`。

運行與快速除錯

- 安裝依賴：`pip install pygame==2.5.2`
- 運行遊戲：`python main.py`（Windows PowerShell）
- 調試提示：若要快速執行多幀測試，可短暫註解 `clock.tick(FPS)`，或在 `main.update()` 呼叫前插入小段測試代碼。

整合點與風險

- 碰撞以 `get_collision_rect()` 為準，新增物件請實作該方法。
- 攝影機跟隨採 `camera_y = player.y - SCREEN_HEIGHT // 2`，render 呼叫需一致性傳入偏移。
- 資源目前為程式內繪製（無外部圖片），若加入檔案需同時提供降級行為。

需要我把此指引擴充為：完整模板（包含可貼上的類別範例、單元測試 scaffold），或維持精簡版本？請回饋想要的深度.
