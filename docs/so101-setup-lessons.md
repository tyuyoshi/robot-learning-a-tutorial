# SO-101 セットアップの対話・つまずき・再開手順

2026-09-13。実機操作とユーザー報告に基づく記録。教材PDFの翻訳ではなく、実習の補足。ユーザーはデータサイエンティスト歴8年。一般的なMLの基礎問題は省略し、ロボット固有の概念を丁寧に説明する。コマンドは省略せず、実行するOS・シェルを明記する。

## 1. 何をセットアップしたか

SO-101 Assembled Kit Proの黒いリーダー（人が操作）と白いフォロワー（物をつかむ）、付属USBカメラ。色の対応は今回のキットの確認結果であり、すべてのSO-101に一般化しない。

- 黒：5V・3A、ZH-DY024D-0503000、センタープラス。
- 白：12V・2A、QL024-12020007（型番末尾は読み取り不確実）、センタープラス。
- Seeed公式表の白用12V・2Aと一致。黒用は公式表5V・4Aに対し付属品3Aという差がある。電源は色や購入相談だけで判断せず、現物とキット仕様を照合。
- 両腕を机へクランプ固定。台座の固定部分と机を挟み、モーター・配線・基板を挟まない。向かい合わせに配置したので互いの動作範囲が重ならないよう確認。
- 組立済みでも校正と固定は必要。既存IDで通信できたため、モーターIDを再設定するsetup-motorsは実行しなかった。
- PC：Windows 11 Home＋WSL2 Ubuntu 24.04.3、i7-12700K、RTX 3090 Ti 24GB。WSLメモリ約39GiB、Windows物理メモリ約79.7GiB。GPU認識と小さなCUDA演算を確認。学習時間や全モデルの実行可否は未検証。
- Python 3.12、LeRobot 0.6.1、Feetech SDK 1.0.0、PyTorch 2.11.0+cu130。WSLはenvironments/so101/.venvに隔離し、uv.lockで依存関係を固定。

## 2. WindowsのUSBをWSLへ渡す

Q：WindowsでCOMポートが見えれば、WSLでも使える？
A：USB/IPによる接続が必要。bindは共有設定、attachはWSLへの接続。Sharedは共有設定済み、AttachedはWSLに接続中。USB再接続でBUSIDが変わることがある。

Windowsの管理者PowerShell（初回）：
```powershell
winget install --interactive --exact dorssel.usbipd-win
usbipd list
usbipd bind --busid 2-5
usbipd bind --busid 2-6
usbipd attach --wsl --busid 2-5
usbipd attach --wsl --busid 2-6
```

wingetのソース更新警告は出たが、usbipd-win 5.3.0のインストールは成功。黒のUSBを一本だけ抜くと2-5が消えたため識別できた。

- 黒：2-5／COM4 → /dev/ttyACM0 → /dev/serial/by-id/usb-1a86_USB_Single_Serial_5B90103226-if00
- 白：2-6／COM3 → /dev/ttyACM1 → /dev/serial/by-id/usb-1a86_USB_Single_Serial_5B90101147-if00
- アームは番号が変わりやすいttyACMよりby-idを使う。

WSLのUbuntuでシリアルアクセス権を付ける：
```sh
sudo usermod -aG dialout "$USER"
newgrp dialout
```
newgrpは子シェルを開く。まとめて貼った後続コマンドが実行されないことがあるため、プロンプトが戻ってから別にidを実行する。通常シェルはfishだが、newgrp後は別シェルになり得る。
```sh
id
ls -l /dev/serial/by-id/
```
dialoutが含まれることを確認。既に起動済みの別ターミナルやエージェントには反映されない場合がある。chmod 666で回避しない。

## 3. uv環境と実行場所

Ubuntuで、リポジトリのルートから実行：
```sh
cd ~/robot-learning-a-tutorial
uv sync --project environments/so101 --frozen --python /usr/bin/python3
uv run --project environments/so101 --frozen lerobot-calibrate --help
```
--projectは使う環境、--frozenはロックファイルを更新せず使う指定。activateしなくてもuv runが専用仮想環境を使う。Windowsのカメラ送信にはWindowsネイティブのuvを別に使う。

## 4. 校正は「手で動かして基準と範囲を記録する」

Q：コマンドを実行すればアームが自動で校正される？
A：手動操作が必要。開始時に保持力が解除されるので腕を支える。

黒の校正（Ubuntu）：
```sh
uv run --project environments/so101 --frozen lerobot-calibrate \
  --teleop.type=so101_leader \
  --teleop.port=/dev/serial/by-id/usb-1a86_USB_Single_Serial_5B90103226-if00 \
  --teleop.id=so101_leader_black \
  --teleop.calibration_dir=local/so101/calibration/leader
```

白の校正（Ubuntu）：
```sh
uv run --project environments/so101 --frozen lerobot-calibrate \
  --robot.type=so101_follower \
  --robot.port=/dev/serial/by-id/usb-1a86_USB_Single_Serial_5B90101147-if00 \
  --robot.id=so101_follower_white \
  --robot.calibration_dir=local/so101/calibration/follower
```

手順：
1. 保存済みファイルがある場合、Enterで再利用、c＋Enterで再校正。毎回再校正する必要はない。
2. Move ... to the middle ...で、関節を無理なく動ける範囲の中間へ置く。この段階は範囲の記録前。
3. Enterを1回押す。その瞬間の位置をセンサー値2047付近に合わせ、範囲記録が始まる。
4. 根元の左右旋回shoulder_pan、肩の上下shoulder_lift、肘elbow_flex、手首の曲げ伸ばしwrist_flex、開閉gripperをゆっくり両端まで動かす。wrist_roll（ひねり）はこの範囲記録の対象外だが、初期姿勢・両腕の対応には関係する。
5. 5関節を動かし終えてからEnterで保存。機械的な止まりやケーブルの張りを力で越えない。

つまずきと訂正：
- 動かさず終了するとMIN=MAXでValueError。次の試行では開閉レバーが未操作でgripperだけ同じエラーになった。
- 黒のgripperは持ち手の開閉レバー。手首の曲げ伸ばしとは別。
- 複数関節を組み合わせて動かしても個別に記録される。一つずつ動かすのは確認漏れを防ぐため。
- 再校正は前回の範囲を引き継がず、5関節すべてを記録し直す。
- 0〜4095近くまで広がる値を見て「またいだ疑い」を指摘した。「またぐ」は4095→0のような値の不連続を意味し、再実行や複数関節の組み合わせではない。最終MIN/MAXだけでは不連続を断定できない。
- 狭い値幅だけで再校正を求めた案内は不適切だった。実際に動ける範囲が狭いことと、その一部しか記録していないことを区別する。後者は基準角度や開閉の対応に影響し得る。値幅の大小だけを合否基準にしない。
- Calibration savedはファイル保存の成功を意味し、全姿勢での追従精度や安全性を保証しない。

最終保存のMIN〜MAX（センサーのカウント値。度やradianではない）：
- 黒：pan 955〜3181、lift 1382〜3540、elbow 1097〜3071、wrist_flex 1578〜3294、gripper 2046〜3217。
- 白：pan 748〜3444、lift 1406〜3784、elbow 1018〜3089、wrist_flex 1893〜3690、gripper 1637〜3089。
- 保存先：local/so101/calibration/leader/so101_leader_black.json と local/so101/calibration/follower/so101_follower_white.json。Git対象外。後の操作も同じid・calibration_dirを指定する。

## 5. 黒を操作して白でつかむ：1→3→5の意味

Q：白が止まった。故障？
A：15秒でdisconnectしたケースはteleop_time_s=15の予定終了だった。WARNINGが続くことと切断は別。終了はCtrl+Cでも可能。通常の終了時は保持力が解除されるため、物を机に戻し、落下・接触しない低い姿勢で終える。

Q：max_relative_targetの1・3・5とは？
A：白の「現在の実測位置」から「今回送る目標位置」までの差の上限。速度・トルク・ゲイン・可動域そのものではない。

```text
今回の送信目標 = 白の現在位置 + clip(黒の指示 - 白の現在位置, -L, +L)
```

現在のuse_degrees=Trueでは、肩・肘など5つの回転関節は度。グリッパーは0〜100の開閉率なので、同じL=5でも5パーセントポイント。全関節が5度という説明は正確ではない。

例：白30度、黒60度なら、L=1で31度、L=3で33度、L=5で35度を送る。次の周期は「前回の目標」ではなく「その時の実測位置」から再計算する。白が30度で止まっていれば、目標も31度／33度／35度のままで、時間経過だけで60度へ積み上がらない。

位置制御では目標と実測の誤差が駆動出力に関係する。差を小さく制限しすぎると、重力・摩擦に対して動かす出力が十分出ず、静止したずれが残る場合がある。現在の設定はP=16、I=0、D=32。今回これらのゲインは変更していない。トルク不足などの直接測定はしておらず、改善結果からの推定。

10Hzは約0.1秒ごとの制御更新。L=5×10Hzを厳密な50度/秒の速度制限と解釈しない。衝突防止、絶対角度制限、把持力制限にもならない。

観察の流れ：
- L=1：開閉は進むが肩・肘はほぼ動かなかった。ログのoriginal goal_posは黒の要求、safe goal_posは制限後の目標。
- L=3：肩・肘が動き、ユーザーが物を持ち上げたと報告。
- 「逆に動く気がする」から確認を進めると、同じ方向へ動くが黒ほど肘が上がらないという現象だった。向かい合わせの左右の見え方、複数関節での手先の移動、各関節の角度を区別する。
- 黒をその姿勢で3〜5秒保持しても差が残ったため、単なる遅れと区別。
- L=5：15秒の比較で改善したと報告。制限がずれに寄与していたと考えられる。完全な角度一致や全姿勢での精度は未検証。さらに大きくすれば必ずよいわけではない。

現在の短時間の確認コマンド（Ubuntu、カメラ入力・記録なし）：
```sh
uv run --project environments/so101 --frozen lerobot-teleoperate \
  --teleop.type=so101_leader \
  --teleop.port=/dev/serial/by-id/usb-1a86_USB_Single_Serial_5B90103226-if00 \
  --teleop.id=so101_leader_black \
  --teleop.calibration_dir=local/so101/calibration/leader \
  --robot.type=so101_follower \
  --robot.port=/dev/serial/by-id/usb-1a86_USB_Single_Serial_5B90101147-if00 \
  --robot.id=so101_follower_white \
  --robot.calibration_dir=local/so101/calibration/follower \
  --robot.max_relative_target=5 \
  --fps=10 \
  --teleop_time_s=15
```
teleopは人の操作入力、robotは実機の動作側。max_relative_targetは全関節に共通の目標差上限、fpsは制御周期の目標、teleop_time_sは実行時間。過去に60秒でも試したが、現在の5の改善確認は15秒。開始前は両腕を近い関節姿勢にそろえ、白の周囲を空ける。通電追従中に白を手で押して補助しない。

初回課題：黒で開く→黒の肩・肘で白を物へ近づける→閉じる→1〜2cm持ち上げる→机へ戻す→離す。白を目で見て操作する。まだ方策学習や自律動作ではない。

## 6. カメラが見えない：認識と権限

カメラは当初2-4、差し替え後2-3。まずWSLのUSBカメラとして試した（現在はこの方式を採用しない）。

Windows PowerShellで実施した診断用接続：
```powershell
usbipd bind --busid 2-4
usbipd attach --wsl --busid 2-4
```

Ubuntu：
```sh
ls -l /dev/video*
sudo usermod -aG video "$USER"
newgrp video
```
プロンプトが戻ったらidを別途実行し、videoとdialoutを確認。/dev/video0、/dev/video1があっても、アクセス権がなければOpenCVで開けない。video追加後、/dev/video0（V4L2）の1台を検出。2つのデバイスファイルが2台のカメラを意味するわけではない。

```sh
uv run --project environments/so101 --frozen lerobot-find-cameras opencv --output-dir local/so101/camera-check --record-time-s 2
```
検出と約2秒の画像取得を行う。GUI表示ではない。同じPNGへ繰り返し上書きするのでログの保存回数ぶんファイルが増えるわけではない。Found 0、imread警告は権限修正で解消した。

## 7. 保存できても画像が正常とは限らない

- YUYV 640×480・30fps：保存成功だが大部分が緑色。
- MJPG 640×480・30fps：上部は写るが下部が黒く欠け、写る割合も変わった。撮り直しても再発。
- Windowsカメラアプリ：全体が正常に映ると報告。
- detach後に同じポートがVMware USB Device（0e0f:0001）になった。VMwareに取り込まれた可能性を考え、カメラUSBの抜き差し後にUSB HD Camera（1e45:8022）へ復帰。VMwareが画像欠損の原因だったとは未確認。
- WSLへ戻すと欠損が再発。カメラのポートを2-4→2-3に替えても改善なし。
- MJPG 320×240・30fps：select() timeoutで1枚目が取得できない。
- Pythonを使わないv4l2直接取得でも(error)の付いたバッファになり、出力ファイル0バイト。Python固有の問題ではなく、WSL側ドライバー／USB転送経路を優先すべきと判断。usbipdの特定バグや帯域不足が確定したわけではない。
- カーネルログにはvhci_get_frame_number、Not yet implementedなどの警告。警告だけで原因を断定しなかった。
- 対応モード：MJPGは1280×720、848×480、800×600、160×120、352×288、320×240、640×360、640×480がいずれも30fps。YUYVは1280×720が10/5fps、848×480と800×600が15/10/5fps、それ以外は30fps。要求したfpsが実際に適用されるとは限らない。

診断で使ったコマンド（Ubuntu）：
```sh
sudo apt update
sudo apt install -y v4l-utils
v4l2-ctl --device=/dev/video0 --list-formats-ext
uv run --project environments/so101 --frozen python environments/so101/check_camera.py --width 640 --height 480
uv run --project environments/so101 --frozen python environments/so101/check_camera.py --width 320 --height 240
timeout 20s v4l2-ctl --device=/dev/video0 --set-fmt-video=width=320,height=240,pixelformat=MJPG --set-parm=30 --stream-mmap=4 --stream-count=3 --stream-to=local/so101/camera-check/direct-320x240.mjpg --verbose
```
v4l-utilsはOSの診断ツール。Python依存はuv環境のまま。apt updateのGitHub CLI署名エラー（EXPKEYSIG／NO_PUBKEY）は別件で、v4l-utils導入は成功。署名問題自体は未修正。timeoutの終了コード124は時間切れを意味するが、当該実行の終了コードは会話で確認できていない。

貼り付けでもつまずいた：fishへbashのhere-documentを案内してしまい、その後の複数行python -cも字下げ・末尾崩れでIndentationError。これは撮影開始前のエラー。check_camera.pyを保存して1行で実行する方式に変更した。

## 8. 解決策：Windowsで撮影し、ZMQでWSLへ

WindowsのカメラをUSB/IPで渡さず、Windowsで取得した画像をJPEG→Base64→JSONとしてZMQで送る。WSLのLeRobot標準ZMQCameraが受け取り画像へ戻す。カメラ名wrist、ポート5555。WindowsにはLeRobot本体を入れず、Windowsネイティブuvがスクリプト内PEP 723の依存（OpenCV・pyzmq）を隔離環境に導入。WSLにもpyzmqを専用環境へ追加済み。

Windows PowerShell（Ubuntu端末ではない）：
```powershell
usbipd list
usbipd detach --busid 2-3
```
detachはカメラがAttachedのときだけ。現在のカメラのBUSIDを確認する。両アームはAttachedのまま。Windowsのカメラアプリを閉じる。

Windowsにuvがなければ：
```powershell
winget install --exact --id astral-sh.uv
```
導入後PowerShellを開き直す。

Windowsで映像送信：
```powershell
uv run --script "\\wsl.localhost\Ubuntu\home\tyuyoshi\robot-learning-a-tutorial\environments\so101\windows_camera_server.py" --bind 172.24.144.1
```
Publishing ... fpsが出たら動かしたままにする。終了はCtrl+C。間違ってUbuntuのuvで実行するとlinux-x86_64のPythonがUNCパスを開けずエラーになる。Windows PowerShellで実行し直して解消した。カメラを複数接続した場合、別のカメラなら送信スクリプトの--indexで選ぶ。

Ubuntuで画像保存：
```sh
uv run --project environments/so101 --frozen python environments/so101/check_network_camera.py --host 172.24.144.1
```
local/so101/camera-check/windows-zmq-10.png、20.png、30.pngを保存。3枚とも正常な640×480画像を目視確認し、黒い欠損は解消。送信側のbindと受信側のhostは同じWindows側IP。この値は当日のWSL NAT環境のもの。再起動などで変わったらUbuntuの次のコマンドでdefault viaの値を確認する。
```sh
ip -4 route show default
```
Windows用とUbuntu用の端末を明示して使い分ける。画像保存コマンド自体はアームを動かさない。

## 9. カメラはどちらに付け、何を見るか

Q：黒と白のどちらに付ける？
A：今回の手首カメラは白いフォロワーに付ける。黒は人が操作する側。対象物と実際につかむ爪の位置関係を見る。

固定カメラなら作業台全体、手首カメラなら爪付近と対象物を見る。手首カメラは腕と一緒に動くため、対象物が常に画面に入るとは限らない。1台で始められるが、全体視野が必要なら後で固定カメラを検討する。「カメラがないとすべての模倣学習が不可能」という購入相談の説明は一般論として不正確で、今回は視覚を使う課題のため必要。

取り付け：送信と追従を終了→白を安定した姿勢に支える→白の12V電源とカメラUSBを抜く→ブラケットに固定→関節や爪に挟まらず動ける配線の余裕を残す→USBをWindowsへ戻す。カメラだけの撮影には白の12Vは不要。現在の構成ではカメラをWSLへ再attachしない。

画角調整の経緯：
- 壁・扉だけの映像から、作業台と爪が見える向きへ調整。
- 箱が大きく写りすぎる状態では少し距離を取り、爪先と対象物の周囲が見えるようにした。
- 窓の逆光で白い爪・ティッシュが白飛び。カーテン等で直射光を避けて改善。完全な露出最適化は未実施。
- 横倒しの画像は手首姿勢でも変わるため、それだけで取り付けをやり直さない。
- 手首カメラの良否は任意の静止姿勢だけでなく、つかむ直前に両方の爪先と対象物が同時に見えるかで確認する。
- 最新画像では爪・対象物が見え、初動確認に進めると判断。全軌道で見失わないことは未検証。個人の室内写真はGitやNotionに転載せず、ローカルで確認した。

## 10. 現在の到達点と次の実習

できたこと：両腕のUSB接続・権限・uv環境・手動校正、黒による白の操作、小物の持ち上げ報告、Windows→WSLのカメラ画像取得、目標差制限1→3→5による追従改善。

まだ行っていないこと：LeRobotでカメラとアームをまとめたデータ収録、長時間の映像遅延/fps評価、観測と行動の時刻合わせ検証、方策学習、自律実行。カメラ送信を起動しただけでは、先のカメラ設定なしteleoperateコマンドに映像は組み込まれない。

次はカメラ入力を含む操作確認と短いエピソードの収録へ進む。教材は第1章のデータ部分（PDF p.5〜6付近）から実機へ寄り道中。データサイエンスの基礎を長く問わず、実機と結び付けて戻る。質問は3回に1回程度を本人回答、ほかは回答・ヒント付きという希望を優先する。

## 参照・再現用ファイル

- [セットアップ記録](https://github.com/tyuyoshi/robot-learning-a-tutorial/blob/main/docs/so101-setup.md)
- [Windows撮影サーバー](https://github.com/tyuyoshi/robot-learning-a-tutorial/blob/main/environments/so101/windows_camera_server.py)
- [LeRobotによる受信確認](https://github.com/tyuyoshi/robot-learning-a-tutorial/blob/main/environments/so101/check_network_camera.py)
- [USBカメラ診断スクリプト](https://github.com/tyuyoshi/robot-learning-a-tutorial/blob/main/environments/so101/check_camera.py)
- [Microsoft：WSL USB接続](https://learn.microsoft.com/en-us/windows/wsl/connect-usb)
- [LeRobot：SO-101](https://huggingface.co/docs/lerobot/so101)
- [Seeed：今回のキット](https://wiki.seeedstudio.com/lerobot_so100m_new/)
- 実装の判断はインストール済みLeRobot 0.6.1のso_follower.py、motors_bus.py、camera_zmq.pyに基づく。将来のバージョンで挙動が変わり得る。

