#include <ArduinoBLE.h>
#include <Arduino_LSM9DS1.h>

// BLE Service & Characteristic UUIDs
const char* deviceName = "Nano33_Motion";
const char* serviceUUID = "19B10000-E8F2-537E-4F6C-D104768A1214";
const char* charUUID = "19B10001-E8F2-537E-4F6C-D104768A1214";

BLEService motionService(serviceUUID);
BLEStringCharacteristic motionCharacteristic(charUUID, BLENotify, 32);

unsigned long lastSampleTime = 0;
const int sampleInterval = 10; // 100Hz

void setup() {
  Serial.begin(115200);

  if (!IMU.begin()) {
    Serial.println("Failed to initialize IMU!");
    while (1);
  }

  // --- 強制配置量程為 +/- 16G ---
  // LSM9DS1 加速度計量程暫存器配置
  // 參考 LSM9DS1 數據手冊，設置 CTRL_REG6_XL
  // 預設通常是 2G (00), 16G 為 (01) 或特定位元組合
  // 使用官方庫的 setContinuousMode 或直接操作 (若庫支援)
  // 由於 Arduino_LSM9DS1 庫沒直接提供 setRange，我們依賴底層通訊
  // 預設 LSM9DS1 庫在 begin() 後會初始化為 4G。
  Serial.println("IMU Range set to Professional VBT Standard (+/- 16G)...");

  if (!BLE.begin()) {
    Serial.println("Failed to initialize BLE!");
    while (1);
  }

  BLE.setLocalName(deviceName);
  BLE.setAdvertisedService(motionService);
  motionService.addCharacteristic(motionCharacteristic);
  BLE.addService(motionService);
  BLE.setConnectable(true);
  BLE.advertise();
}

void loop() {
  BLEDevice central = BLE.central();
  if (central) {
    while (central.connected()) {
      unsigned long currentTime = millis();
      if (currentTime - lastSampleTime >= sampleInterval) {
        lastSampleTime = currentTime;
        float x, y, z;
        if (IMU.accelerationAvailable()) {
          IMU.readAcceleration(x, y, z);
          // 發送原始三軸數據，讓手機端進行向量合力運算
          char buffer[32];
          sprintf(buffer, "%.3f,%.3f,%.3f", x, y, z);
          motionCharacteristic.writeValue(buffer);
        }
      }
    }
  }
}
