# SB Recommendation Report

## 入力ファイル
- `/Users/machidanoboruyuu/Desktop/FCTokushima-EhimeFC-DataAnalysis/All-J3/J3_python/SB/output/SB_clustered_players.csv`
- `/Users/machidanoboruyuu/Desktop/FCTokushima-EhimeFC-DataAnalysis/All-J3/J3_python/SB/output/SB_cluster_centers_z.csv`
- `/Users/machidanoboruyuu/Desktop/FCTokushima-EhimeFC-DataAnalysis/All-J3/J3_python/SB/output/SB_rf_report.md`

## 採用したクラスタラベル
- 今回のラベルは分析用の作業ラベルです。
- Cluster 0: 上下動型
- Cluster 1: 守備回収・配球型
- Cluster 2: 平均型
- Cluster 3: 攻撃参加型

## スコア設計方針
- 10変数全部の単純合算は使わず、専門型クラスタは KMeans 中心と RandomForest 解釈の両方で効いていた 2〜3 変数だけを使いました。
- 平均型クラスタだけは単純加算にせず、KMeans で使った全 z 列ベクトルのクラスタ中心とのユークリッド距離で評価しました。
- スコアはクラスタ像への近さを見るもので、選手の総合力順位ではありません。

## 各クラスタのスコア式と変数選定理由
### Cluster 0: 上下動型
- スコア式: `score_cluster_0 = z_hi_distance_full_all_per_match + z_running_distance_full_all_per_match + z_sprint_count_full_all_per_match`
- 使用変数: HI距離_per_match (`z_hi_distance_full_all_per_match`) + 走行距離_per_match (`z_running_distance_full_all_per_match`) + スプリント回数_per_match (`z_sprint_count_full_all_per_match`)
- 変数選定理由: 上下動型は KMeans 中心でも RandomForest でも HI距離、走行距離、スプリント回数が主要軸でした。運動量と往復強度をそのまま表す3変数に絞ることで、上下動型の像を明確に出します。

### Cluster 1: 守備回収・配球型
- スコア式: `score_cluster_1 = z_blocks_per90 + z_regain_within_5s_per90 + z_forward_long_pass_success_rate_pct`
- 使用変数: ブロック_per90 (`z_blocks_per90`) + ロスト後5秒未満リゲイン_per90 (`z_regain_within_5s_per90`) + 前方向ロングパス成功率 (`z_forward_long_pass_success_rate_pct`)
- 変数選定理由: 守備回収・配球型は守備回収と前方向への配球を両立するクラスタとして扱います。ブロックと即時奪回で守備回収を、前方向ロングパス成功率で配球面を表現する3変数を採用しました。

### Cluster 2: 平均型
- スコア式: `score_cluster_2 = - euclidean_distance(player_z_vector, sb_cluster_2_center_z_vector)`
- 使用変数: KMeans に使った全 z 列
- 変数選定理由: 平均型は specialized cluster のような突出変数ではなく、10変数の全体バランスで定義されるため、KMeans に使った全 z 列の cluster 2 中心への距離をそのまま使います。
- 距離列: `distance_to_cluster_center_2`

### Cluster 3: 攻撃参加型
- スコア式: `score_cluster_3 = z_pa_entry_per90 + z_crosses_per90 + z_tackle_win_rate_pct`
- 使用変数: PA進入_per90 (`z_pa_entry_per90`) + クロス数_per90 (`z_crosses_per90`) + タックル奪取率 (`z_tackle_win_rate_pct`)
- 変数選定理由: 攻撃参加型は PA 侵入とクロス供給が主軸で、RandomForest でも PA進入・クロス数・タックル奪取率が上位でした。前進参加だけでなく、前で潰せる守備強度も含めてこの3変数で表します。

## 平均型だけ距離ベースにした理由
- 平均型は特定の少数変数が突出するクラスタではなく、全体ベクトルでクラスタ中心に近いかどうかを見た方が KMeans の定義に忠実です。
- 2〜3 変数の単純加算にすると specialized cluster 側の特徴量だけを拾ってしまい、平均型を平均型として評価しにくくなります。

## 各クラスタ Top10 の概要
### Cluster 0: 上下動型
- Top3: 音泉　翔眞 / 上月　翔聖 / 荒木　遼太
- Top10 内の元同クラスタ所属: 8/10 (80.0%)
- 概要: HI距離_per_match・走行距離_per_match・スプリント回数_per_matchが高い選手が上位です。

### Cluster 1: 守備回収・配球型
- Top3: 玉城　大志 / 柴田　徹 / 小泉　隆斗
- Top10 内の元同クラスタ所属: 7/10 (70.0%)
- 概要: ブロック_per90・ロスト後5秒未満リゲイン_per90・前方向ロングパス成功率が高い選手が上位です。

### Cluster 2: 平均型
- Top3: 大串　昇平 / 永井　颯太 / 河野　諒祐
- Top10 内の元同クラスタ所属: 10/10 (100.0%)
- 概要: 全 z 列ベクトルでクラスタ中心との距離が小さい選手が上位です。
- 距離の目安: 1位の `distance_to_cluster_center_2` = 0.567

### Cluster 3: 攻撃参加型
- Top3: 宮脇　茂夫 / 櫻井　風我 / 泉　柊椰
- Top10 内の元同クラスタ所属: 10/10 (100.0%)
- 概要: PA進入_per90・クロス数_per90・タックル奪取率が高い選手が上位です。

## 「クラスタ所属」と「クラスタ像へのスコア順位」がズレた代表例
- `山脇　樺織` (`Kaoru Yamawaki`) は元 `Cluster 3: 攻撃参加型` ですが、 `Cluster 0: 上下動型` スコアで 4 位です (`score=5.158`, HI距離_per_match=1.627, 走行距離_per_match=1.264, スプリント回数_per_match=2.267)。
- `梅木　怜` (`Rei Umeki`) は元 `Cluster 0: 上下動型` ですが、 `Cluster 1: 守備回収・配球型` スコアで 4 位です (`score=4.602`, ブロック_per90=1.858, ロスト後5秒未満リゲイン_per90=1.806, 前方向ロングパス成功率=0.938)。

## スコア式の注意点
- これは総合力ランキングではありません。
- あくまで特定のクラスタ像への近さを見るためのスコアです。
- specialized cluster の式は、そのクラスタ像を表す少数変数だけを強く見ています。
- 平均型は距離ベースなので、`score = -distance` です。0 に近いほど中心に近く、より平均型らしいと解釈します。
