# SO-101 — 最初のテレオペレーションまで

2026-09-13。最初の目標は、カメラなしでリーダーの動きにフォロワーを追従させること。

## 現在地

- 学習者の申告：SO-101 リーダー＋フォロワー2台セット。組立済みと思われるが現物未確認。
- 購入相談では Seeed / Cytron の Assembled Kit Pro を選んだ経緯。購入相談に記載された仕様を現物確認済みとは扱わない。
- 電源の OUTPUT、アーム側の識別ラベル、固定具、サーボIDの初期設定状態は未確認。
- PC は [環境メモ](environment.md) を参照。WSL 内の Python は 3.12.3、uv は利用可能。
- Windows の Get-Command と標準配置先で usbipd が見つからなかった。セッション内には ttyACM / ttyUSB デバイスなし。サンドボックス内の結果だけでホストの接続状態までは断定しない。
- この教材用の LeRobot 環境は未構築。通電・校正・モーター設定・動作指令は未実施。

## 順序

1. 現物と電源の対応を確認し、アームを固定する。電源は購入相談だけで判断せず、付属説明・現物ラベルに照合する。
2. Windows に usbipd-win を準備し、アームを一本ずつ識別して WSL へ接続する。
3. LeRobot と Feetech SDK を教材専用の環境に導入し、バージョンと検証結果を記録する。
4. 既存のモーターID設定を確認する。組立済みアームで setup-motors を無条件に実行しない。この処理は各モーターの不揮発設定を変更する。
5. 公式手順でリーダー・フォロワーを校正する。校正はコマンド入力だけでなく、指定姿勢や可動範囲を手で動かす工程を含む。
6. ポートと校正IDを固定して、周囲を空けた状態で小さな動きからテレオペレーションを確認する。

## WSL USB 接続の準備用コマンド（未実行）

Windows PowerShell でインストールする。対話形式で再起動の要否を確認する。

```powershell
winget install --interactive --exact dorssel.usbipd-win
usbipd list
```

その後、現物と照合した BUSID を使い、管理者 PowerShell で `usbipd bind --busid <BUSID>`、通常の PowerShell で `usbipd attach --wsl --busid <BUSID>` を実行する。BUSID は実測してから指定する。WSL 側でデバイスとシリアルポート、アクセス権を確認する。

## 参照した公式資料

- [Microsoft：WSL の USB 接続](https://learn.microsoft.com/en-us/windows/wsl/connect-usb)
- [LeRobot：インストール](https://huggingface.co/docs/lerobot/installation)
- [LeRobot：SO-101](https://huggingface.co/docs/lerobot/so101)
- [LeRobot：実機の模倣学習・テレオペレーション](https://huggingface.co/docs/lerobot/il_robots)

実際の導入時は選んだ LeRobot バージョンに対応する手順を使う。
