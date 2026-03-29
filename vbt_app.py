import streamlit as st
import asyncio
import pandas as pd
import threading
from bleak import BleakScanner, BleakClient
from collections import deque
import time
from vbt_engine import VBTEngine

# Configuration
DEVICE_NAME = "Nano33_Motion"
CHAR_UUID = "19B10001-E8F2-537E-4F6C-D104768A1214"

# State
shared_buffer = deque(maxlen=200) # 2 seconds of data at 100Hz
shared_results = deque(maxlen=10) # Store last 10 MCVs
shared_status = ["Waiting..."]
shared_running = [False]
vbt = VBTEngine(dt=0.01)

def ble_thread_func():
    async def run_ble():
        shared_status[0] = "Searching for Nano33_Motion..."
        device = await BleakScanner.find_device_by_filter(lambda d, ad: ad.local_name == DEVICE_NAME)
        if not device:
            shared_status[0] = "Device Not Found."
            shared_running[0] = False
            return

        async with BleakClient(device) as client:
            shared_status[0] = f"Connected to {device.address}"
            def callback(sender, data):
                raw_str = data.decode("utf-8")
                try:
                    vals = [float(v) for v in raw_str.split(",")]
                    if len(vals) == 3:
                        shared_buffer.append({"X": vals[0], "Y": vals[1], "Z": vals[2]})
                        # Core VBT Logic
                        res = vbt.update(vals[2])
                        if res:
                            shared_results.append(res)
                            # TTS in separate thread or via a flag
                except: pass

            await client.start_notify(CHAR_UUID, callback)
            while shared_running[0]: await asyncio.sleep(0.5)
            await client.stop_notify(CHAR_UUID)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_ble())

# UI
st.set_page_config(page_title="VBT Monitor", layout="wide")
st.title("🏋️‍♂️ VBT 速度力量訓練監控系統")

with st.sidebar:
    if not shared_running[0]:
        if st.button("🚀 Start VBT Session"):
            shared_running[0] = True
            threading.Thread(target=ble_thread_func, daemon=True).start()
    else:
        if st.button("🛑 Stop Session"):
            shared_running[0] = False
    st.info(f"Status: {shared_status[0]}")

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("最新動作結果")
    if shared_results:
        last = shared_results[-1]
        st.metric("平均向心速度 (MCV)", f"{last['mcv']:.2f} m/s")
        st.metric("最大峰值速度 (PV)", f"{last['pv']:.2f} m/s")
    else:
        st.write("等待第一組動作...")

with col2:
    st.subheader("垂直加速度 (100Hz)")
    chart_place = st.empty()

# Main Loop
while shared_running[0]:
    if shared_buffer:
        df = pd.DataFrame(list(shared_buffer))
        chart_place.line_chart(df[['Z']], height=300)
    time.sleep(0.1)
