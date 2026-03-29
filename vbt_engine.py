import numpy as np
import time

class VBTEngine:
    def __init__(self, dt=0.01):
        self.dt = dt
        self.gravity = 1.0
        self.velocity = 0.0
        self.max_velocity = 0.0
        self.velocities = []
        
        # States: 0=IDLE, 1=START, 2=CONCENTRIC, 3=END
        self.state = 0
        self.start_time = 0
        
        self.calib_buffer = []
        self.is_calibrated = False

    def update(self, raw_z):
        if not self.is_calibrated:
            self.calib_buffer.append(raw_z)
            if len(self.calib_buffer) >= 100: # 增加到 100 筆確保校準更精確
                self.gravity = np.mean(self.calib_buffer)
                self.is_calibrated = True
                print(f"--- 校準完成: 基準重力 G={self.gravity:.4f} ---")
            return None

        # 1. 計算淨加速度
        net_accel = raw_z - self.gravity
        
        # 2. 強力噪聲過濾 (Deadzone)
        # 如果波動小於 0.08G，直接視為絕對靜止
        if abs(net_accel) < 0.08:
            net_accel = 0.0
            if self.state == 0:
                # 待機中：強制速度為 0，並微調重力基準
                self.velocity = 0.0
                self.gravity = self.gravity * 0.9 + raw_z * 0.1
                return None # 絕對不處理後續邏輯

        # 3. 速度積分
        self.velocity += net_accel * 9.81 * self.dt

        # --- VBT 核心狀態機 ---
        result = None
        
        if self.state == 0: # IDLE (待機)
            # 啟動門檻：瞬間加速度必須突破 0.15G
            if abs(net_accel) > 0.15:
                self.state = 1
                self.start_time = time.time()
                self.velocities = []
                self.max_velocity = 0.0
            else:
                self.velocity = 0.0 # 沒達標前，速度依舊鎖死在 0
        
        elif self.state == 1: # START (動作辨識)
            # 檢查是否為有效啟動：0.5 秒內必須產生足夠的速度
            if self.velocity > 0.12:
                self.state = 2
            elif time.time() - self.start_time > 0.5:
                # 誤觸：啟動半秒後速度還是太慢，滾回 IDLE
                self.state = 0
                self.velocity = 0.0
                
        elif self.state == 2: # CONCENTRIC (向心加速中)
            if self.velocity > 0:
                self.velocities.append(self.velocity)
                if self.velocity > self.max_velocity:
                    self.max_velocity = self.velocity
            
            # 結束判定：速度回落至 0.1 以下，或超時
            if (self.velocity < 0.1 and len(self.velocities) > 10) or (time.time() - self.start_time > 6.0):
                self.state = 3
                
        elif self.state == 3: # END (結算)
            # 有效動作門檻：向心速度峰值必須 > 0.25 m/s
            if len(self.velocities) > 15 and self.max_velocity > 0.25:
                mcv = np.mean(self.velocities)
                pv = self.max_velocity
                result = {"mcv": mcv, "pv": pv}
            
            self.state = 0
            self.velocity = 0.0
            
        return result
