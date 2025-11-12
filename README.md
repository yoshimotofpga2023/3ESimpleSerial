# 超音波センサー測定用シリアル通信ロガー
updated : 2025/11/13
## 使い方

- arduino（回路作成&プログラム書き込み済み）がPCと接続されていることを確認する．
- [connect]ボタンを押す．左上で、arudinoのポートを選ぶ

    ※ポートがわからなければ、arudino IDEで確認する．

- [Start]ボタンを押して測定を開始する．

    ※常にarduinoからシリアル通信でデータが送信されていることを想定するが、数値以外のデータを受信した場合は
    画面上に数字は表示されない．

- 距離データを十分に取得できたら[Stop]ボタンを押して計測をやめる

- データがおかしい、あるいは計測点が少ないなどもう一度計測する場合は、そのまま[Start]ボタンを再度押す．

    ※前回計測されたデータはリセットされる．

- 取得したデータ内容に問題がなければ、画面のデータをコピーし、PCのメモ帳等にコピペし、必要に応じて
データを加工して、CSV形式でファイルを保存する．（ファイル名の最後に.csvとすればOK）

- アプリを終了するときは念の為[disconnect]ボタンをおしてarduinoとPCの接続をオフにしておく．

## 仕様

### プログラム

- Web Serial APIをJavaScriptで呼び出し．
- [connect]ボタンで、指定されたボーレートでarduinoとシリアル通信を開始する．
    - 非同期処理(await)でarduinoと接続を試みる．接続に成功すればシリアル通信を始める．
    - データの取得は readLoop関数で定義している．
    ```
      async function readLoop() {
    const decoder = new TextDecoder();
    try {
      while (port && keepReading) {
        const r = port.readable.getReader();
        reader = r;
        try {
          while (true) {
            const { value, done } = await r.read();
            if (done) break;
            if (value) {
              const chunk = decoder.decode(value);
              ln(chunk.replace(/\r/g, "\\r").replace(/\n/g, "\\n\n"));
              rxBuffer += chunk;
              // 行ごとに処理
              let idx;
              while ((idx = rxBuffer.search(/\r?\n/)) >= 0) {
                const line = rxBuffer.slice(0, idx);
                rxBuffer = rxBuffer.slice(idx + (rxBuffer[idx] === '\r' && rxBuffer[idx+1] === '\n' ? 2 : 1));
                const trimmed = line.trim();
                if (trimmed.length === 0) continue;
                if (isNumericLine(trimmed)) {
                  addDistanceLine(trimmed);
                }
              }
            }
          }
        } catch (e) {
          // 読み取り中断時など
        } finally {
          r.releaseLock();
          if (!keepReading) break;
        }
      }
    } catch (e) {
      ln("[read error] " + e);
    }
  }
    ```
    関数のポイントは、改行文字ごとにシリアル通信のデータを読み取る処理をしている．
    たとえば、123.4\r\nときたら、123.4のみをlineという変数に格納する．
    データ整形が必要なので、最終的にtrimmedという変数にデータが入る．

    最終的に、addDistanceという関数で、データの取得時間と取得した距離データをrecords配列へpushする．画面には、距離のみ表示する．

    - 以下の正規表現で取得したデータから数値のみを取得する．

    ```
    /^[\s]*[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?[\s]*$/
    ```
    上記関数内、isNumericLine関数で処理している．

- [Start]ボタンで、arduinoからシリアル通信で送信されてくるデータを取得する．
    - 前回計測したデータがあればリセットされる．
    - 500ms間隔でarduinoに文字列"D"をシリアル通信で送信している．
        - この仕様に対応したarduinoのプログラムであれば、Dを受け取った場合のみシリアル通信で測定データを送信するというロジックを作成できる．


- [Stop]ボタンで、計測を終了する．まだ、arduinoとはシリアル通信を継続している．
    - Interval割り込みの停止と、その関数で保持されるtimerIDオブジェクトをメモリ領域から解放する．

- [Disconnect]ボタンでarduinoとのシリアル接続を切断する．

- （未検証のため利用非推奨）[DownloadCSV]ボタンでCSV形式で加工されたデータがダウンロードされる．

- その他
    - シリアル通信のデータ加工されていないものは「デバッグ用ログ」画面に表示されている．
    - css、javascriptはすべて、htmlファイルに記述されている．

### 環境
- Webブラウザ(chrome, edge)に依存するWeb Serial APIを利用．
- サーバーは無料のstreamlit cloudを使用．そのため、サーバー機能はPython(streamlitに依存する)
- サーバー機能（バックエンド）はstreamlit(python)、UI機能（フロントエンド、シリアル通信機能）はJavaScript(htmlとcss)と、UIの大枠はstreamlit(python)

