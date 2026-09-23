# 操作・移動・移動操作：歴史、技術、論文、社会実装

調査日：2026-09-23。教材第2.2節からの補足調査。論文著者・研究機関・製造者・導入企業の公開資料を参照した。製品の網羅的ランキングではなく、技術と実装の関係を理解するための代表例。企業発表の実績は第三者による独立検証と区別する。教材の読書再開位置はp.12末尾のまま。

## 1. 三つの分野を一つの場面で理解する

「隣の部屋のコップを持ってきて」を分解すると分かりやすい。

| 分野 | 変えるもの | コップの例 | 主な難しさ |
| --- | --- | --- | --- |
| Manipulation／マニピュレーション（操作） | 対象物の位置・向き・状態 | コップをつかむ、持ち上げる、注ぐ | 接触、摩擦、滑り、変形、見えなくなる部分 |
| Locomotion／ロコモーション（移動） | ロボット自身の位置・姿勢 | 部屋まで車輪・脚で移動する | 車輪なら走行制約、脚なら接地とバランス |
| Mobile manipulation（移動操作） | 自分と対象物の両方 | コップへ近づき、つかみ、運ぶ | 台車・脚・腕・物体・作業順序の整合 |

移動には「身体をどう進めるか」と「どこへ、どういう経路で行くか」がある。厳密には後者はnavigation（航法）。実用の移動ロボットでは自己位置推定、経路計画、障害物回避まで一緒に必要になるため、本ノートでは併せて扱う。

これは形の分類ではない。四足でもアームを付ければ移動操作ができるし、人型でもその場で手だけを使えば操作の課題になる。移動操作は「移動して止まってつかむ」も含み、常に歩行と把持を同時実行する必要はない。人が商品を取り、台車が運ぶ協働ピッキングは、台車自身が把持するシステムとは分ける。

現在のSO-101は机への固定によって、自己位置推定と転倒防止の問題を外し、操作を学びやすくしている。それでも視覚、関節制御、接触、失敗後の復帰という主要課題が残る。

## 2. 歴史：何ができず、何が必要になったのか

### 1960〜1970年代：反復作業の機械化と、考えて動くロボット

工場では危険・重労働・繰り返し作業の自動化が出発点だった。対象物を治具で決まった場所へ置き、ロボットが教示した動作を繰り返せるようにする。日本では川崎重工が1969年に国産初の産業用ロボットを製造し、安川電機は1977年に全電動のMOTOMANを送り出した。[川崎の沿革](https://kawasakirobotics.com/jp/company/history/)、[安川の技術史](https://www.yaskawa.co.jp/technology/history)

並行して、SRIのShakey（1966〜1972年）は、周囲を認識して行動を計画する移動ロボットを研究した。「動作を再生する」だけでなく、「状況から何をするか決める」という系譜である。[SRIの歴史資料](https://www.sri.com/hoi/shakey-the-robot/)

### 1980〜2000年代：接触、バランス、地図を数学で扱う

部品を穴に入れる場合、正しい位置へ強引に押すだけでは引っ掛かる。Hoganのインピーダンス制御は、接触時の力と動きの関係を設計する考え方を整理した。柔らかいばね・ダンパーのように振る舞わせる、というイメージが役立つ。[Hogan, 1985](https://newmanlab.mit.edu/wp-content/uploads/2017/09/1985-impedance-control-an-approach-to-manipulation-part-I-theory.pdf)

脚の研究では、身体の重さを支えながら足を切り替えることが中心課題になった。Hondaは1986年に二足歩行研究を開始し、2000年にASIMOを発表した。梶田らの2003年の研究は、将来の足運びを見越して重心運動を作るZMPプレビュー制御の代表例である。[Hondaの歴史](https://global.honda/en/ASIMO/history/)、[Kajita et al., 2003](https://people.csail.mit.edu/katiebyl/kb/DW2008/papers_of_tangential_interest/kajita03.pdf)

移動では「地図がないと現在地が分からず、現在地が分からないと地図を作れない」という循環を、同時推定するSLAMが重要になった。腕の経路では、多関節の姿勢空間を探索するRRTなどが発展した。[SLAM解説論文, 2006](https://www-personal.acfr.usyd.edu.au/tbailey/publications/slamtutorial1.htm)、[LaValleのRRT資料](https://lavalle.pl/rrtpubs.html)

### 2010年代以降：観測と行動をデータから学ぶ

工場の整った部品配置に比べ、家庭や物流では物体の形・位置・照明・重なりが変わる。そこで、画像からの認識や行動選択を学習する方向が広がった。脚では、シミュレーター内で多数の試行を行い、学んだ方策を実機へ移すsim-to-realが有力になった。Hwangboらの2019年のANYmal研究はその代表例。[論文](https://arxiv.org/abs/1901.08652)

これは古典制御の廃止ではない。学習した方策が目標を出し、モデルに基づく制約やサーボ制御が実行する組み合わせがある。現在のSO-101でも、ACTの推論とモーターの位置制御は別の役割を持つ。

### 2020年代：長い作業、複数の身体、基盤モデルへ

ACTやDiffusion Policyは、一瞬の指令だけでなく行動系列を扱う。Mobile ALOHAは台車と両腕の実演を収集する。Open X-Embodimentは異なる機体の経験を共有し、π₀などは画像・言語・ロボットデータを基盤に多様な操作を学ぶ。研究の焦点が「一つの動作」から「多様な状況で一連の作業を完遂する」へ広がっている。出典は第6節の原論文・プロジェクトを参照。

## 3. Manipulation：物に触れると、問題が変わる

### 主な技術と役割

1. **認識・姿勢推定**：物体はどこにあり、どちらを向き、どこならつかめるか。画像の中心と把持に適した位置は一致しないことがある。
2. **逆運動学・経路計画**：その位置へ手を届かせる腕の形と、途中でぶつからない経路を求める。
3. **力・接触の制御**：押し過ぎを避け、滑らない力で保持する。位置制御、力制御、インピーダンス制御を課題に応じて使う。[MITの制御教材](https://manipulation.mit.edu/force.html)
4. **模倣学習・強化学習**：人の実演から学ぶ、あるいは報酬を用いて行動を改善する。ACTは今回の模倣学習側。
5. **成功判定と復帰**：爪を閉じた事実と、物を保持できた事実を区別する。失敗なら再観測・つかみ直しへ戻る。

コップをつかむときは、自由空間を動く状態から、爪が物に触れ、力をかけ、物と一体で動く状態へ移る。接触の有無で力学が変わり、画像だけでは摩擦や滑りが見えにくい。ここが単純な座標予測より難しい点である。

### 代表的な社会実装

- **Mujin × アスクル**：AVC関西のピースピッキング。倉庫の認識・動作計画・設備連携をまとめて実用化する例。汎用アームの研究と、物流業務として成立させる統合技術の違いが分かる。[導入事例](https://www.mujin.co.jp/videos/piece-picking-robot-for-e-commerce-logistics-center-of-askul/)
- **Amazon Vulcan**：2025年公表の接触・力覚を使う棚への収納／取り出し。画像で位置を決めるだけでなく、接触の情報を利用する実運用例。ネットワーク全体への拡大計画と、すでに稼働している拠点は区別する。[Amazon発表](https://www.aboutamazon.com/news/operations/amazon-vulcan-robot-pick-stow-touch)
- **Telexistence × ファミリーマート**：飲料補充TX SCARA。商品・棚・仕事を限定し、自動操作と必要時の遠隔支援を組み合わせる。2022年資料は導入開始と300店舗への拡大計画であり、この資料だけから300店舗への完了を断定しない。[導入企業の発表](https://www.family.co.jp/company/news_releases/2022/20220810_01.html)

実務上の強さは、未知の物体を一度つかむ能力だけでは決まらない。処理速度、品物の破損率、連続稼働時間、失敗時の人手、品種変更にかかる時間が重要になる。

## 4. Locomotion：車輪と脚では、難しさと価値が違う

### 車輪：移動効率と運用全体

平らな床では、車輪は身体を常に支えやすく、搬送の構成を簡単にできる。実用上は走行だけでなく、SLAM／自己位置推定、経路計画、人や台車の回避、充電、複数台の渋滞回避が必要になる。

AGVは事前に定めた経路を走る構成、AMRは周囲を見て自律的に経路を調整する構成として説明されることが多い。ただし製品の呼び方と実際の機能には幅があるので、名称だけで能力を判定しない。[オムロンのAMR説明](https://www.fa.omron.co.jp/product/robotics/lineup/mobile/feature/)

### 脚：どこを支点に、どう体重を支えるか

脚は階段や不整地へのアクセスに価値がある一方、接地場所、摩擦、身体の姿勢を同時に扱う。

- **状態推定**：IMU・関節センサー・カメラ等から、身体の傾き、速度、接地状態を推定する。
- **ZMP等のバランス指標**：支持面に対して転倒モーメントをどう扱うかを考える。重心の真下を足の中央へ置くだけで全ての動歩行を説明できるわけではない。
- **MPC（モデル予測制御）**：少し先までの運動を予測して操作を決め、観測が更新されるたびに解き直す。
- **強化学習・sim-to-real**：シミュレーターで多数の条件を経験させる。現実との差に備え、摩擦・質量・遅延などを変える学習や、実行中の適応が使われる。[Hwangbo et al.](https://arxiv.org/abs/1901.08652)、[RMA](https://arxiv.org/abs/2107.04034)

### 社会実装の見どころ

- **Amazon Robotics**：2025年6月にロボット累計配備100万台を公表。倉庫の搬送・仕分け等を含む全体の数字で、人型100万台ではない。個体の賢さに加え、フリート全体の連携が事業価値を生む。[Amazon発表](https://www.aboutamazon.com/news/operations/amazon-million-robots-ai-foundation-model)
- **オムロン**：工場向けLD／MD／HD等のAMRと運用システム。製造設備や人と混在する現場への統合が重要。[製品・導入事例](https://www.fa.omron.co.jp/product/robotics/lineup/mobile/)
- **ラピュタロボティクス**：PA-AMRで人の倉庫ピッキングを支援する。人が取り出し、ロボットが移動を担う構成を、ロボット自動把持と混同しない。[製品と導入事例](https://www.rapyuta-robotics.com/ja/solutions-pa-amr/)
- **Boston Dynamics Spot／ANYbotics ANYmal**：階段等のある産業設備の巡回・点検。SpotのHyundaiでの導入、ANYmalの化学設備等での活用が公表されている。巡回できてもバルブ操作までできるとは限らない。[Hyundaiとの発表](https://bostondynamics.com/news/boston-dynamics-hyundai-motor-group-expand-collaboration-drive-mobility-manufacturing-innovation/)、[ANYboticsの事例](https://www.anybotics.com/industries/robotic-inspection-for-chemicals/)

## 5. Mobile manipulation：二つを足すと、相互依存が生まれる

「コップまで移動する」と「コップをつかむ」を別々に解けば十分とは限らない。

- 近くまで来ても、机の脚が邪魔で腕を伸ばせない。
- 腕を伸ばすと重心が移り、台車や脚の安定性が変わる。
- 物を持つと通れる隙間や視界が変わる。
- 台車の停止誤差が、手先の把持位置の誤差になる。
- コップを倒したら、作業順序そのものを組み直す必要がある。

ここで、**全身制御（whole-body control）**は腕と移動部分をまとめて扱い、**TAMP（task and motion planning）**は「何をどの順にするか」と「物理的にどう動くか」を結び付ける。たとえば、先に障害物を移すか、別の場所から近づくかを、実行可能性と一緒に考える。[Garrett et al., 2021](https://arxiv.org/abs/2010.01083)

### 商用運用と実証を分けて見る

| 例 | 確認できる段階 | 技術的な意味と限界 |
| --- | --- | --- |
| Boston Dynamics Stretch × DHL | 北米で2023年から商用導入。2025年に追加1,000台超に向けたMOU | 移動可能な箱荷下ろし専用機。MOUの台数を導入済み台数に数えない。人型でなくても仕事は成立する |
| Agility Digit × GXO | 2024年から商用運用・複数年契約を発表 | 人用の環境で物流の限定作業を担う。契約と現場稼働は汎用家事能力の証明とは別 |
| Figure 02 × BMW | 2025年の実生産環境でのパイロット | 部品の取り扱いを実工程で評価。Figureは約3万台の車両生産への寄与を報告。ロボット単独で車を組み立てた意味ではない |
| Hexagon AEON × BMW Leipzig | 2026-09-21の記事でパイロットを報告 | 車輪で移動する人型に近い身体。二足歩行が唯一の実用解ではない |
| 川崎重工Nyokkey＋FORRO | 2025年8月の病院実証 | 搬送ロボットとアーム付き移動ロボットを連携し、検体を検査機器へ投入。病院全体の無人化達成とは別 |
| Toyota HSR／ELEY | 研究開発と派生技術の現場移転 | 2026年にELEYを紹介。HSRの航法等は別製品へ移転しているが、ELEY自体の広域商用稼働を意味しない |

出典：[DHL／Stretch](https://bostondynamics.com/news/dhl-signs-mou-for-additional-1000-robot-deployment/)、[Digit／GXO](https://www.agilityrobotics.com/content/digit-deployed-at-gxo-in-historic-humanoid-raas-agreement)、[Figureの実績報告](https://www.figure.ai/news/production-at-bmw)、[BMWのパイロット報告](https://www.bmwgroup.com/de/news/allgemein/2026/humanoide-roboter-in-leipzig.html)、[川崎の病院実証](https://www.khi.co.jp/pressrelease/news_250821-1.pdf)、[ToyotaのHSR／ELEY解説](https://global.toyota/jp/mobility/frontier-research/44105139.html)。

## 6. 代表論文：タイトルより「解こうとした問題」を覚える

以下は発明の全系譜ではなく、分野をつなぐ読みどころ。年は原則初公開年、TAMPは雑誌刊行年も併記する。

| 年・論文 | 分野 | 一言でいう貢献 | SO-101との接点 |
| --- | --- | --- | --- |
| 1985・Hogan, [Impedance Control](https://newmanlab.mit.edu/wp-content/uploads/2017/09/1985-impedance-control-an-approach-to-manipulation-part-I-theory.pdf) | 操作・接触 | 位置だけでなく接触時の力学的な応答を設計する | 物に触れた後の制御を考える。現設定へそのまま追加できるという意味ではない |
| 1998・LaValle, [RRT](https://msl.cs.illinois.edu/~lavalle/papers/Lav98c.pdf) | 操作・移動共通 | 高次元の姿勢空間で、サンプルを使って経路を探索 | IKで目標姿勢が分かっても途中の衝突回避が残る |
| 2003・Kajita et al., [ZMP Preview Control](https://people.csail.mit.edu/katiebyl/kb/DW2008/papers_of_tangential_interest/kajita03.pdf) | 二足移動 | 将来の支持位置を見越して歩行パターンを生成 | 固定アームでは免除されているバランス問題 |
| 2006・Durrant-Whyte & Bailey, [SLAM Part I](https://www-personal.acfr.usyd.edu.au/tbailey/publications/slamtutorial1.htm) | 移動 | 地図と自己位置の同時推定を体系化した解説 | 台車を追加すると「根元が世界のどこか」が変数になる |
| 2019・Hwangbo et al., [Learning Agile and Dynamic Motor Skills](https://arxiv.org/abs/1901.08652) | 脚移動 | シミュレーションで学んだ運動技能を実機ANYmalへ移す | 実演中心のACTとは異なる学習経路 |
| 2021・Kumar et al., [RMA](https://arxiv.org/abs/2107.04034) | 脚移動 | 最近の観測履歴から環境変化へ素早く適応 | 学習時と異なる摩擦・荷重への対応を考える |
| 2020公開／2021刊・Garrett et al., [Integrated Task and Motion Planning](https://arxiv.org/abs/2010.01083) | 移動操作 | 離散的な作業順序と連続的な運動計画を統合する問題を整理 | 「倒した→つかみ直す」までの作業構造 |
| 2022・Ahn et al., [SayCan](https://say-can.github.io/) | 移動操作・言語 | 言語として適切な手順と、ロボットが実行できる技能を結合 | 「やるべきこと」と「できること」は異なる |
| 2023・Zhao et al., [ACT／ALOHA](https://arxiv.org/abs/2304.13705) | 操作 | 低コストの実演収集、行動チャンク、時間的アンサンブル | 今回使用した方式。予測の時間的な整合を改善する |
| 2023・Chi et al., [Diffusion Policy](https://diffusion-policy.cs.columbia.edu/) | 操作 | 条件付き拡散モデルで行動系列の分布を表す | 左右から回り込む等、複数の選択肢を扱う発想。ただし復帰技能は自動で生えない |
| 2023・[Open X-Embodiment／RT-X](https://robotics-transformer-x.github.io/) | 複数機体 | 異なるロボットのデータを集め、経験の転移を検証 | ファイル形式の共通化と、関節・行動の互換性は別 |
| 2024・Fu, Zhao & Finn, [Mobile ALOHA](https://arxiv.org/abs/2401.02117) | 移動操作 | 台車と両腕を含む全身テレオペレーションと模倣学習 | 黒→白の実演を、移動＋両腕へ拡張したイメージ。研究デモ |
| 2024・Physical Intelligence, [π₀](https://www.physicalintelligence.company/blog/pi0) | 汎用操作 | 視覚言語の事前学習とflow matchingを用いる行動生成 | 1課題の実演だけから学ぶ方式から、多様な経験を土台にする方向へ |

ACTとDiffusion Policyは、単純な平均回帰では表しにくい行動系列を扱う異なる設計である。どちらも「少数の実演でどんな環境でも動く」保証はない。また、SLAM・RRT・インピーダンス制御はニューラルネットワークの登場で不要になった技術ではなく、別の問題を担当している。

## 7. 強いプレイヤーを「何に強いか」で見る

強さを、①機体・駆動、②知覚・制御ソフト、③データ・学習モデル、④現場統合・保守の四つに分ける。研究動画、資金調達、販売台数、現場の処理能力はそれぞれ違う指標であり、一列の順位にしない。

### 国内の代表

| プレイヤー | 主な位置 | 見るべき強み・証拠 |
| --- | --- | --- |
| FANUC | 操作・産業機体 | 製造・供給・保守の規模。2023年8月に産業用ロボット累計出荷100万台。年間台数でも現在稼働台数でもない。[公式発表](https://www.fanuc.co.jp/ja/profile/pr/newsrelease/2023/news20230915.html) |
| 安川電機 | 操作・駆動／制御 | MOTOMANとモーション制御の蓄積。溶接等の製造工程を考える入口。[技術史](https://www.yaskawa.co.jp/technology/history) |
| 川崎重工 | 操作＋移動操作 | 産業用アームの基盤と、Nyokkeyによるサービス領域の実証。両者の商用成熟度を分ける。[沿革](https://kawasakirobotics.com/jp/company/history/)、[実証](https://www.khi.co.jp/pressrelease/news_250821-1.pdf) |
| Mujin | 操作の知能化・現場統合 | 多様な物流設備とピッキングの統合。アスクルの稼働事例を参照。[事例](https://www.mujin.co.jp/videos/piece-picking-robot-for-e-commerce-logistics-center-of-askul/) |
| オムロン | 車輪移動・工場統合 | AMRの製品群と工場での運用連携。[製品・事例](https://www.fa.omron.co.jp/product/robotics/lineup/mobile/) |
| ラピュタロボティクス | 車輪移動・群管理 | 倉庫で人と協働する搬送・ピッキング支援。[製品・事例](https://www.rapyuta-robotics.com/ja/solutions-pa-amr/) |
| Telexistence | 用途特化の操作 | 飲料補充、自動化と遠隔支援の組み合わせ。[FamilyMart発表](https://www.family.co.jp/company/news_releases/2022/20220810_01.html) |
| Toyota | 移動操作・研究と現場移転 | HSRから航法・認識等を現場製品へ移す経路と、ELEYの接触研究。[2026年解説](https://global.toyota/jp/mobility/frontier-research/44105139.html) |

### 海外の代表

| プレイヤー | 主な位置 | 見るべき強み・段階 |
| --- | --- | --- |
| ABB Robotics | 産業用・協働操作 | アームとプログラミング／シミュレーションの製品体系。[GoFa](https://www.abb.com/global/en/areas/robotics/products/robots/collaborative-robots/gofa) |
| Amazon Robotics | 操作・搬送・大規模運用 | 実物流での運用とデータ収集を結び付けられる。[配備規模](https://www.aboutamazon.com/news/operations/amazon-million-robots-ai-foundation-model) |
| Boston Dynamics | 脚移動・物流操作 | Spotの点検、Stretchの荷下ろし。Atlasなど別製品の研究成果を同一の商用実績に合算しない。[導入段階の説明](https://bostondynamics.com/news/boston-dynamics-hyundai-motor-group-expand-collaboration-drive-mobility-manufacturing-innovation/) |
| ANYbotics | 脚移動・点検 | 工場の視覚・熱・音響情報を取得する点検システム。[産業事例](https://www.anybotics.com/industries/robotic-inspection-for-chemicals/) |
| Unitree | 脚・人型の機体供給 | G1等を製品として供給。購入可能性と、顧客業務を自律完遂できることは別。[G1公式](https://www.unitree.com/g1/) |
| Agility | 人型の物流作業 | DigitをGXOの商用契約・現場運用へ接続。[導入発表](https://www.agilityrobotics.com/content/digit-deployed-at-gxo-in-historic-humanoid-raas-agreement) |
| Figure／Hexagon | 人型・移動操作 | BMWでの生産パイロット。現場での検証対象として注目。[BMW](https://www.bmwgroup.com/de/news/allgemein/2026/humanoide-roboter-in-leipzig.html) |
| Google DeepMind | 認識・推論・方策 | Gemini Robotics系。2026-04-14のER 1.6は身体環境の推論能力を強化。推論モデルの提供と全身制御製品の普及は区別。[公式解説](https://deepmind.google/blog/gemini-robotics-er-1-6/) |
| Physical Intelligence | 操作の基盤モデル | π₀を起点とした多機体・多課題の方策研究。[π₀](https://www.physicalintelligence.company/blog/pi0) |
| NVIDIA | 学習・シミュレーション基盤 | Isaac系とGR00T。複数の機体企業が使う開発基盤側。[GR00T研究](https://research.nvidia.com/publication/2025-03_nvidia-isaac-gr00t-n1-open-foundation-model-humanoid-robots) |

この表からの解釈として、機体メーカー、AIモデル開発者、現場への導入者は競合するだけでなく組み合わせて価値を作る。日本を「古い機械だけ」、海外を「AIだけ」と分けるのは不正確。国内にも知能化・運用統合の企業があり、海外にも駆動・製造・保守を積み上げる企業がある。

## 8. 「最先端」を見分けるための観点

派手な一回の成功と、仕事として使えることの間には差がある。比較するときは次を確認する。

| 確認すること | 読み違えやすい例 |
| --- | --- |
| 自律／遠隔操作／人の介入 | 動画で手が映らなくても自律とは限らない |
| デモ／現場実証／商用運用／追加計画 | 「1,000台導入へ」と「1,000台稼働中」は別 |
| 対象物と環境の範囲 | 同じ箱を運ぶ成功が、透明なコップや衣服へ直結しない |
| 成功率と試行条件 | 成功場面だけでは分母が分からない |
| 失敗後の復帰・人手 | 100回に1回の停止でも、無人連続稼働には大きく響く |
| 速度・破損・保守・総費用 | 研究上の高成功率だけでは事業採算は決まらない |

説明用に、独立した10工程がそれぞれ95%の確率で成功すると仮定すると、全工程の成功は0.95^10≒60%。これは実測値ではなく、長い作業では個別技能の成功率だけでは足りず、復帰や再試行が必要になることを示す例である。

## 9. 今回のSO-101の経験との対応

| 経験 | 研究上の接点 | 現時点で言える範囲 |
| --- | --- | --- |
| 自律動作で震えた | 指令の時間的一貫性、制御周期、閉ループ動作 | 原因を一つに確定していない |
| 時間的アンサンブルで震えが減った | ACTの系列予測の統合 | 本人の改善報告。把持能力や汎化まで証明しない |
| つかむ途中で物を倒した | 接触を伴う操作、認識・追従誤差 | 映像と指令の照合は未完了 |
| 倒した後に進まなかった | 分布シフト、復帰技能、長い作業の計画 | 成功1実演に復帰のお手本がない可能性。停止原因は未確定 |
| 公開データを使いたい | 多機体学習・Open X-Embodiment・基盤方策 | 単位、座標、行動表現、カメラ配置、制御周期の違いを扱う必要がある |

今後の読み順は、教材のFK／IK→ヤコビアン→制御で「どう動くか」を理解し、ACTで「実演から何を学んだか」を整理した後、Diffusion Policy→Mobile ALOHA→Open X-Embodiment／π₀へ広げるとつながりやすい。今回は補足説明であり、理解確認済み・追加実験済みとは記録しない。
