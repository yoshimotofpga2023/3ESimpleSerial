import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path

st.set_page_config(page_title="Web Serial × Streamlit", layout="centered")
st.title("超音波センサー測定用シリアル通信ロガー")

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
    components.html(html, height=320, scrolling=True)

st.text("超音波測定用プログラム(Arduino IDE)")

st.code(
    '''
// HC-SR04 超音波距離センサー 測距→CSV行出力（ミリ秒, センチメートル）
const int PIN_TRIG = 9;
const int PIN_ECHO = 8;

void setup() {
  pinMode(PIN_TRIG, OUTPUT);
  pinMode(PIN_ECHO, INPUT);
  Serial.begin(115200);               // ←Octave側も同じボーレートに
  Serial.println("millis,distance_cm"); // ヘッダ（最初の1行）
  delay(100);
}

float measureDistanceCm() {
  // トリガパルス（10us）
  digitalWrite(PIN_TRIG, LOW);
  delayMicroseconds(2);
  digitalWrite(PIN_TRIG, HIGH);
  delayMicroseconds(10);
  digitalWrite(PIN_TRIG, LOW);

  // ECHOパルス幅を測定（タイムアウト 30ms ≒ 約5m）
  unsigned long duration = pulseIn(PIN_ECHO, HIGH, 30000UL);

  if (duration == 0) {
    // タイムアウト時は負値で通知（Octave側で無視可）
    return -1.0f;
  }

  // 音速 ≈ 343 m/s → 0.0343 cm/us、往復のため /2
  float distance_cm = (duration * 0.0343f) / 2.0f;
  return distance_cm;
}

void loop() {
  float d = measureDistanceCm();
  unsigned long t = millis();

  // CSV: millis,distance_cm
  Serial.print(t);
  Serial.print(",");
  Serial.println(d, 2); // 小数2桁

  delay(500); // 20Hzサンプリング（必要に応じて調整）
}
    '''
)



st.write("ブレッドボードへの実装例")
st.image("./tinker_USImg01.png")