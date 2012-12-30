# QR drone
## 目次
 * [これは何？](#これは何？)
 * [扱う情報](#扱う情報)
 * [ヘリコプターとの通信プロトコル](#ヘリコプターとの通信プロトコル)
 * [やること](#やること)
 * [インターフェース](#インターフェース)

## これは何？
mbedを使ったクアッドコプターを作ろうプロジェクト。  
クアッドコプターに載せたmbedがXBee経由でPCと通信する。

## 扱う情報
### ヘリコプターから
 * 加速度
 * 角速度
 * 高度
 * 位置座標
 * モーター電圧
 * 動作モード

### コントローラーから
 * 出力変更レバーの値
 * 方向レバーの値(前後pitch, 左右roll)

### 無線カメラから
 * カメラ映像

### 予め必要なデータ
 * 座標入りの地図


## ヘリコプターとの通信プロトコル
送信直前に、`+`を全て`+\x00`で置き換え、受信直後に`+\x00`を`+`に置き換えることで、  
通信途中で`++`(XBeeの設定モードに入る)が現れないようにする。

括弧内はバイト数

    < header (12)>
      (2)[magic number "\xff\x00"]
      (2)[type]
      (4)[length of body]
      (4)[crc-32 of body]
    < body >
	  [data]


type: CHANGE_MODE(0x10) (pc <-> helicopter)

    < body (1) >
	  (1)[mode to change]

type: OK_CHANGE_MODE(0x11) (pc <-> helicopter)

    < body (1) >
	  (1)[recieved mode to change]

type: REPORT_CONTEXT(0x20) (pc <- helicopter)

    < body (21) >
      (1)[current mode]
    　(4)[acceleration] //加速度
      (4)[angular velocity] //角速度
      (4)[height] //高度
      (4)[geographical position] //GPSの位置座標
      (4)[motor voltage] //モーター電圧

type: CHANGE_GEARSHIFT(0x30) (pc -> helicopter)

    < body (12) >
	  (4)[power change lever]
	  (4)[direction lever (pitch)]
	  (4)[direction lever (roll)]


## やること
 1. ヘリから各種データを受信
 2. 動作モード名の表示と背景色の決定
 3. 加速度角速度高度モーターの周波数は折れ線グラフで表示
 4. 加速度角速度から傾き計算→3Dモデルで表示
 5. 位置座標の変化から速度算出

## インターフェース
![UIイメージ](https://raw.github.com/Kph-Lab/QRdrone/master/UIsample.png)

わざとゆっくり描画する。以下の様な順に。
 1. 最初の背景はモードの色とは別の色
 2. 各ウィンドウの枠を最初に
 3. ログ出力を優先
 4. 常に文字が流れる感じ
 5. 次に各ウィンドウのタイトルとグラフの軸
 6. 広範囲な地図の読み込み
