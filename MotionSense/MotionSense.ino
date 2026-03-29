#include <ArduinoBLE.h>
#include <Arduino_LSM9DS1.h>

// BLE Service & Characteristic UUIDs
const char* deviceName = "Nano33_Motion";
const char* serviceUUID = "19B10000-E8F2-537E-4F6C-D104768A1214";
const char* charUUID = "19B10001-E8F2-537E-4F6C-D104768A1214";

BLEService motionService(serviceUUID);
BLEStringCharacteristic motionCharacteristic(charUUID, BLENotify, 32);

unsigned long lastSampleTime = 0;
const int sampleInterval = 10; // 10ms = 100Hz (VBT Standard)

void setup() {
  Serial.begin(115200); // Higher baud rate for VBT calibration

  if (!IMU.begin()) {
    Serial.println("Failed to initialize IMU!");
    while (1);
  }

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
  Serial.println("VBT Motion Engine Active (100Hz)...");
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
          
          // Format: "x,y,z" with 3 decimal precision
          // Optimized for VBT processing in Python
          char buffer[32];
          sprintf(buffer, "%.3f,%.3f,%.3f", x, y, z);
          motionCharacteristic.writeValue(buffer);
        }
      }
    }
  }
}
