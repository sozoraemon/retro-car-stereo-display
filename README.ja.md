# Retro Car Stereo Display

Raspberry PiとPythonを使って、1990年代のカーオーディオの表示画面を再現するプロジェクトです。

当時のカーオーディオに特徴的な3Dスペクトラムアナライザーやドットマトリクス表示、レベルメーターなどを、PythonのPygameで再現しています。

モデルにしたのは、KENWOODのDPX-440、DPX-550、ALPINEのMDA-W779JBの3機種です。

[MHS35 SPI液晶（Raspberry Pi用3.5インチディスプレイ）](https://electronicwork.shop/items/6ac8ff42c5f8f197e65e1657)での表示を基本としていますが、[HyperPixel 4.0](https://shop.pimoroni.com/en-jp/products/hyperpixel-4?variant=12569485443155)でも動作します。

音声再生機能はありません。スペクトラムアナライザーは実際の音声信号とは連動せず、ランダムに動作します。懐かしいカーオーディオの表示演出を眺めて楽しむための作品です。

## 対応機種

### KENWOOD DPX-440

<img src="photos/dpx440.jpeg" alt="KENWOOD DPX-440 running on Raspberry Pi" width="400">

- 立体的な3Dスペクトラムアナライザー
- 左右対称の曲線状サイドメーター
- 2列ずつ上から下に流れる点灯アニメーション
- 機種名、メーカー名、現在時刻を切り替えるドットマトリクス表示

### KENWOOD DPX-550

<img src="photos/dpx550.jpeg" alt="KENWOOD DPX-550 running on Raspberry Pi" width="400">

- 奥行きのある3Dスペクトラムアナライザー
- 24バンドのレベル変化アニメーション
- 曜日と現在時刻を表示するドットマトリクス

### ALPINE MDA-W779JB

<img src="photos/w779jb.jpeg" alt="ALPINE MDA-W779JB running on Raspberry Pi" width="400">

- 扇状に広がる3Dスペクトラムアナライザー
- 青系の18段カラー表示とアクセントカラー
- 中央から上下に広がるレベル変化アニメーション
- 曜日と現在時刻を表示するドットマトリクス

## 動作環境

以下の環境を想定しています。

| 項目 | 内容 |
|---|---|
| コンピューター | Raspberry Pi 5 |
| OS | Raspberry Pi OS（Trixie） |
| プログラミング言語 | Python |
| 描画ライブラリ | Pygame |
| 描画解像度 | 800×480 |
| 液晶モジュール | MHS35 SPI液晶（480×320）、HyperPixel 4.0（800×480） |
| 画面表示方式 | Wayland DMA-BUFミラーリング（MHS35 SPI液晶の場合） |

本プロジェクトはMHS35 SPI液晶での表示を基本としていますが、HyperPixel 4.0でも動作します。

使用する液晶モジュールは、以下のページで確認できます。

- [MHS35 SPI液晶（Raspberry Pi用ディスプレイモジュール・3.5インチ）](https://electronicwork.shop/items/6ac8ff42c5f8f197e65e1657)
- [HyperPixel 4.0｜Pimoroni公式サイト](https://shop.pimoroni.com/en-jp/products/hyperpixel-4?variant=12569485443155)

## 事前準備

MHS35 SPI液晶を使用する場合は、以下のミラーリングプログラムを設定してください。

**[Raspberry Pi SPI LCD Mirror](https://github.com/sozoraemon/raspberry-pi-spi-lcd-mirror)**

このプログラムを使用すると、Raspberry Piのデスクトップ画面をMHS35 SPI液晶にミラーリングできます。

液晶モジュールの取り付け方法や詳しい設定手順については、[ブログ記事](https://sozorablog.com/raspberry-pi-3-5-inch-spi-lcd/)でも紹介しています。

### 画面解像度の変更

本プロジェクトでは800×480のデスクトップ解像度を使用します。

MHS35 SPI液晶のミラーリング環境を設定済みの場合は、既存の自動起動設定にある解像度指定を書き換えます。

ターミナルで以下のコマンドを実行してください。

```bash
mkdir -p ~/.config/labwc && touch ~/.config/labwc/autostart && sed -i '/wlr-randr --output NOOP-1 --custom-mode/d' ~/.config/labwc/autostart && echo '( sleep 3; wlr-randr --output NOOP-1 --custom-mode 800x480 ) &' >> ~/.config/labwc/autostart
```

設定後、Raspberry Piを再起動してください。

```bash
sudo reboot
```

再起動後、ミラーリング環境の仮想ディスプレイ解像度が800×480に設定されます。

## プログラムの実行

本リポジトリを取得します。

```bash
git clone https://github.com/sozoraemon/retro-car-stereo-display.git
cd retro-car-stereo-display
```

使用する機種のPythonファイルを実行してください。

**KENWOOD DPX-440**

```bash
python3 dpx440.py
```

**KENWOOD DPX-550**

```bash
python3 dpx550.py
```

**ALPINE MDA-W779JB**

```bash
python3 w779jb.py
```

実行すると、カーオーディオの表示アニメーションが始まります。終了する場合は、Escキーを押してください。

### SSHから実行する場合

SSH接続では、Waylandの描画先が自動設定されず、画面が表示されない場合があります。

その場合は、以下のように環境変数を指定して実行してください。

```bash
XDG_RUNTIME_DIR="/run/user/$(id -u)" \
WAYLAND_DISPLAY=wayland-0 \
SDL_VIDEODRIVER=wayland \
python3 dpx440.py
```

ほかの機種を使用する場合は、最後のPythonファイル名を変更してください。

このコマンドは、Waylandソケットが`wayland-0`の環境を想定しています。環境によって異なる場合は、実際のソケット名に変更してください。

終了する場合は、Escキーを押してください。SSHから実行している場合は、ターミナルでCtrl+Cを押して終了することもできます。

### ファイル構成

リポジトリは以下の構成になっています。

```text
retro-car-stereo-display/
├── README.md
├── dpx440.py
├── dpx440.png
├── dpx550.py
├── dpx550.png
├── w779jb.py
├── w779jb.png
└── photos/
    ├── dpx440.jpeg
    ├── dpx550.jpeg
    └── w779jb.jpeg
```

各Pythonファイルは、同じフォルダにある対応する背景画像を読み込みます。

## 表示アニメーションについて

### 3Dスペクトラムアナライザー

24バンドのスペクトラムアナライザーを描画します。

各バンドの高さをランダムに変化させ、音楽に合わせて動いているような演出を再現しています。

機種ごとに形状や配色、点灯パターンが異なります。

### 左右サイドメーター

DPX-440では、左右対称の曲線状メーターを表示します。

点灯位置を一定間隔で移動させ、光が流れるような動きを表現しています。

曲線は高解像度で描画してから縮小し、輪郭を滑らかにしています。

### ドットマトリクス

5×7ドットの文字を使用し、曜日や現在時刻などを表示します。

DPX-440では、メーカー名と機種名も順番に表示し、文字の切り替えアニメーションを加えています。

## 注意事項

- Raspberry Pi 5とMHS35 SPI液晶を想定していますが、Pygameが動作するほかの環境でも利用できる場合があります。
- 表示アニメーションは実際の音声信号とは連動していません。
- SPI液晶へのミラーリング速度は、Pythonプログラムの描画速度とは異なります。
- 掲載するメーカー名や商標は、それぞれの権利者に帰属します。
- 本プロジェクトは各カーオーディオメーカーの公式製品ではなく、各社による承認・提携を示すものではありません。
- 背景画像や製品デザインの権利については、公開・再利用の条件を別途確認してください。

## 関連プロジェクト

[Raspberry Pi SPI LCD Mirror](https://github.com/sozoraemon/raspberry-pi-spi-lcd-mirror)

Raspberry Pi 5のデスクトップをMHS35 SPI液晶にミラーリングするためのプログラムです。
