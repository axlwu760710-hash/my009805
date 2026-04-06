import streamlit as st
import yfinance as yf
import pandas as pd

# 1. 基礎設定
st.set_page_config(page_title="009805監控", layout="wide")
st.title("⚡ 009805 電力基建即時監控")

# 2. 核心權重數據
COMPONENTS = {
    "GEV": 0.1276, "VRT": 0.0979, "ETN": 0.0904, "PWR": 0.0640, "HUBB": 0.0615,
    "NEE": 0.0424, "SO": 0.0351, "DUK": 0.0335, "NXT": 0.0272, "D": 0.0232,
    "CEG": 0.0124, "VST": 0.0074, "AMSC": 0.0023
}

# 3. 抓取按鈕
if st.button("🚀 立即刷新數據"):
    with st.spinner("努力抓取美股報價中..."):
        tickers = list(COMPONENTS.keys()) + ["009805.TW"]
        data = yf.download(tickers, period="2d", interval="1d", progress=False)['Close']
        latest, prev = data.iloc[-1], data.iloc[-2]
        
        results = []
        total_est = 0
        for t, weight in COMPONENTS.items():
            change = (latest[t] - prev[t]) / prev[t]
            impact = change * weight
            total_est += impact
            results.append({"代號": t, "漲跌": f"{change:+.2%}", "貢獻": impact})
        
        # 顯示大字報
        st.metric("預估 009805 總漲跌", f"{total_est:+.2%}")
        st.dataframe(pd.DataFrame(results).sort_values("貢獻", ascending=False))
else:
    st.write("請按下按鈕開始。現在美股盤前已有部分數據！")
