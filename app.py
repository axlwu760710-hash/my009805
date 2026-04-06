import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# 1. 頁面設定
st.set_page_config(page_title="009805 完整監控", page_icon="⚡", layout="wide")
st.title("⚡ 009805 新光美國電力基建 (完整 50 檔)")

# 2. 完整 50 檔成分股與權重數據
COMPONENTS = {
    "GEV": 0.1276, "VRT": 0.0979, "ETN": 0.0904, "PWR": 0.0640, "HUBB": 0.0615,
    "NEE": 0.0424, "SO": 0.0351, "DUK": 0.0335, "NXT": 0.0272, "D": 0.0232,
    "AEP": 0.0231, "BE": 0.0224, "FSLR": 0.0204, "ED": 0.0180, "SWX": 0.0178,
    "AGX": 0.0176, "EXC": 0.0163, "MTZ": 0.0155, "PEG": 0.0133, "CEG": 0.0124,
    "EIX": 0.0124, "WEC": 0.0124, "TTEK": 0.0123, "POWL": 0.0121, "ES": 0.0115,
    "ACM": 0.0113, "ETR": 0.0111, "XEL": 0.0103, "ENS": 0.0100, "FE": 0.0097,
    "PPL": 0.0093, "GNRC": 0.0089, "VST": 0.0074, "DTE": 0.0067, "AEE": 0.0066,
    "EVRG": 0.0062, "VICR": 0.0057, "PNW": 0.0053, "CMS": 0.0052, "OGE": 0.0044,
    "PCG": 0.0043, "CNP": 0.0041, "NRG": 0.0041, "LNT": 0.0041, "ENPH": 0.0037,
    "AES": 0.0033, "ITRI": 0.0030, "AMSC": 0.0023, "MEI": 0.0006, "MVST": 0.0002
}

# 3. 抓取與計算邏輯
if st.button("🚀 刷新 50 檔即時數據"):
    with st.spinner("正在搬運 50 檔美股即時報價..."):
        tickers = list(COMPONENTS.keys()) + ["009805.TW"]
        # 抓取兩天資料計算漲跌幅
        data = yf.download(tickers, period="2d", interval="1d", progress=False)['Close']
        latest = data.iloc[-1]
        prev = data.iloc[-2]
        
        results = []
        total_impact = 0
        
        for t, weight in COMPONENTS.items():
            change = (latest[t] - prev[t]) / prev[t]
            contribution = change * weight
            total_impact += contribution
            results.append({
                "代號": t,
                "現價": f"{latest[t]:.2f}",
                "今日漲跌": f"{change:+.2%}",
                "權重": f"{weight:.2%}",
                "對ETF貢獻": contribution
            })
        
        # 4. 顯示頂部大字報
        real_change = (latest["009805.TW"] - prev["009805.TW"]) / prev["009805.TW"]
        c1, c2 = st.columns(2)
        c1.metric("預估 009805 總漲跌 (50檔加權)", f"{total_impact:+.2%}")
        c2.metric("台股 009805 現價漲跌", f"{real_change:+.2%}")
        
        # 5. 顯示完整列表
        df = pd.DataFrame(results).sort_values("對ETF貢獻", ascending=False)
        st.write("### 📊 50 檔成分股貢獻度明細")
        st.dataframe(
            df.style.format({"對ETF貢獻": "{:+.4%}"}),
            use_container_width=True,
            height=600  # 固定高度方便捲動看 50 檔
        )
        st.success(f"更新成功！時間：{datetime.now().strftime('%H:%M:%S')}")
else:
    st.info("點擊上方按鈕，即刻掌握 50 檔電力基建股動向。")
