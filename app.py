import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# 1. 頁面基礎設定
st.set_page_config(page_title="009805 專業版監控", page_icon="📈", layout="wide")
st.title("⚡ 009805 新光美國電力基建 (50檔精確權重)")

# 2. 核心權重數據 (對標最新指數權重)
# 如果你發現哪一檔權重變了，直接改後面的數字即可
COMPONENTS = {
    "GEV": 0.1265, "VRT": 0.0975, "ETN": 0.0912, "PWR": 0.0635, "HUBB": 0.0610,
    "NEE": 0.0418, "SO": 0.0355, "DUK": 0.0332, "NXT": 0.0275, "D": 0.0235,
    "AEP": 0.0232, "BE": 0.0222, "FSLR": 0.0205, "ED": 0.0182, "SWX": 0.0179,
    "AGX": 0.0175, "EXC": 0.0162, "MTZ": 0.0156, "PEG": 0.0135, "CEG": 0.0125,
    "EIX": 0.0124, "WEC": 0.0124, "TTEK": 0.0123, "POWL": 0.0121, "ES": 0.0116,
    "ACM": 0.0114, "ETR": 0.0112, "XEL": 0.0104, "ENS": 0.0101, "FE": 0.0098,
    "PPL": 0.0094, "GNRC": 0.0090, "VST": 0.0076, "DTE": 0.0068, "AEE": 0.0067,
    "EVRG": 0.0063, "VICR": 0.0058, "PNW": 0.0054, "CMS": 0.0053, "OGE": 0.0045,
    "PCG": 0.0044, "CNP": 0.0042, "NRG": 0.0042, "LNT": 0.0042, "ENPH": 0.0038,
    "AES": 0.0034, "ITRI": 0.0031, "AMSC": 0.0024, "MEI": 0.0007, "MVST": 0.0003
}

# 3. 數據計算邏輯
if st.button("🚀 執行精確權重刷新"):
    with st.spinner("正在同步 50 檔美股即時報價與匯率..."):
        # 加入 USD/TWD 匯率抓取，讓計算更接近真實淨值
        tickers = list(COMPONENTS.keys()) + ["009805.TW", "TWD=X"]
        data = yf.download(tickers, period="2d", interval="1d", progress=False)['Close']
        
        if not data.empty:
            latest = data.iloc[-1]
            prev = data.iloc[-2]
            
            results = []
            total_impact = 0
            
            # 計算美股漲跌對 ETF 的貢獻
            for t, weight in COMPONENTS.items():
                if t in latest and t in prev:
                    change = (latest[t] - prev[t]) / prev[t]
                    impact = change * weight
                    total_impact += impact
                    results.append({
                        "代號": t,
                        "當前價": f"${latest[t]:.2f}",
                        "今日漲跌": f"{change:+.2%}",
                        "權重": f"{weight:.2%}",
                        "貢獻度": impact
                    })
            
            # 考慮匯率波動 (美金漲 = 009805 受益)
            usd_change = (latest["TWD=X"] - prev["TWD=X"]) / prev["TWD=X"]
            final_est = total_impact + usd_change
            
            # 顯示大字報
            st.divider()
            c1, c2, c3 = st.columns(3)
            c1.metric("美股加權預估", f"{total_impact:+.2%}")
            c2.metric("匯率變動 (USD/TWD)", f"{usd_change:+.2%}")
            c3.metric("總計預估漲跌", f"{final_est:+.2%}", help="這是美股漲跌+匯率變動的綜合預估")
            
            # 顯示表格
            df = pd.DataFrame(results).sort_values("貢獻度", ascending=False)
            st.write("### 📊 成分股即時貢獻明細")
            st.dataframe(
                df.style.format({"貢獻度": "{:+.4%}"}),
                use_container_width=True,
                height=600
            )
            st.success(f"同步完成！台灣時間：{datetime.now().strftime('%H:%M:%S')}")
else:
    st.info("請點擊按鈕刷新。現在美股剛開盤，波動正精彩！")
