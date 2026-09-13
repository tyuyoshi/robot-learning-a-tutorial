# SO-101 — 最初のテレオペレーションまで

2026-09-13。最初の目標は、カメラなしでリーダーの動きにフォロワーを追従させること。

## 現在地

- 学習者の申告：SO-101 リーダー＋フォロワー2台セット。組立済みと思われるが現物未確認。
- 購入相談では Seeed / Cytron の Assembled Kit Pro を選んだ経緯。購入相談に記載された仕様を現物確認済みとは扱わない。
- 付属カメラありと申告。Seeed の公式商品写真では黒がリーダー、白がフォロワー。学習者は黒へ5V・3A、白へ12V・2Aの付属電源を接続し直したと報告。固定具とサーボIDの初期設定状態は未確認。
- PC は [環境メモ](environment.md) を参照。WSL 内の Python は 3.12.3、uv は利用可能。
- usbipd-win 5.3.0 を学習者が導入。両アームの bind / attach に成功し、Windows 側で Attached を確認した。
- サンドボックス外で WSL 側の2ポートを確認。学習者は `sudo usermod -aG dialout "$USER"` と `newgrp dialout` を実行し、現在のターミナルで `id` に dialout が含まれることを確認した。既存の別プロセスにグループ変更が反映されているとは限らない。
- 通電は学習者が実施。校正・モーター設定・動作指令は未実施。

## ポート対応（2026-09-13 確認）

黒の USB を抜いた際に Windows の 2-5 が消えたこと、および WSL の vhci 接続情報とシリアルリンクを照合した。

| アーム | Windows BUSID / COM | 今回の WSL ポート | WSL の固定識別パス |
| --- | --- | --- | --- |
| 黒・リーダー | 2-5 / COM4 | /dev/ttyACM0 | /dev/serial/by-id/usb-1a86_USB_Single_Serial_5B90103226-if00 |
| 白・フォロワー | 2-6 / COM3 | /dev/ttyACM1 | /dev/serial/by-id/usb-1a86_USB_Single_Serial_5B90101147-if00 |

USB の再接続で BUSID や ttyACM の番号が変わる場合がある。アーム操作には原則 by-id パスを使う。カメラは Windows の 2-4（USB HD Camera）として認識されているが、WSL への接続は未実施。

## 専用 Python 環境

`environments/so101/` に LeRobot 0.6.1 と Feetech SDK 用の依存定義・`uv.lock` を置く。`uv sync` で導入済み。仮想環境は同フォルダの `.venv/`（Git 対象外）で、システム Python には導入していない。

リポジトリのルートから、ロック済みの環境を再作成する：

```bash
uv sync --project environments/so101 --frozen --python /usr/bin/python3
source environments/so101/.venv/bin/activate
lerobot-calibrate --help
```

`--help` は使い方を表示するだけで、アームには接続しない。実際の校正では机への固定と周囲の作業空間を確認したうえで、リーダー・フォロワーを一本ずつ扱う。

環境を activate せずに実行する場合は、リポジトリルートで `uv run --project environments/so101 --frozen lerobot-calibrate --help` のように指定する。

### 導入後の確認結果

- Python 3.12.3 / LeRobot 0.6.1 / Feetech SDK 1.0.0 / PySerial 3.5。
- PyTorch 2.11.0+cu130 / torchvision 0.26.0。
- `lerobot-calibrate --help` と `lerobot-teleoperate --help` が終了コード0。SO-101 の leader / follower の選択肢を確認。
- GPU はサンドボックス外から確認。`torch.cuda.is_available()` は True、RTX 3090 Ti を認識し、GPU 上で `[1, 2, 3]` の二乗和が14になることを確認。
- この確認ではアームに接続していない。モーター通信、校正、テレオペレーション、カメラ動作はまだ未検証。

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
