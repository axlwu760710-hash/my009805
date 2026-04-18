import streamlit as st
import streamlit.components.v1 as components
import os

st.set_page_config(page_title="009805 監控站", layout="wide")

# 定位 index.html
current_dir = os.path.dirname(os.path.abspath(__file__))
index_path = os.path.join(current_dir, "index.html")

if os.path.exists(index_path):
    with open(index_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    
    # 檢查是否已經被 Actions 填入數據 (檢查標籤是否還在)
    if "" in html_content:
        st.warning("⚠️ 數據正在初始化中，請稍候並點擊 GitHub Actions 手動執行 Run workflow")
    
    components.html(html_content, height=1200, scrolling=True)
else:
    st.error(f"❌ 找不到 index.html！請確認檔案已上傳至 Repository 根目錄。")
    st.info(f"目前目錄下的檔案有: {os.listdir(current_dir)}")
