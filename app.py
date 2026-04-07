import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
from datetime import datetime

# --- 1. 網頁配置 ---
st.set_page_config(page_title="009805 淨值即時監控", layout="wide")

# --- 2. 完整 50 檔成分股與權重 ---
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

# --- 3. 數據抓取函數 (修正 Adj Close 抓取邏輯) ---
@st.cache_data(ttl=60)
def get_all_data(tickers):
    # 下載成份股
    df_stocks = yf.download(tickers, period='2d', interval='1d', progress=False)
    # 下載匯率
    df_fx = yf.download('TWD=X', period='2d', interval='1d', progress=False)
    
    # 修正：針對新版 yfinance，直接提取 Close 價格並處理索引
    prices = df_stocks['Close'] 
    fx_prices = df_fx['Close']
    return prices, fx_prices

# --- 4. 側邊欄 ---
with st.sidebar:
    st.header("⚙️ 參數設定")
    last_nav = st.number_input("昨日官方收盤淨值 (NAV)", value=17.50, format="%.4f")
    if st.button("手動刷新數據"):
        st.cache_data.clear()
        st.rerun()

# --- 5. 核心邏輯處理 ---
st.title("⚡ 009805 新光美國電力基建 - 實時監控儀表板")

tickers = list(COMPONENTS.items())
try:
    prices, fx_prices = get_all_data(list(COMPONENTS.keys()))
    
    # 取得最新匯率與昨日匯率
    current_fx = float(fx_prices.iloc[-1])
    prev_fx = float(fx_prices.iloc[-2])
    fx_change_ratio = current_fx / prev_fx

    stock_results = []
    total_weighted_change = 0

    for ticker, weight in COMPONENTS.items():
        # 修正：從 DataFrame 提取該股的兩日價格
        ticker_prices = prices[ticker].dropna()
        curr_p = ticker_prices.iloc[-1]
        prev_p = ticker_prices.iloc[-2]
        change = (curr_p - prev_p) / prev_p
        
        contribution = change * weight
        total_weighted_change += contribution
        
        stock_results.append({
            "代號": ticker,
            "漲跌幅%": round(change * 100, 2),
            "權重%": round(weight * 100, 2),
            "貢獻度%": round(contribution * 100, 4)
        })

    # --- 6. 淨值計算 ---
    estimated_nav = last_nav * (1 + total_weighted_change) * fx_change_ratio
    nav_diff = estimated_nav - last_nav
    nav_pct = (nav_diff / last_nav) * 100

    # --- 7. 顯示儀表板 ---
    c1, c2, c3 = st.columns(3)
    c1.metric("預估即時淨值", f"{estimated_nav:.4f}", f"{nav_diff:.4f} ({nav_pct:.2f}%)")
    c2.metric("即時美金匯率", f"{current_fx:.2f}", f"{current_fx - prev_fx:.2f}")
    c3.metric("美股成分股總變動", f"{total_weighted_change*100:.2f}%")

    st.markdown("---")

    # --- 8. 熱力圖 ---
    st.subheader("📊 成分股表現熱力圖")
    df_viz = pd.DataFrame(stock_results)
    fig = px.treemap(
        df_viz, path=["代號"], values="權重%",
        color="漲跌幅%", color_continuous_scale='RdYlGn',
        color_continuous_midpoint=0
    )
    st.plotly_chart(fig, use_container_width=True)

    # --- 9. 明細表 ---
    st.subheader("📝 成分股詳細數據")
    st.dataframe(df_viz.sort_values("貢獻度%", ascending=False), use_container_width=True)

except Exception as e:
    st.error(f"數據解析失敗。錯誤訊息: {e}")
    st.info("提示：如果出現 'Close' 或 'Adj Close' 錯誤，通常是 Yahoo 盤中數據尚未完全同步，請稍候再刷新。")

st.caption(f"最後更新時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
