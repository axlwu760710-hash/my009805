import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
from datetime import datetime
import streamlit.components.v1 as components

# --- 1. 網頁配置 ---
st.set_page_config(page_title="009805 電力基建即時預估 | 專業版", layout="wide", initial_sidebar_state="expanded")

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

# --- 3. 數據抓取 ---
@st.cache_data(ttl=60)
def get_all_data(tickers):
    df_stocks = yf.download(tickers, period='5d', interval='1d', progress=False)
    df_fx = yf.download('TWD=X', period='5d', interval='1d', progress=False)
    prices = df_stocks['Close'] if isinstance(df_stocks.columns, pd.MultiIndex) else df_stocks
    fx_prices = df_fx['Close']['TWD=X'] if isinstance(df_fx.columns, pd.MultiIndex) else df_fx['Close']
    return prices, fx_prices

# --- 4. 側邊欄：參數與【贊助區】 ---
with st.sidebar:
    st.title("🛡️ 控制中心")
    query_nav = st.query_params.get("nav", "15.11")
    last_nav = st.number_input("昨日官方淨值 (NAV)", value=float(query_nav), format="%.4f")
    if str(last_nav) != query_nav:
        st.query_params["nav"] = str(last_nav)
    
    if st.button("🚀 強制刷新數據"):
        st.cache_data.clear()
        st.rerun()

    st.markdown("---")
    # --- 變現區 A：贊助按鈕 ---
    st.subheader("☕ 支持作者")
    st.write("如果預估精準，歡迎贊助一杯咖啡，讓工具持續維護！")
    # 這裡可以放你的 Buy Me a Coffee 或 綠界/街口 連結
    st.markdown("[👉 點我贊助 (Buy Me a Coffee)](https://www.buymeacoffee.com/yourname)")
    
    st.markdown("---")
    # --- 變現區 B：推薦連結 (Affiliate) ---
    st.subheader("📈 投資推薦")
    st.info("還沒開通美股？使用以下連結開戶享手續費優惠：")
    st.markdown("- [富邦證券開戶送好禮](https://example.com)")
    st.markdown("- [Firstrade 免費開戶連結](https://example.com)")

# --- 5. 主頁面：核心數據 ---
st.title("⚡ 009805 美國電力基建 - 淨值導航")

try:
    prices, fx_prices = get_all_data(list(COMPONENTS.keys()))
    fx_clean = fx_prices.dropna()
    current_fx = float(fx_clean.iloc[-1])
    prev_fx = float(fx_clean.iloc[-2])
    fx_change_ratio = current_fx / prev_fx

    stock_results = []
    total_weighted_change = 0

    for ticker, weight in COMPONENTS.items():
        if ticker in prices.columns:
            ticker_series = prices[ticker].dropna()
            if len(ticker_series) >= 2:
                curr_p = ticker_series.iloc[-1]; prev_p = ticker_series.iloc[-2]
                change = (curr_p - prev_p) / prev_p
                total_weighted_change += (change * weight)
                stock_results.append({
                    "代號": ticker, "漲跌幅%": round(change * 100, 2),
                    "權重%": round(weight * 100, 2), "貢獻度%": round(change * weight * 100, 4)
                })

    est_nav = last_nav * (1 + total_weighted_change) * fx_change_ratio
    nav_diff = est_nav - last_nav

    # 儀表板
    col1, col2, col3 = st.columns(3)
    col1.metric("即時預估淨值", f"${est_nav:.4f}", f"{nav_diff:.4f} ({nav_diff/last_nav:.2%})")
    col2.metric("即時美金匯率", f"{current_fx:.2f}", f"{(current_fx-prev_fx):.2f}")
    col3.metric("成分股加權變動", f"{total_weighted_change:.2%}")

    # --- 變現區 C：橫幅廣告位 (Banner Ad) ---
    st.markdown("---")
    components.html("""
        <div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; text-align: center;">
            <p style="color: #555; margin: 0;">廣告預留位 (AD SPACE)</p>
            <p style="font-size: 12px; color: #888;">合作洽談：your_email@example.com</p>
        </div>
    """, height=80)
    st.markdown("---")

    # 熱力圖
    df_viz = pd.DataFrame(stock_results)
    st.subheader("📊 盤面動態 (Treemap)")
    fig = px.treemap(df_viz, path=["代號"], values="權重%", color="漲跌幅%", 
                     color_continuous_scale='RdYlGn', color_continuous_midpoint=0)
    st.plotly_chart(fig, use_container_width=True)

    # 數據表
    st.subheader("📝 成分股貢獻明細")
    st.dataframe(df_viz.sort_values("貢獻度%", ascending=False), use_container_width=True)

except Exception as e:
    st.error(f"系統運行中... 請點擊刷新按鈕。 (Error: {e})")

st.caption(f"數據最後更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 本工具僅供參考，投資請自行評估風險。")
