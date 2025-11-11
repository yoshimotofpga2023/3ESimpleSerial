import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path

st.set_page_config(page_title="3EUSMeasureApp", layout="centered")
st.title("超音波センサー測定用シリアル通信ロガー")

st.info(
    "使い方: Chrome/Edge（デスクトップ）で開き、**Connect** を押してポートを選択 → 入力欄から送信。"
    "Connectが成功したら、Startボタンで通信開始．測定が終わったらStopボタンを押す．"
    "Web Serial は `https://` または `http://localhost` でのみ有効です。\n\n"
    "アプリの仕様はこちら 👉 [アプリ仕様](https://github.com/yoshimotofpga2023/3ESimpleSerial/tree/main)"  
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
    components.html(html, height=320, scrolling=True)

st.text("超音波測定用プログラム(Arduino IDE)")

st.code(
    '''
      // Trig/Echo ピンは環境に合わせて変更
      const int PIN_TRIG = 9;
      const int PIN_ECHO = 10;

      void setup() {
        Serial.begin(115200);
        pinMode(PIN_TRIG, OUTPUT);
        pinMode(PIN_ECHO, INPUT);
      }

      float readDistanceCmOnce() {
        digitalWrite(PIN_TRIG, LOW);
        delayMicroseconds(2);
        digitalWrite(PIN_TRIG, HIGH);
        delayMicroseconds(10);
        digitalWrite(PIN_TRIG, LOW);
        long duration = pulseIn(PIN_ECHO, HIGH, 30000UL); // タイムアウト30ms
        if (duration == 0) return -1.0; // 取得失敗
        float cm = duration * 0.0343 / 2.0;
        return cm;
      }

      void loop() {
        if (Serial.available()) {
          String cmd = Serial.readStringUntil('\\n');
          cmd.trim();
          if (cmd.equalsIgnoreCase("D")) {
            float d = readDistanceCmOnce();
            if (d < 0) Serial.println("NaN");  // JS側は数値のみ拾うのでNaNは無視されます
            else Serial.println(d, 1);         // 例: 123.4
          }
        }
      }

    '''
)



st.write("ブレッドボードへの実装例")
st.image("./tinker_USImg01.png")