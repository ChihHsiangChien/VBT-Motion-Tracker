# 🏋️ VBT Pro Motion Tracker (v3.3)

本專案將 **Arduino Nano 33 BLE** 轉化為極致精確的 **VBT (Velocity Based Training)** 專業訓練設備。透過 100Hz 高頻採樣、向量合力投影演算法以及 Web PWA 技術，提供媲美商用儀器的監控體驗。

---

## 🚀 核心物理技術 (v3.3)
- **$\pm 16G$ 專業量程**: 解鎖 LSM9DS1 IMU 的最大動態範圍，防止高爆發動作（如抓舉）產生訊號剪裁。
- **方向感知引擎 (Direction-Aware)**: 
  - 透過 **向量點積投影 (Vector Projection)**，自動辨識垂直地面運動分量。
  - **向上過濾**: 指標僅針對「克服重力 (Concentric)」的向上位移進行積分，自動拋棄下蹲或放下動作的干擾。
- **動態重力補償**: 靜止時以 2% 權重持續校準基準重力，補償環境溫飄與微小震動。

---

## 📱 手機 App 亮點 (PWA)
- **運動配置檔 (Exercise Profiles)**: 
  - 預設 **硬舉、深蹲、臥推、抓舉** 四大模式。
  - 針對不同運動自動切換「啟動門檻」與「緩衝參數」，並支援個別運動的個人化儲存。
- **多模式語音系統**: 
  - 支援「僅報平均」、「僅報峰值」或「兩者皆報」。
  - 語速可調 (最高 3.0x)，具備**即時播報中斷**機制，確保連續動作不延遲。
- **極致高對比 UI**: 
  - 針對健身房環境設計的「白底黑字」數據面板，確保在汗水與晃動中依然清晰。
- **視覺化分析**: 
  - **即時波形圖**: 追蹤單次動作的力量曲線，保留至下次啟動前。
  - **組數趨勢圖**: 監控整組訓練的速度衰減 (Velocity Loss)。
  - **歷史數據卡片**: 點擊展開可回顧歷次訓練的完整曲線。

---

## 🛠️ 操作指南

### 1. 燒錄硬體
使用 `arduino-cli` 上傳專用韌體：
```bash
./bin/arduino-cli upload -p /dev/ttyACM0 --fqbn arduino:mbed_nano:nano33ble MotionSense/MotionSense.ino
```

### 2. 雲端 App 部署 (GitHub Pages)
直接訪問您的 GitHub 網址，並點擊 **「新增至主螢幕」**：
👉 **https://ChihHsiangChien.github.io/VBT-Motion-Tracker/**

### 3. 穩定連線與自動診斷
- **數據心跳**: 介面底部實時顯示 RAW 數據與封包頻率 (Hz)。
- **自動偵錯**: 系統每 0.5 秒偵測一次流，若 Arduino 斷電或斷連，UI 會在 1.5 秒內自動自癒並重置狀態。

---

## 📁 檔案說明
- `index.html`: 全功能手機 App (PWA)。
- `vbt_engine.py`: VBT 核心物理演算法 (移植參考)。
- `MotionSense/`: Arduino 100Hz / 16G 專用韌體。

---
*Developed by Gemini CLI | 2026-03-29*
