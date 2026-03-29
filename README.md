# 🏋️ Arduino Nano 33 BLE - 專業 VBT 訓練監控系統

本專案將 **Arduino Nano 33 BLE** 打造為專業的 **VBT (Velocity Based Training)** 速度力量訓練設備，支援桌面端 (Python) 與手機端 (Web PWA) 雙平台監控。

---

## 🛠️ 技術規格 (VBT Core)
- **採樣率**: 100Hz (10ms 間隔)，提供高精度的物理積分基礎。
- **物理算法**: 
  - **自動重力校準**: 啟動後自動過濾靜止重力 (Zero-G Offset)。
  - **狀態機偵測**: `IDLE` -> `START` -> `CONCENTRIC` -> `END`。
  - **向心過濾**: 自動忽略下蹲 (Eccentric) 負速，僅紀錄向上推起的有效速度。
- **關鍵指標**: 
  - **MCV (Mean Concentric Velocity)**: 平均向心速度 (m/s)。
  - **Peak Velocity**: 最大峰值速度 (m/s)。
  - **Velocity Loss**: 速度衰減百分比 (疲勞監控)。

---

## 💻 桌面端操作流程 (Python)

### 1. 燒錄 100Hz VBT 韌體
```bash
./bin/arduino-cli upload -p /dev/ttyACM0 --fqbn arduino:mbed_nano:nano33ble MotionSense/MotionSense.ino
```

### 2. 啟動專業監控 (CLI)
即時報數、計數、並分析速度衰減。
```bash
.venv/bin/python vbt_pro.py
```

---

## 📱 手機端部署 (GitHub Pages)
本專案已優化為 PWA (Progressive Web App)，可透過 GitHub Pages 快速部署：

1. 將 `index.html` 與 `manifest.json` 上傳至 GitHub Repository。
2. 進入 Repo 的 **Settings > Pages** 開啟託管功能。
3. 使用 **Android 手機 Chrome 瀏覽器** 開啟對應網址。
4. 點擊瀏覽器選單的 **「新增至主螢幕」**，即可離線作為原生 App 使用。

---

## 📁 核心檔案結構
- `vbt_engine.py`: VBT 核心演算法 (純數學邏輯，易於移植)。
- `vbt_pro.py`: 桌面端 CLI 專業監控程式。
- `index.html`: 手機端 PWA 網頁 App (含 Chart.js 視覺化)。
- `vbt_app.py`: Streamlit 即時視覺化儀表板。
- `MotionSense/`: Arduino 100Hz VBT 專用韌體。

---
*Last Updated: 2026-03-29 by Gemini CLI*
