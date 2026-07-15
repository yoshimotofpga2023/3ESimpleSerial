import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path

st.set_page_config(page_title="Web Serial × Streamlit", layout="centered")
st.title("Web Serial API で Arduino と通信（距離の定期計測）")

st.info(
    "Chrome/Edge（デスクトップ）で開き、`https://` または `http://localhost` でアクセスしてください。"
    "Connect → Start で1秒間隔の距離計測を開始、Stopで停止、Startを再度押すとリセットして再開します。"
)

HTML_PATH = Path(__file__).with_name("webserial.html")

@st.cache_data(show_spinner=False)
def load_html_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")

if not HTML_PATH.exists():
    st.error(f"外部HTMLが見つかりません: {HTML_PATH.name}")
else:
    html = load_html_text(HTML_PATH)
    components.html(html, height=560, scrolling=True)

st.write("### Arduinoプログラム(超音波センサー専用)"
         " "
         "Arduino IDEを起動して以下のプログラムをコピペ。Arduinoに書き込むこと。"
         "Arduinoとブレッドボードの接続におけるピン配置は、プログラムやArduinoにて適宜調整すること。"
         )

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


st.write("ブレッドボードへの実装例①")
st.image("./tinker_USImg01.png")
st.image("./USMeasure01.png")

st.write("### ボタン(GPIO ポート2)押下で超音波測定")

st.code(
    '''
// ===== Ultrasonic + Mode (STREAM / BUTTON) =====
// Trig/Echo ピン
const int PIN_TRIG = 9;
const int PIN_ECHO = 10;

// ボタン（GNDへ落とす、内部プルアップ）
const int PIN_BTN  = 2;

// モード
enum Mode { MODE_STREAM = 0, MODE_BUTTON = 1 };
Mode mode = MODE_STREAM;

// チャタリング対策
const unsigned long DEBOUNCE_MS = 30;
bool lastStableBtn = HIGH;       // INPUT_PULLUPなので未押下=HIGH
bool lastReading   = HIGH;
unsigned long lastChangeMs = 0;

// 押しっぱなし対策（押した瞬間1回だけ）
bool pressLatched = false;

// 送信間隔（連続送信抑制）
const unsigned long MIN_SEND_INTERVAL_MS = 50;
unsigned long lastSendMs = 0;

float readDistanceCmOnce() {
  digitalWrite(PIN_TRIG, LOW);
  delayMicroseconds(2);
  digitalWrite(PIN_TRIG, HIGH);
  delayMicroseconds(10);
  digitalWrite(PIN_TRIG, LOW);

  long duration = pulseIn(PIN_ECHO, HIGH, 30000UL); // 30ms timeout
  if (duration == 0) return -1.0;
  float cm = duration * 0.0343f / 2.0f;
  return cm;
}

void sendDistanceOnce() {
  unsigned long now = millis();
  if (now - lastSendMs < MIN_SEND_INTERVAL_MS) return;
  lastSendMs = now;

  float d = readDistanceCmOnce();
  if (d < 0) Serial.println("NaN");
  else Serial.println(d, 1);
}

void setMode(Mode m) {
  mode = m;
  // 状態リセット
  pressLatched = false;

  // モード通知（数値でないのでロガーには入らない想定）
  Serial.print("[MODE] ");
  Serial.println(mode == MODE_STREAM ? "STREAM" : "BUTTON");
}

// 受信コマンド（改行区切り）
void handleSerialCommands() {
  if (!Serial.available()) return;

  String cmd = Serial.readStringUntil('\n');
  cmd.trim();
  cmd.toUpperCase();

  // ---- モード切替コマンド ----
  if (cmd == "MODE STREAM" || cmd == "STREAM" || cmd == "M0") {
    setMode(MODE_STREAM);
    return;
  }
  if (cmd == "MODE BUTTON" || cmd == "BUTTON" || cmd == "M1") {
    setMode(MODE_BUTTON);
    return;
  }

  // ---- 距離要求コマンド ----
  if (cmd == "D") {
    // ★重要：BUTTONモードでは D に反応しない（ボタン押下だけ送信）
    if (mode == MODE_STREAM) {
      sendDistanceOnce();
    } else {
      // 何もしない（必要ならログを出すが、数値じゃないのでロガーには入らない）
      // Serial.println("[IGNORED] D in BUTTON");
    }
    return;
  }

  // それ以外は無視（必要ならログ）
  // Serial.print("[UNKNOWN] "); Serial.println(cmd);
}

// ボタンのデバウンス＋押下イベント生成（立下り）
bool buttonPressedEvent() {
  bool reading = digitalRead(PIN_BTN);

  if (reading != lastReading) {
    lastChangeMs = millis();
    lastReading = reading;
  }

  if (millis() - lastChangeMs > DEBOUNCE_MS) {
    if (reading != lastStableBtn) {
      lastStableBtn = reading;

      // HIGH->LOW が「押した」イベント
      if (lastStableBtn == LOW) return true;
    }
  }
  return false;
}

void setup() {
  Serial.begin(115200);
  pinMode(PIN_TRIG, OUTPUT);
  pinMode(PIN_ECHO, INPUT);
  pinMode(PIN_BTN, INPUT_PULLUP);

  setMode(MODE_STREAM);
}

void loop() {
  handleSerialCommands();

  // BUTTONモードのときだけ、物理ボタン押下で送信
  if (mode == MODE_BUTTON) {
    if (buttonPressedEvent()) {
      if (!pressLatched) {
        pressLatched = true;
        sendDistanceOnce();
      }
    } else {
      // 離したら次の押下を許可
      if (lastStableBtn == HIGH) pressLatched = false;
    }
  }
}
    '''
)

st.write("ブレッドボードへの実装例②")
st.image("./tinker_USImg02.png")
st.image("./USMeasure02.png")

st.write("### ボタン(GPIO ポート2)押下で可変抵抗器の電圧（抵抗）測定")

st.code(
    '''
// ===== A0 Voltage + Button Send =====

const int PIN_ANALOG = A0;

// ボタン（GNDへ落とす、内部プルアップ）
const int PIN_BTN = 2;

// ADC基準電圧
const float VREF = 5.0;

// チャタリング対策
const unsigned long DEBOUNCE_MS = 30;
bool lastStableBtn = HIGH;
bool lastReading   = HIGH;
unsigned long lastChangeMs = 0;

// 押しっぱなし対策
bool pressLatched = false;

// 送信間隔
const unsigned long MIN_SEND_INTERVAL_MS = 50;
unsigned long lastSendMs = 0;

float readVoltageOnce() {
  int adc = analogRead(PIN_ANALOG);
  float voltage = adc * VREF / 1023.0;
  return voltage;
}

void sendVoltageOnce() {
  unsigned long now = millis();
  if (now - lastSendMs < MIN_SEND_INTERVAL_MS) return;
  lastSendMs = now;

  float v = readVoltageOnce();

  // 電圧値のみ送信
  Serial.println(v, 3);
}

// ボタンのデバウンス＋押下イベント生成
bool buttonPressedEvent() {
  bool reading = digitalRead(PIN_BTN);

  if (reading != lastReading) {
    lastChangeMs = millis();
    lastReading = reading;
  }

  if (millis() - lastChangeMs > DEBOUNCE_MS) {
    if (reading != lastStableBtn) {
      lastStableBtn = reading;

      // HIGH → LOW が押下イベント
      if (lastStableBtn == LOW) return true;
    }
  }

  return false;
}

void setup() {
  Serial.begin(115200);

  pinMode(PIN_ANALOG, INPUT);
  pinMode(PIN_BTN, INPUT_PULLUP);
}

void loop() {
  if (buttonPressedEvent()) {
    if (!pressLatched) {
      pressLatched = true;
      sendVoltageOnce();
    }
  } else {
    // ボタンを離したら次の押下を許可
    if (lastStableBtn == HIGH) {
      pressLatched = false;
    }
  }
}
    '''
)

st.write("ブレッドボードへの実装例")
st.image("./tinker_potentionMeterFig01.png")
st.image("./04_chap04p123_01.png")


st.write("### 自動で26点のcds光センサーの抵抗値測定")

st.code(
    '''
const int ledPin = 9;
const int cdsPin = A0;
const int buttonPin = 2;

const float fixedResistor = 10000.0;

const float gammaValue = 0.6;
const float r10Typ = 30000.0;

// チャタリング対策
const unsigned long DEBOUNCE_MS = 30;
bool lastStableBtn = HIGH;
bool lastReading = HIGH;
unsigned long lastChangeMs = 0;

bool pressLatched = false;

// PWM値
int pwmValue = 0;

float estimateLux(float resistance, float r10) {
  if (resistance <= 0.0) return -1.0;
  return 10.0 * pow(r10 / resistance, 1.0 / gammaValue);
}

bool buttonPressedEvent() {
  bool reading = digitalRead(buttonPin);

  if (reading != lastReading) {
    lastChangeMs = millis();
    lastReading = reading;
  }

  if (millis() - lastChangeMs > DEBOUNCE_MS) {
    if (reading != lastStableBtn) {
      lastStableBtn = reading;

      if (lastStableBtn == LOW) {
        return true;
      }
    }
  }

  return false;
}

float readLuxOnce() {
  analogWrite(ledPin, pwmValue);
  delay(1000);
  int sensorValue = analogRead(cdsPin);
  float voltage = sensorValue * (5.0 / 1023.0);

  float cdsResistance = -1.0;

  if (voltage > 0.01 && voltage < 4.99) {
    cdsResistance = fixedResistor * (5.0 - voltage) / voltage; 
  // 回路: 5V - CdS - A0 - 10kΩ - GND
//    cdsResistance = fixedResistor * voltage / (5.0 - voltage); 
  // 回路: 5V - 10kΩ - A0 - CdS - GND
  }
  if (cdsResistance <= 0.0) {
    return -1.0;
  }
  return estimateLux(cdsResistance, r10Typ);
}

void sendLuxOnce() {
  float lux = readLuxOnce();

  if (lux > 0.0) {
    Serial.println(lux, 2);
  } else {
    Serial.println("NaN");
  }
}

void setup() {
  pinMode(ledPin, OUTPUT);
  pinMode(cdsPin, INPUT);
  pinMode(buttonPin, INPUT_PULLUP);

  Serial.begin(115200);

  analogWrite(ledPin, pwmValue);
}

void loop() {
  if (buttonPressedEvent()) {
    if (!pressLatched) {
      pressLatched = true;

      sendLuxOnce();

      pwmValue += 10;

      if (pwmValue > 255) {
        pwmValue = 0;
      }
    }
  } else {
    if (lastStableBtn == HIGH) {
      pressLatched = false;
    }
  }
}
    '''
)

st.write("ブレッドボードでの実体配線図（すでに組み立て済み）")
st.image("./tinker_cdsMeasureFig01.png")
st.image("./cdsMeasureFigure01.png")