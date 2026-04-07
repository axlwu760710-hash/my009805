import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
from datetime import datetime

# --- 1. 網頁配置 ---
st.set_page_config(page_title="009805 淨值即時監控", layout="wide")

# --- 2. 定義 009805 成分股與權重 (請根據最新公告定期微調權重) ---
# 這裡列出前幾大龍頭，其餘小權重股已簡化處理，總計應為 100%
COMPONENTS = {
    'GEV': 0.082, 'ETN': 0.078, 'PWR': 0.065, 'VRT': 0.054, 'SRE': 0.048,
    'NEE': 0.045, 'AEP': 0.042, 'D': 0.040, 'EXC': 0.038, 'SO': 0.035,
    'AME': 0.032, 'HUBB': 0.030, 'CEG': 0.028, 'VST': 0.025, 'PCG': 0.022,
    'ED': 0.020, 'EIX': 0.018, 'PEG': 0.018, 'WEC': 0.015, 'ES': 0.015,
    'DTE': 0.014, 'ETR': 0.014, 'FE': 0.013, 'PPL': 0.012, 'AEE': 0.012,
    'LNT': 0.011, 'EVRG': 0.011, 'CMS': 0.010, 'NRG': 0.010, 'NI': 0.009,
    'PNW': 0.009, 'ATO': 0.008, 'SR': 0.008, 'OGE': 0.008, 'CNP': 0.007,
    'ALE': 0.007, 'PNM': 0.006, 'BKH': 0.006, 'NWN': 0.005, 'AVA': 0.005,
    'MGEE': 0.004, 'NWE': 0.004, 'POR': 0.004, 'CWT': 0.004, 'SJW': 0.003,
    'AWR': 0.003, 'YORW': 0.002, 'ARTNA': 0.002, 'MSEX': 0.002, 'WTRG': 0.001
}

# --- 3. 數據抓取函數 ---
@st.cache_data(ttl=60) # 每 60 秒快取一次，兼顧即時與性能
def get_all_data(tickers):
    # 抓取成份股兩天份數據以便計算漲跌
    data = yf.download(tickers, period='2d', interval='1d', progress=False)
    # 抓取即時匯率
    fx_data = yf.download('TWD=X', period='2d', interval='1d', progress=False)
    return data['Adj Close'], fx_data['Adj Close']

# --- 4. 側邊欄：設定昨日官網淨值 ---
with st.sidebar:
    st.header("⚙️ 參數設定")
    # 請根據投信官網每日更新此數值
    last_nav = st.number_input("昨日官方收盤淨值 (NAV)", value=17.50, format="%.4f")
    st.caption("提示：台股開盤時，此工具會追蹤美股盤後/盤前波動。")
    if st.button("手動刷新數據"):
        st.cache_data.clear()
        st.rerun()

# --- 5. 核心邏輯處理 ---
st.title("⚡ 009805 新光美國電力基建 - 實時監控儀表板")

tickers = list(COMPONENTS.keys())
try:
    prices, fx_prices = get_all_data(tickers)
    
    current_fx = fx_prices['TWD=X'].iloc[-1]
    prev_fx = fx_prices['TWD=X'].iloc[-2]
    fx_change_ratio = current_fx / prev_fx

    stock_results = []
    total_weighted_change = 0

    for ticker, weight in COMPONENTS.items():
        curr_p = prices[ticker].iloc[-1]
        prev_p = prices[ticker].iloc[-2]
        change = (curr_p - prev_p) / prev_p
        
        contribution = change * weight
        total_weighted_change += contribution
        
        stock_results.append({
            "代號": ticker,
            "漲跌幅%": round(change * 100, 2),
            "權重%": round(weight * 100, 2),
            "貢獻度%": round(contribution * 100, 4)
        })

    # --- 6. 淨值估算公式 ---
    # 預估淨值 = 昨日淨值 * (1 + 成分股加權變動) * 匯率變動比率
    estimated_nav = last_nav * (1 + total_weighted_change) * fx_change_ratio
    nav_diff = estimated_nav - last_nav
    nav_pct = (nav_diff / last_nav) * 100

    # --- 7. 儀表板顯示 ---
    c1, c2, c3 = st.columns(3)
    c1.metric("預估即時淨值", f"{estimated_nav:.4f}", f"{nav_diff:.4f} ({nav_pct:.2f}%)")
    c2.metric("即時美金匯率", f"{current_fx:.2f}", f"{current_fx - prev_fx:.2f}")
    c3.metric("美股成分股總變動", f"{total_weighted_change*100:.2f}%")

    st.markdown("---")

    # --- 8. [A] 圖表派：熱力圖 ---
    st.subheader("📊 成分股表現熱力圖 (大小=權重, 顏色=漲跌)")
    df_viz = pd.DataFrame(stock_results)
    fig = px.treemap(
        df_viz,
        path=["代號"],
        values="權重%",
        color="漲跌幅%",
        color_continuous_scale='RdYlGn',
        color_continuous_midpoint=0,
        hover_data=["貢獻度%"]
    )
    st.plotly_chart(fig, use_container_width=True)

    # --- 9. [B] 功能派：貢獻度清單 ---
    col_left, col_right = st.columns([2, 1])
    with col_left:
        st.subheader("📝 成分股詳細數據")
        st.dataframe(df_viz.sort_values("貢獻度%", ascending=False), height=400, use_container_width=True)
    
    with col_right:
        st.subheader("💡 盤面小結")
        top_stock = df_viz.iloc[df_viz['貢獻度%'].idxmax()]
        bottom_stock = df_viz.iloc[df_viz['貢獻度%'].idxmin()]
        st.write(f"✅ **最強貢獻：** {top_stock['代號']} ({top_stock['貢獻度%']}%)")
        st.write(f"❌ **最大拖累：** {bottom_stock['代號']} ({bottom_stock['貢獻度%']}%)")
        st.write(f"🌎 **匯率影響：** {((fx_change_ratio-1)*100):.2f}% (台幣貶值有利淨值)")

except Exception as e:
    st.error(f"數據抓取失敗，請檢查網路或稍後再試。錯誤訊息: {e}")

st.caption(f"最後更新時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 數據來源: Yahoo Finance")
