# 学習環境

2026-09-12 に実機で確認。容量の空きは確認時点の値。

| 項目 | 確認結果 |
| --- | --- |
| ホスト OS | Windows 11 Home、ビルド 26200 |
| Linux 環境 | WSL2、Ubuntu 24.04.3 LTS、x86_64 |
| カーネル | 6.18.33.2-microsoft-standard-WSL2 |
| CPU | Intel Core i7-12700K、物理12コア・20スレッド（Windows 側で確認） |
| 物理メモリ | Windows 認識容量 約79.7GiB |
| WSL メモリ | 約39GiB、確認時の利用可能量 約26GiB |
| GPU | NVIDIA GeForce RTX 3090 Ti、VRAM 24564MiB |
| NVIDIA ドライバー | 591.86 |
| WSL ファイルシステム | 空き約789GiB。Windows 側の実空き容量は未確認 |

## 確認できたこと・未確認のこと

- WSL から `/usr/lib/wsl/lib/nvidia-smi` が成功。エージェントのサンドボックス内では GPU が遮断されるため、外側で確認した。
- `nvidia-smi` の CUDA 表示は 13.1。2026-09-13 に専用仮想環境の PyTorch 2.11.0+cu130 で RTX 3090 Ti の認識と小さな GPU 計算を確認した。
- 2026-09-13：`uv` で `environments/so101/.venv` に LeRobot 0.6.1 と Feetech SDK を導入。両アームの USB は WSL で認識済み。シミュレーター・モーター通信・カメラ動作は未確認。
- 2026-09-13：SO-101 リーダー＋フォロワーの2台セットを購入済み・未セットアップと確認。現物確認と作業の進捗は [実機準備](so101-setup.md) を参照。

## 再確認に使ったコマンド

WSL 側：`cat /etc/os-release`、`uname -r`、`lscpu`、`free -h`、`df -h .`、`/usr/lib/wsl/lib/nvidia-smi`。

Windows 側は PowerShell の `Get-CimInstance` で `Win32_OperatingSystem`、`Win32_ComputerSystem`、`Win32_Processor` の必要項目のみ確認した。ホスト名やシリアル番号を含む生ログは保存しない。
