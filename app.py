import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
from datetime import datetime
import streamlit.components.v1 as components

# --- 1. 網頁配置 ---
st.set_page_config(page_title="009805 電力基建監控 | 2026專業版", layout="wide")

# --- 2. 【2026/04 最新官方權重校正】 ---
# 數據源：根據最新說明書與券商APP持股比例校對 (GEV 12.76%, VRT 9.79%)
COMPONENTS = {
    'GEV': 0.1276, 'VRT': 0.0979, 'ETN': 0.0904, 'PWR': 0.0640, 'HUBB': 0.0615,
    'NEE': 0.0424, 'SO': 0.0351, 'DUK': 0.0335, 'NXT': 0.0272, 'D': 0.0232,
    'EXC': 0.0220, 'SRE': 0.0210, 'AEP': 0.0200, 'AME': 0.0190, 'CEG': 0.0180,
    'VST': 0.0170, 'PCG': 0.0160, 'ED': 0.0150, 'EIX': 0.0140, 'PEG': 0.0130,
    'WEC': 0.0120, 'ES': 0.0120, 'DTE': 0.0110, 'ETR': 0.0110, 'FE': 0.0100,
    'PPL': 0.0100, 'AEE': 0.0090, 'LNT': 0.0090, 'EVRG': 0.0080, 'CMS': 0.0080,
    'NRG': 0.0080, 'NI': 0.0070, 'PNW': 0.0070, 'ATO': 0.0060, 'SR': 0.0060,
    'OGE': 0.0060, 'CNP': 0.0050, 'ALE': 0.0050, 'PNM': 0.0050, 'BKH': 0.0040,
    'NWN': 0.0040, 'AVA': 0.0040, 'MGEE': 0.0030, 'NWE': 0.0030, 'POR': 0.0030,
    'CWT': 0.0030, 'SJW': 0.0020, 'AWR': 0.0020, 'YORW': 0.0020, 'WTRG': 0.0010
}

# --- 3. 數據抓取 ---
@st.cache_data(ttl=60)
def get_all_data(tickers):
    df_stocks = yf.download(tickers, period='5d', interval='1d', progress=False)
    df_fx = yf.download('TWD=X', period='5d', interval='1d', progress=False)
    # 處理多重索引問題
    prices = df_stocks['Close'] if isinstance(df_stocks.columns, pd.MultiIndex) else df_stocks
    fx_prices = df_fx['Close']['TWD=X'] if isinstance(df_fx.columns, pd.MultiIndex) else df_fx['Close']
    return prices, fx_prices

# --- 4. 側邊欄：參數設定與變現區 ---
with st.sidebar:
    st.header("⚙️ 控制中心")
    # 網址記憶功能：F5 重新整理後 NAV 不會重置
    query_nav = st.query_params.get("nav", "15.11")
    last_nav = st.number_input("昨日官方淨值 (NAV)", value=float(query_nav), format="%.4f")
    if str(last_nav) != query_nav:
        st.query_params["nav"] = str(last_nav)
    
    if st.button("🚀 刷新即時數據"):
        st.cache_data.clear()
        st.rerun()

    st.markdown("---")
    # --- 💰 Ko-fi 贊助區 (請換成你在 Ko-fi 設定的 ID) ---
    kofi_id = "009805pro" 
    st.subheader("☕ 支持開發者")
    components.html(f"""
        <div style="text-align: center;">
            <a href="https://ko-fi.com/{kofi_id}" target="_blank">
                <img src="https://storage.ko-fi.com/cdn/kofi2.png?v=3" 
                     alt="Support me on Ko-fi" 
                     style="height: 45px; border-radius: 5px; box-shadow: 0px 4px 8px rgba(0,0,0,0.1);">
            </a>
            <p style="font-size: 12px; color: #666; margin-top: 8px;">預估準確？贊助咖啡支持持續營運</p>
        </div>
    """, height=100)

# --- 5. 主頁面顯示 ---
st.title("⚡ 009805 美國電力基建 - 即時導航")

try:
    prices, fx_prices = get_all_data(list(COMPONENTS.keys()))
    fx_clean = fx_prices.dropna()
    current_fx = float(fx_clean.iloc[-1])
    prev_fx = float(fx_clean.iloc[-2])
    fx_ratio = current_fx / prev_fx

    stock_results = []
    total_change = 0
    for t, w in COMPONENTS.items():
        if t in prices.columns:
            s = prices[t].dropna()
            if len(s) >= 2:
                chg = (s.iloc[-1] - s.iloc[-2]) / s.iloc[-2]
                total_change += (chg * w)
                stock_results.append({
                    "代號": t, 
                    "漲跌%": round(chg*100, 2), 
                    "權重%": round(w*100, 2), 
                    "貢獻%": round(chg*w*100, 4)
                })

    # 計算預估淨值
    est_nav = last_nav * (1 + total_change) * fx_ratio
    diff = est_nav - last_nav

    # 儀表板
    col1, col2, col3 = st.columns(3)
    col1.metric("預估即時淨值", f"${est_nav:.4f}", f"{diff:.4f} ({diff/last_nav:.2%})")
    col2.metric("即時匯率 (USD/TWD)", f"{current_fx:.2f}", f"{(current_fx-prev_fx):.2f}")
    col3.metric("成分股加權總變動", f"{total_change:.2%}")

    st.markdown("---")
    # 熱力圖 (Treemap)
    df = pd.DataFrame(stock_results)
    st.subheader("📊 盤面表現 (Treemap)")
    fig = px.treemap(df, path=["代號"], values="權重%", color="漲跌%", 
                     color_continuous_scale='RdYlGn', color_continuous_midpoint=0)
    st.plotly_chart(fig, use_container_width=True)

    # 詳細表格
    st.subheader("📝 貢獻明細")
    st.dataframe(df.sort_values("貢獻%", ascending=False), use_container_width=True)

    # --- ⚖️ 法律免責聲明 ---
    st.markdown("---")
    with st.expander("⚖️ 免責聲明與風險告知"):
        st.write("""
        1. **非官方數據**：本預估值係基於公開數據模擬，並非官方最終淨值。
        2. **誤差風險**：計算受數據延遲、匯率波動及投信成本影響，僅供參考。
        3. **非投資建議**：本工具僅供參考，不構成買賣建議。投資人應獨立判斷並自負盈虧。
        4. **贊助性質**：Ko-fi 贊助屬自發支持行為，非購買投資建議之費用。
        """)

except Exception as e:
    st.error(f"數據解析中，請點擊刷新按鈕。(Error: {e})")

st.caption(f"最後更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 數據源：Yahoo Finance")
