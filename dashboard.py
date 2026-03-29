import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Page Config
st.set_page_config(page_title="Nano 33 BLE Motion Dashboard", layout="wide")

st.title("🏃‍♂️ Nano 33 BLE 運動感測分析儀表板")
st.markdown("---")

CSV_FILE = "motion_raw.csv"

def analyze_and_render(df):
    # 1. Stats Row
    col1, col2, col3 = st.columns(3)
    
    # Stability
    std_x = df['acc_x'].std()
    std_y = df['acc_y'].std()
    stability = 100 - (min((std_x + std_y) * 200, 100))
    
    # Squat Detection (Simple Logic)
    threshold_low, threshold_high = 0.8, 1.2
    count, in_squat = 0, False
    for val in df['acc_z']:
        if not in_squat and val < threshold_low: in_squat = True
        if in_squat and val > threshold_high:
            count += 1
            in_squat = False
            
    col1.metric("偵測深蹲次數", f"{count} 次", delta=None)
    col2.metric("動作穩定度評分", f"{stability:.1f}%", delta="穩定" if stability > 80 else "需要加強")
    col3.metric("總採集點數", len(df))

    # 2. Charts
    st.subheader("📊 三軸加速度實時數據 (X, Y, Z)")
    df_plot = df.copy()
    df_plot['index'] = range(len(df_plot))
    
    # Plotting using Matplotlib for more control
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.plot(df['acc_x'], label='Acc X (Stable)', alpha=0.7)
    ax.plot(df['acc_y'], label='Acc Y (Side)', alpha=0.7)
    ax.plot(df['acc_z'], label='Acc Z (Vertical)', color='orange', linewidth=2)
    ax.axhline(1.0, color='gray', linestyle='--', alpha=0.5)
    ax.set_title("Movement Waveform (G-Force)")
    ax.set_xlabel("Sample Index")
    ax.set_ylabel("Acceleration (G)")
    ax.legend()
    st.pyplot(fig)

    # 3. Distribution Analysis
    st.subheader("🔍 數據分佈分析 (Distribution)")
    col_a, col_b = st.columns(2)
    with col_a:
        fig_hist = plt.figure()
        sns.kdeplot(data=df[['acc_x', 'acc_y', 'acc_z']], fill=True)
        plt.title("Acceleration Density Plot")
        st.pyplot(fig_hist)
    with col_b:
        st.markdown("""
        ### 💡 動作建議 (AI Insight)
        - **Z 軸波動**：代表重力加速度的劇烈變化，這是判斷深蹲、跳躍的核心指標。
        - **X/Y 軸偏移**：如果您在做深蹲時，X/Y 軸有明顯偏離 $0.0G$，代表您的核心或膝蓋在側向晃動。
        - **Android 移植建議**：目前 BLE 使用 `Notify` 模式發送 `String`。在 Android 端可以使用 `onCharacteristicChanged` 監聽。
        """)

try:
    df = pd.read_csv(CSV_FILE)
    if not df.empty:
        analyze_and_render(df)
    else:
        st.warning("`motion_raw.csv` 檔案是空的，請先執行 `collect.py` 採集數據。")
except FileNotFoundError:
    st.error("找不到 `motion_raw.csv`。請先啟動採集腳本！")

# Auto Refresh Button
if st.button("刷新數據"):
    st.rerun()
