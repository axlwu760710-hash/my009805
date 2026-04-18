import yfinance as yf
import pandas as pd
import datetime
import os

# 1. 自動偵測 index.html 的位置
current_dir = os.path.dirname(os.path.abspath(__file__))
index_path = os.path.join(current_dir, "index.html")

# 2. 50 檔精確權重
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

def generate_dashboard():
    # 抓取 50 檔 + 匯率
    tickers = list(COMPONENTS.keys()) + ["TWD=X"]
    data = yf.download(tickers, period="2d", interval="1d", progress=False)['Close']
    
    if data.empty or len(data) < 2:
        return None, 0, 0, 0
    
    latest = data.iloc[-1]
    prev = data.iloc[-2]
    
    total_impact = 0
    table_rows = ""
    
    # 計算美股貢獻
    for t, weight in COMPONENTS.items():
        if t in latest and t in prev:
            change = (latest[t] - prev[t]) / prev[t]
            impact = change * weight
            total_impact += impact
            
            # 使用適合你藍色 UI 的顏色
            color = "#22c55e" if change >= 0 else "#ef4444"
            table_rows += f"""
            <tr>
                <td><b class="ticker">{t}</b></td>
                <td style="color:{color}">{change:+.2%}</td>
                <td><span class="weight-tag">{weight:.2%}</span></td>
                <td style="color:{color}; font-weight:bold;">{impact:+.4%}</td>
            </tr>
            """
            
    # 匯率計算
    usd_change = (latest["TWD=X"] - prev["TWD=X"]) / prev["TWD=X"]
    final_est = total_impact + usd_change
    
    return table_rows, total_impact, usd_change, final_est

# 執行主程式
rows, impact, fx, total = generate_dashboard()

if rows:
    # 讀取模板
    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()

    # --- 關鍵修正：將數據填入對應標籤 ---
    html = html.replace("", rows)
    html = html.replace("", f"{impact:+.2%}")
    html = html.replace("", f"{fx:+.2%}")
    html = html.replace("", f"{total:+.2%}")
    html = html.replace("", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    # 寫回檔案
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html)
    print("數據同步成功！")
else:
    print("數據獲取失敗，請檢查網路或 API。")
import streamlit as st
import streamlit.components.v1 as components
import os

# 1. 基礎設定
st.set_page_config(page_title="009805 監控終端", layout="wide")

# 2. 定位 index.html 的絕對路徑
current_dir = os.path.dirname(os.path.abspath(__file__))
index_path = os.path.join(current_dir, "index.html")

# 3. 標題
st.title("⚡ 009805 美國電力基建 - 核心監測終端")

# 4. 讀取並顯示邏輯
if os.path.exists(index_path):
    try:
        with open(index_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        
        # 顯示網頁內容
        components.html(html_content, height=1200, scrolling=True)
    except Exception as e:
        st.error(f"讀取網頁時發生錯誤：{e}")
else:
    # 如果檔案不存在，顯示提示並引導
    st.warning("⚠️ 尚未偵測到動態數據檔 (index.html)")
    st.info("請確保您已執行 GitHub Actions 中的 'Daily 009805 Update'，它會自動產生這個檔案。")
    
    # 備援：直接嵌入 GitHub Pages 網址
    GITHUB_URL = "https://axlwu760710-hash.github.io/009805viewer/"
    st.write("---")
    st.write("正在從備援網址載入...")
    components.iframe(GITHUB_URL, height=800, scrolling=True)

# 5. 頁尾說明
st.caption("數據同步由 GitHub Actions 驅動 | 若數據未更新請檢查 Action 執行狀態")
