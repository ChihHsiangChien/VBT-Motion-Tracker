import asyncio
import time
from bleak import BleakScanner, BleakClient
from vbt_engine import VBTEngine

# --- Configuration ---
DEVICE_NAME = "Nano33_Motion"
CHAR_UUID = "19B10001-E8F2-537E-4F6C-D104768A1214"

# Initialize Engines
engine = VBTEngine(dt=0.01)

# Session State
reps = []
best_mcv = 0.0

async def main():
    global best_mcv
    print(f"--- 搜尋 VBT 裝置: {DEVICE_NAME} ---")
    device = await BleakScanner.find_device_by_filter(lambda d, ad: ad.local_name == DEVICE_NAME)
    if not device:
        print("❌ 找不到裝置")
        return

    async with BleakClient(device) as client:
        print(f"✅ 已連線 | 請靜止 0.5 秒進行 [靜態校準]...")
        
        def notification_handler(sender, data):
            global best_mcv
            raw_str = data.decode("utf-8")
            try:
                vals = [float(v) for v in raw_str.split(",")]
                result = engine.update(vals[2])
                
                if result:
                    mcv = result['mcv']
                    reps.append(mcv)
                    if mcv > best_mcv: best_mcv = mcv
                    
                    v_loss = (1 - (mcv / best_mcv)) * 100 if best_mcv > 0 else 0
                    
                    print(f"\n[{time.strftime('%H:%M:%S')}] Rep #{len(reps)}")
                    print(f"  🏎️ 平均速度 (MCV): {mcv:.2f} m/s")
                    print(f"  📉 速度衰減 (Loss): {v_loss:.1f}%")
                    print(f"  ⚡ 峰值速度 (PV):   {result['pv']:.2f} m/s")
                    print("-" * 30)
            except: pass

        await client.start_notify(CHAR_UUID, notification_handler)
        print("🏋️ 監控啟動！請執行一組 5 次的移動測試。")

        try:
            while True:
                await asyncio.sleep(1.0)
        except asyncio.CancelledError: pass
        finally:
            if reps:
                print("\n" + "!"*40)
                print(f"🏁 訓練組統計")
                print(f"總次數: {len(reps)} 下")
                print(f"最佳表現: {best_mcv:.2f} m/s")
                print(f"平均速度: {sum(reps)/len(reps):.2f} m/s")
                print("!"*40 + "\n")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n中斷測試。")
