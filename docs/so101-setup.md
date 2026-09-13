# SO-101 — 最初のテレオペレーションまで

2026-09-13。最初の目標は、カメラなしでリーダーの動きにフォロワーを追従させること。

## 現在地

- 学習者の申告：SO-101 リーダー＋フォロワー2台セット。組立済みと思われるが現物未確認。
- 購入相談では Seeed / Cytron の Assembled Kit Pro を選んだ経緯。購入相談に記載された仕様を現物確認済みとは扱わない。
- 付属カメラありと申告。Seeed の公式商品写真では黒がリーダー、白がフォロワー。学習者は黒へ5V・3A、白へ12V・2Aの付属電源を接続し直したと報告。その後クランプ固定と既存IDでの通信を確認した。
- PC は [環境メモ](environment.md) を参照。WSL 内の Python は 3.12.3、uv は利用可能。
- usbipd-win 5.3.0 を学習者が導入。両アームの bind / attach に成功し、Windows 側で Attached を確認した。
- サンドボックス外で WSL 側の2ポートを確認。学習者は `sudo usermod -aG dialout "$USER"` と `newgrp dialout` を実行し、現在のターミナルで `id` に dialout が含まれることを確認した。既存の別プロセスにグループ変更が反映されているとは限らない。
- 両腕をクランプで固定済みと学習者が報告。両腕の校正ファイルを保存し、テレオペレーションの初動を確認済み。モーターIDの再設定は実施していない。

## ポート対応（2026-09-13 確認）

黒の USB を抜いた際に Windows の 2-5 が消えたこと、および WSL の vhci 接続情報とシリアルリンクを照合した。

| アーム | Windows BUSID / COM | 今回の WSL ポート | WSL の固定識別パス |
| --- | --- | --- | --- |
| 黒・リーダー | 2-5 / COM4 | /dev/ttyACM0 | /dev/serial/by-id/usb-1a86_USB_Single_Serial_5B90103226-if00 |
| 白・フォロワー | 2-6 / COM3 | /dev/ttyACM1 | /dev/serial/by-id/usb-1a86_USB_Single_Serial_5B90101147-if00 |

USB の再接続で BUSID や ttyACM の番号が変わる場合がある。アーム操作には原則 by-id パスを使う。カメラは差し替え後 Windows の 2-3（USB HD Camera）。カメラは Windows で撮影し、下記の ZMQ 経由で WSL に渡す。

## 専用 Python 環境

`environments/so101/` に LeRobot 0.6.1 と Feetech SDK 用の依存定義・`uv.lock` を置く。`uv sync` で導入済み。仮想環境は同フォルダの `.venv/`（Git 対象外）で、システム Python には導入していない。

リポジトリのルートから、ロック済みの環境を再作成する：

```bash
uv sync --project environments/so101 --frozen --python /usr/bin/python3
uv run --project environments/so101 --frozen lerobot-calibrate --help
```

`--help` は使い方を表示するだけで、アームには接続しない。実際の校正では机への固定と周囲の作業空間を確認したうえで、リーダー・フォロワーを一本ずつ扱う。

環境を activate せずに実行する場合は、リポジトリルートで `uv run --project environments/so101 --frozen lerobot-calibrate --help` のように指定する。

### 導入後の確認結果

- Python 3.12.3 / LeRobot 0.6.1 / Feetech SDK 1.0.0 / PySerial 3.5。
- PyTorch 2.11.0+cu130 / torchvision 0.26.0。
- `lerobot-calibrate --help` と `lerobot-teleoperate --help` が終了コード0。SO-101 の leader / follower の選択肢を確認。
- GPU はサンドボックス外から確認。`torch.cuda.is_available()` は True、RTX 3090 Ti を認識し、GPU 上で `[1, 2, 3]` の二乗和が14になることを確認。
- 上記は導入時のソフトウェア確認。以後、学習者の実機操作で校正・追従・ネットワーク経由のカメラ画像保存を確認した。

## 実機確認とカメラの現在地

- ユーザーの通常シェルは fish。複数行の Python を貼り付けず、保存したスクリプトを1行のコマンドで実行する。
- 校正は `local/so101/calibration/leader/so101_leader_black.json` と `local/so101/calibration/follower/so101_follower_white.json` に保存。Git 対象外。
- `max_relative_target=1` では肩・肘が動かず、`3` に変更した短時間の試行で動いたと報告。10Hzで試験。これは現在位置からの目標差の制限で、速度制限や衝突防止ではない。全可動範囲の追従精度は未検証。
- USBカメラは WSL の `/dev/video0` として認識。ユーザーに `video` グループを追加しアクセス権を解決したが、YUYV/MJPG 640×480で画像欠損、MJPG 320×240でタイムアウト。v4l2直接取得でもエラーフレーム。ポート変更でも改善しなかった。Windowsのカメラアプリでは正常と報告。
- Windows撮影 → ZMQ → LeRobot 0.6.1 の `ZMQCamera` で受信し、640×480の3枚に欠損がないことを目視確認。連続運用時のfps・遅延、アームとの同時収録は未検証。画角は作業台へ調整が必要。

### 再開コマンド

Windows PowerShell でカメラを WSL から外す（Attached の場合のみ）。BUSIDは `usbipd list` で確認する。Windowsのカメラアプリは閉じる。

```powershell
usbipd detach --busid 2-3
uv run --script "\\wsl.localhost\Ubuntu\home\tyuyoshi\robot-learning-a-tutorial\environments\so101\windows_camera_server.py" --bind 172.24.144.1
```

Windowsネイティブのuvを使う。PEP 723の依存定義から独立環境を作り、WindowsにはLeRobot本体を導入しない。送信プロセスは起動したままにし、終了はCtrl+C。カメラ名は `wrist`、ポートは5555。送信先はこのPCのWSL向けインターフェースに限定する。IPはWSL再起動などで変わる場合があるため、WSLの `ip -4 route show default` で確認する。

Ubuntu（fish）、リポジトリのルートで受信を確認する：

```fish
uv run --project environments/so101 --frozen python environments/so101/check_network_camera.py --host 172.24.144.1
```

`local/so101/camera-check/windows-zmq-{10,20,30}.png` に保存。画像はGit対象外。今後のLeRobotカメラ設定は `type=zmq`、`server_address=172.24.144.1`、`camera_name=wrist` を使用する。

## 順序

1. 現物と電源の対応を確認し、アームを固定する。電源は購入相談だけで判断せず、付属説明・現物ラベルに照合する。
2. Windows に usbipd-win を準備し、アームを一本ずつ識別して WSL へ接続する。
3. LeRobot と Feetech SDK を教材専用の環境に導入し、バージョンと検証結果を記録する。
4. 既存のモーターID設定を確認する。組立済みアームで setup-motors を無条件に実行しない。この処理は各モーターの不揮発設定を変更する。
5. 公式手順でリーダー・フォロワーを校正する。校正はコマンド入力だけでなく、指定姿勢や可動範囲を手で動かす工程を含む。
6. ポートと校正IDを固定して、周囲を空けた状態で小さな動きからテレオペレーションを確認する。

## WSL USB 接続の記録

Windows PowerShell でインストールする。対話形式で再起動の要否を確認する。

```powershell
winget install --interactive --exact dorssel.usbipd-win
usbipd list
```

今回、管理者 PowerShell で `usbipd bind --busid 2-5` と `usbipd bind --busid 2-6`、続いて `usbipd attach --wsl --busid 2-5` と `usbipd attach --wsl --busid 2-6` を実行済み。再接続時は `usbipd list` で BUSID と状態を確認する。

## 参照した公式資料

- [Microsoft：WSL の USB 接続](https://learn.microsoft.com/en-us/windows/wsl/connect-usb)
- [LeRobot：インストール](https://huggingface.co/docs/lerobot/installation)
- [LeRobot：SO-101](https://huggingface.co/docs/lerobot/so101)
- [LeRobot：実機の模倣学習・テレオペレーション](https://huggingface.co/docs/lerobot/il_robots)
- [Seeed：キット固有の電源仕様](https://wiki.seeedstudio.com/lerobot_so100m_new/#specification)。Pro の Leader は5V、Follower は12V。Follower 用12V・2Aの記載あり。Leader 用は同表で5V・4Aとあり、付属品の5V・3Aとは差がある。
- [Seeed：商品写真](https://media-cdn.seeedstudio.com/media/catalog/product/1/-/1-100046482-so-arm-101-assembled-kit-pro.jpg)

実際の導入時は選んだ LeRobot バージョンに対応する手順を使う。
