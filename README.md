# popro_control

複数台のGoProをUSB接続して撮影した動画を、PC側でまとめて収集・整理するためのツールです。

このツールの主目的は **動画ファイルの収集** です。複数カメラへの接続維持、同時録画の開始・停止、カメラ状態の管理は、このリポジトリ単体ではなく、市販ツールの [Camera Tools for GoPro Heros](https://www.toolsforgopro.com/cameratools) を使用する前提です。

## 使用者向け概要

### このツールでできること

- USB接続された複数GoProをPC側から検出する。
- 各GoPro内のMP4一覧を読み取る。
- 同時撮影された動画を1つの撮影グループとして一覧表示する。
- 選択した撮影グループを各GoProから並列ダウンロードする。
- take名を付けて、`cam01_take名.mp4` のような連番ファイル名で整理する。
- 必要に応じて、追加保存先にも同じtakeフォルダをコピーする。

### Camera Tools for GoPro Heros との役割分担

popro_control は収集ツールです。録画や接続維持の主処理は Camera Tools for GoPro Heros 側で行います。

Camera Tools for GoPro Heros は、カメラが起動状態を維持するための定期的な信号も送っています。そのため、popro_control を使う間は Camera Tools for GoPro Heros も同時に起動している必要があります。

Camera Tools for GoPro Heros が行うこと:

- 複数GoProへの接続維持
- USB/Bluetooth/Wi-Fi経由のカメラ制御
- 複数カメラへの同時録画開始・停止
- Camera Tools Command Server によるHTTP JSONコマンド受付

popro_control が行うこと:

- 接続済みGoProの検出
- メディア一覧の取得
- 同時撮影されたMP4の推定
- MP4のダウンロード
- take名でのリネーム・整理
- 追加保存先へのコピー

公式ページでは、Camera Tools for GoPro Heros はPCをGoProリモートとして使えるアプリで、複数カメラの録画開始・停止、設定変更、HTTPコマンドサーバー、USBによる複数カメラ制御に対応すると説明されています。

### 同時撮影された動画の見つけ方

各カメラの動画ファイル名、厳密な撮影開始時間、厳密な撮影時間は一致しません。そのため、このツールはファイル名の一致ではなく、以下の近さで同時撮影された動画を推定します。

- 撮影開始時間が一定の閾値内にある
- 動画の長さが一定の閾値内にある
- 接続中の全GoPro台数ぶんのMP4がそろっている

ツール起動時と `Relaod Files` ボタン押下時には、全GoProの時計合わせ処理が実行されます。これにより、各カメラの撮影開始時間が大きくずれないようにしてから、撮影開始時間と動画長を使って同じ撮影タイミングの動画を探します。

現在の実装では、撮影開始時間の差は5秒以内、動画長の差は3秒以内で判定します。

### 前提

- Windows PC
- Python 3.9以降
- USB接続された複数台のGoPro
- Camera Tools for GoPro Heros
- Camera Tools Command Server が起動していること
- popro_control の使用中、Camera Tools for GoPro Heros も同時に起動し続けていること

この実装は、USB接続されたGoProがPC上で `172.2x.xxx.5x` 系のIPv4アドレスとして見えることを前提にしています。検出時はPC側インターフェースの末尾を `1` に置き換え、GoPro本体のHTTP APIを `http://<ip>:8080` として扱います。

### インストール

```bat
pip install git+https://github.com/tomosud/popro_control.git#egg=popro_control
```

ローカル環境では、リポジトリ直下の `requirements.txt` にある依存関係をインストールしてください。

```bat
pip install -r requirements.txt
```

主な依存関係は `dearpygui`, `requests`, `aiohttp`, `aiofiles`, `psutil`, `tzdata`, `pynput` です。

### 起動

リポジトリ直下で以下を実行します。

```bat
run.bat
```

または直接起動します。

```bat
python popro_control\popro_start.py
```

起動すると Dear PyGui ベースの `GoPro File explorer` ウィンドウが開きます。

### 基本的な使い方

1. Camera Tools for GoPro Heros を起動する。
2. Camera Tools 側で複数GoProを接続し、撮影制御できる状態にする。
3. Camera Tools Command Server を起動し、URLを `Commend_server` に設定する。
4. GoProをUSBでPCに接続する。
5. `run.bat` で popro_control を起動する。
6. 必要に応じて `Additional SavePath` を設定する。
7. `Relaod Files` を押して各GoProのメディア一覧を再取得する。
8. 一覧に表示された撮影グループのtake名を確認・編集する。
9. 撮影グループのボタンを押すと、該当takeのMP4が全カメラから収集される。

カメラ名ボタンを押すと、そのGoProに対してビープ系コマンドを送ります。撮影グループ行の小さい番号ボタンを押すと、対応するGoPro上のMP4 URLをブラウザで開きます。

### 保存仕様

ローカルの一時保存先は `C:/GoPro/` です。

GoProから直接ダウンロードされた元ファイルは以下の形式で保存されます。

```text
C:/GoPro/<YYYY_MM_DD>/<YYYY_MM_DD_HH_MM_SS>/<GoPro名>_<元ファイル名>
```

その後、同じ日付フォルダ配下にtake名のフォルダが作成され、カメラ順の連番ファイル名でコピーされます。

```text
C:/GoPro/<YYYY_MM_DD>/<take名>/cam01_<take名>.mp4
C:/GoPro/<YYYY_MM_DD>/<take名>/cam02_<take名>.mp4
...
```

take名の初期値は撮影時刻から自動生成されます。

```text
take_<HH>-<MM>_<SS>
```

例:

```text
take_12-27_08
```

`add_filepath` が設定されている場合、takeフォルダは追加保存先にもコピーされます。

```text
<add_filepath>/<YYYY_MM_DD>/<take名>/
```

### UIの色

- 撮影グループボタンが暗色: 必要なファイルがローカルに存在する
- 撮影グループボタンが茶色: まだ未収集のファイルがある
- GoProボタンが黄色系: そのカメラからコピー中
- GoProボタンが赤茶系: 追加保存先へコピー中

### 削除操作

take名入力欄に `delete` と入力して撮影グループボタンを押すと、そのグループに含まれるGoPro上のMP4を削除する処理が実行されます。

これはカメラ内メディアを直接削除する操作です。通常の収集作業では使用しないでください。

## 技術者向け詳細

### 主要ファイル

- `popro_control/popro_start.py`: エントリーポイント。`popro_ui.main()` を呼び出す。
- `popro_control/popro_ui.py`: Dear PyGui のUI、撮影グループ表示、コピー操作、設定保存。
- `popro_control/popro_command.py`: GoPro本体HTTP APIへのアクセス、メディア一覧取得、時刻合わせ、ローカルコピー。
- `popro_control/popro_camera_server_control.py`: Camera Tools Command Server へのHTTP JSONコマンド送信。
- `popro_control/popro_para_http.py`: `aiohttp` / `aiofiles` によるMP4の並列ダウンロード。
- `popro_control/popro_remote.py`: メディアキーによる録画開始・停止の補助コード。現状の主用途は動画収集。

### 起動時の処理

`popro_ui.main()` の主な流れ:

1. `cm.ret_gopros()` でGoProを検出する。
2. `psc.connect_all_cameras(try_to_connect=True)` でCamera Tools側のカメラ接続を確認・接続要求する。
3. Dear PyGui の画面を作る。
4. `add_button_gopros()` で検出したGoProボタンを表示する。
5. `add_button_files()` で各GoProのMP4一覧を取得し、同時撮影グループを表示する。
6. `cm.get_time()` で全GoProの時計をPCの日本時間に合わせる。

`Relaod Files` 押下時は `reload_file()` が実行され、表示中の撮影グループを削除して `add_button_files()` を再実行した後、`cm.get_time()` で再度時計合わせを行います。

### GoPro検出ロジック

`cm.ret_gopros()` は `psutil.net_if_addrs()` でPCのIPv4アドレスを調べ、デフォルトでは以下の正規表現に合うアドレスを探します。

```text
172\.2\d\.1\d{2}\.5\d
```

見つかったPC側IPアドレスの末尾1文字を `1` に置き換え、GoPro側IPとして扱います。

例:

```text
PC側IP:    172.24.106.54
GoPro側IP: 172.24.106.51
Base URL:  http://172.24.106.51:8080
```

各GoProには以下を問い合わせます。

```text
GET http://<gopro-ip>:8080/gopro/camera/info
```

取得した `ap_ssid` をGoPro名、`ap_mac_addr` を補助情報として保持します。

内部データ形式:

```json
{
  "http://172.24.106.51:8080": {
    "url": "http://172.24.106.51:8080",
    "name": "HERO12 Black01",
    "checkurl": "http://172.24.106.51:8080/gp/gpMediaList",
    "ap_mac_addr": "06574710694f"
  }
}
```

この辞書は `popro_ui.gopro_dict` と `popro_command.gopro_dict` として使われます。

### Camera Tools Command Server

設定された `Commend_server` に対して、JSONをPOSTします。

カメラ一覧取得:

```json
{
  "command": "getAllCameras"
}
```

録画開始・停止などのカメラコマンド:

```json
{
  "command": "sendCameraCommand",
  "cameras": ["HERO12 Black01 (172.24.106.51)"],
  "cameraCommand": "startRecording"
}
```

ステータス取得:

```json
{
  "command": "cameraStatus",
  "cameras": ["HERO12 Black01 (172.24.106.51)"]
}
```

Command Server のURLは `C:/GoPro/Rename_Setting.ini` の `Commend_server` に保存されます。UI上の表記も実装上のキー名も `Commend_server` です。

### 時計合わせ

`cm.get_time()` はPCの `Asia/Tokyo` 現在時刻を使い、各GoProに以下のHTTP APIを送ります。

```text
GET http://<gopro-ip>:8080/gopro/camera/set_date_time?date=<YYYY_MM_DD>&time=<HH_MM_SS>&tzone=540&dst=0
```

その後、確認用に以下を取得します。

```text
GET http://<gopro-ip>:8080/gopro/camera/get_date_time
```

この時計合わせは、同時撮影判定の精度を上げるための前処理です。ただし、実際の判定では厳密一致ではなく、開始時刻と動画長に閾値を設けています。

### メディア一覧取得

各GoProに以下を問い合わせます。

```text
GET http://<gopro-ip>:8080/gp/gpMediaList
```

GoProのレスポンス例:

```json
{
  "id": "298554459323482383",
  "media": [
    {
      "d": "100GOPRO",
      "fs": [
        {
          "n": "GX010001.MP4",
          "cre": "1710861484",
          "mod": "1710861484",
          "glrv": "710050",
          "ls": "-1",
          "s": "12665667"
        }
      ]
    }
  ]
}
```

`ret_all_media()` は `.MP4` を含むファイルだけを対象にします。各MP4について動画メタデータも取得します。

```text
GET http://<gopro-ip>:8080/gp/gpMediaMetadata?p=<dir>/<filename>&t=videoinfo
```

処理後の内部データ例:

```json
{
  "1710829084": {
    "n": "GX010001.MP4",
    "cre": "1710861484",
    "mod": "1710861484",
    "s": "12665667",
    "localtime": "2024-03-19 15:18:04",
    "dir": "100GOPRO",
    "dur": "9",
    "w": "3840",
    "h": "2160",
    "fps": "30000",
    "fps_denom": "1001",
    "dl": "http://172.24.106.51:8080/videos/DCIM/100GOPRO/GX010001.MP4"
  }
}
```

このデータはファイルとして保存されず、メモリ上で撮影グループ判定に使われます。辞書キーは `cre` そのものではなく、実装上は `int(cre) - 32400` のtimestampです。一方、同時撮影判定の時刻比較には各要素内の生の `cre` を使います。

### 同時撮影グループ判定

`add_button_files()` で以下のように判定します。

- `cre_compi = 5`
- `dur_compi = 3`
- 検出済みGoPro台数を `lengopro` とする
- URLソート後の先頭GoProを基準カメラとして使う
- 基準カメラの各MP4に対して、他カメラの候補MP4を探す
- `abs(base_cre - now_cre) <= 5` を満たす候補のうち、撮影開始時刻差が最小のものを採用候補にする
- その候補について `abs(base_dur - candidate_dur) <= 3` を満たせば同じ撮影とみなす
- 全GoPro台数ぶんそろった場合だけUIに表示する

擬似コード:

```text
for base_video in first_camera_videos:
    group = [base_video]

    for camera in other_cameras:
        candidates = videos where abs(base_video.cre - video.cre) <= 5
        nearest = candidate with smallest cre difference

        if abs(base_video.dur - nearest.dur) <= 3:
            group.append(nearest)

    if len(group) == detected_gopro_count:
        show_as_same_take(group)
```

このため、以下は一致している必要がありません。

- GoPro上のファイル名
- 完全に同一の撮影開始秒
- 完全に同一の動画長

逆に、カメラの時計が大きくずれていたり、録画開始に大きな遅延がある場合は、同じ撮影でもグループ化されない可能性があります。

### UI用の撮影グループデータ

同時撮影グループは `popro_ui.temp_files_dict` に保持されます。

キーは基準カメラの `localtime`、値は各GoProのMP4情報リストです。

```json
{
  "2024-03-19 15:18:04": [
    {
      "n": "GX010001.MP4",
      "cre": "1710861484",
      "dur": "9",
      "dir": "100GOPRO",
      "dl": "http://172.24.106.51:8080/videos/DCIM/100GOPRO/GX010001.MP4"
    },
    {
      "n": "GX010001.MP4",
      "cre": "1710861486",
      "dur": "10",
      "dir": "100GOPRO",
      "dl": "http://172.26.186.51:8080/videos/DCIM/100GOPRO/GX010001.MP4",
      "gopro": "http://172.26.186.51:8080"
    }
  ]
}
```

このデータもファイルには保存されません。UI表示、プレビューURL、コピー対象URLの生成に使われます。

### 中間データとファイル

実際にファイルとして残るもの:

- `C:/GoPro/Rename_Setting.ini`: 設定とtake名を保存するJSON。
- `C:/GoPro/<YYYY_MM_DD>/<YYYY_MM_DD_HH_MM_SS>/...`: GoProから直接ダウンロードした元MP4。
- `C:/GoPro/<YYYY_MM_DD>/<take名>/...`: take名で整理したMP4。
- `<add_filepath>/<YYYY_MM_DD>/<take名>/...`: 追加保存先が設定されている場合のコピー。

ファイルとしては残らず、メモリ上だけで使うもの:

- `gopro_dict`: 検出したGoProのURL、名前、確認用URL、MACアドレス。
- `ret_all_media()` の戻り値: 各GoProのMP4一覧とメタデータ。
- `temp_files_dict`: UIに表示する同時撮影グループ。
- `url_dict`: 並列ダウンロードへ渡すURLと保存ファイル名の対応表。
- `temp_popro_ui_dict`: Dear PyGuiの部品IDと内部データの対応表。

リポジトリ直下の `tool_setting.ini` もJSON形式ですが、現在のUI本体の設定保存先は `C:/GoPro/Rename_Setting.ini` です。

### ダウンロード用データ

撮影グループボタンを押すと、各MP4の `dl` URLから保存先を作ります。

`ret_dlpath_from_dict()` の戻り値:

```json
{
  "url": "http://172.24.106.51:8080/videos/DCIM/100GOPRO/GX010001.MP4",
  "file_name": "HERO12 Black01_GX010001.MP4",
  "folder_path": "C:/GoPro/2024_03_20/2024_03_20_00_18_04"
}
```

`popro_para_http.download_main_wrapper()` に渡される `url_dict`:

```json
{
  "http://172.24.106.51:8080/videos/DCIM/100GOPRO/GX010001.MP4": "HERO12 Black01_GX010001.MP4",
  "http://172.26.186.51:8080/videos/DCIM/100GOPRO/GX010001.MP4": "HERO12 Black02_GX010001.MP4"
}
```

この辞書もファイル保存されず、並列ダウンロード処理の入力としてだけ使われます。

### ローカルファイル構成

一時保存:

```text
C:/GoPro/<YYYY_MM_DD>/<YYYY_MM_DD_HH_MM_SS>/<GoPro名>_<元ファイル名>
```

take名フォルダ:

```text
C:/GoPro/<YYYY_MM_DD>/<take名>/cam01_<take名>.mp4
C:/GoPro/<YYYY_MM_DD>/<take名>/cam02_<take名>.mp4
```

追加保存先:

```text
<add_filepath>/<YYYY_MM_DD>/<take名>/cam01_<take名>.mp4
<add_filepath>/<YYYY_MM_DD>/<take名>/cam02_<take名>.mp4
```

`cam01`, `cam02` の順番は、take名フォルダへコピーする時点で一時保存フォルダ内のMP4をソートした順番です。

### 永続化される設定JSON

設定は `C:/GoPro/Rename_Setting.ini` にJSONとして保存されます。拡張子は `.ini` ですが、中身はJSONです。

形式:

```json
{
  "add_filepath": "//server/share/Move_ai",
  "Commend_server": "http://10.102.106.60:810",
  "2024_03_20_00_18_04": "take_00-18_04"
}
```

キーの意味:

- `add_filepath`: 追加保存先。空文字の場合は追加コピーしない。
- `Commend_server`: Camera Tools Command Server のURL。
- `YYYY_MM_DD_HH_MM_SS`: 撮影グループのtake名。UIのtake名入力欄を編集すると保存される。

`button_file_color_update()` では、現在表示されている撮影グループに対応しない古いtake名キーを整理し、`add_filepath` と `Commend_server` は残します。

リポジトリ直下の `tool_setting.ini` はサンプルまたは旧設定用のJSONですが、現在のUI本体は `C:/GoPro/Rename_Setting.ini` を使用します。

### カメラ上ファイルの削除

take名入力欄が `delete` の場合、コピーではなく削除処理に分岐します。

削除URL:

```text
GET http://<gopro-ip>:8080/gopro/media/delete/file?path=<dir>/<filename>
```

例:

```text
GET http://172.24.106.51:8080/gopro/media/delete/file?path=100GOPRO/GX010001.MP4
```

これはGoPro内のメディアを削除するため、通常の収集作業では使用しないでください。

### 注意点

- 2台以上のGoProが検出されない場合、撮影グループは表示されません。
- MP4以外のメディアは収集対象外です。
- GoProの時計が大きくずれていると、同時撮影グループとして判定されない可能性があります。
- 録画開始タイミングや録画停止タイミングが大きくずれた場合も、閾値外になれば表示されません。
- `C:/GoPro/` と `C:/GoPro/Rename_Setting.ini` を使用します。
- 追加保存先はWindows UNCパスとして存在確認できる必要があります。
- Camera Tools Command Server のURLが未設定または起動していない場合、接続確認やカメラ制御系の処理は失敗します。
- Camera Tools for GoPro Heros が終了していると、カメラを起動状態に保つ定期信号が止まるため、popro_control 側の検出やメディア取得が不安定になる可能性があります。
