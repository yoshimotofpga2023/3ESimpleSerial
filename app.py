import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path

st.set_page_config(page_title="Web Serial × Streamlit", layout="centered")
st.title("Web Serial API で Arduino と通信（ブラウザ内）")

st.info(
    "使い方: Chrome/Edge（デスクトップ）で開き、**Connect** を押してポートを選択 → 入力欄から送信。"
    "Web Serial は `https://` または `http://localhost` でのみ有効です。"
)

# 読み込むHTMLファイルのパス
HTML_PATH = Path(__file__).with_name("webserial.html")

@st.cache_data(show_spinner=False)
def load_html_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")
if not HTML_PATH.exists():
    st.error(f"外部HTMLが見つかりません: {HTML_PATH.name}")
else:
    html = load_html_text(HTML_PATH)
    # 高さは必要に応じて調整
    components.html(html, height=520, scrolling=True)
