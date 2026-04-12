# CB Recommendation Report

## 入力ファイル
- `/Users/machidanoboruyuu/Desktop/FCTokushima-EhimeFC-DataAnalysis/All-J3/J3_python/CB/output/CB_clustered_players.csv`
- `/Users/machidanoboruyuu/Desktop/FCTokushima-EhimeFC-DataAnalysis/All-J3/J3_python/CB/output/CB_cluster_centers_z.csv`
- `/Users/machidanoboruyuu/Desktop/FCTokushima-EhimeFC-DataAnalysis/All-J3/J3_python/CB/output/CB_rf_report.md`

## 採用したクラスタラベル
- 今回のラベルは分析用の作業ラベルです。
- Cluster 0: ビルドアップ型
- Cluster 1: 守備安定型
- Cluster 2: 対人迎撃型
- Cluster 3: 平均型

## スコア設計方針
- 10変数全部の単純合算は使わず、専門型クラスタは KMeans 中心と RandomForest 解釈の両方で効いていた 2〜3 変数だけを使いました。
- 平均型クラスタだけは単純加算にせず、KMeans で使った全 z 列ベクトルのクラスタ中心とのユークリッド距離で評価しました。
- スコアはクラスタ像への近さを見るもので、選手の総合力順位ではありません。

## 各クラスタのスコア式と変数選定理由
### Cluster 0: ビルドアップ型
- スコア式: `score_cluster_0 = z_successful_forward_passes_per90 + z_pass_success_rate_pct + z_successful_long_passes_per90`
- 使用変数: 前進パス成功数_per90 (`z_successful_forward_passes_per90`) + パス成功率 (`z_pass_success_rate_pct`) + ロングパス成功数_per90 (`z_successful_long_passes_per90`)
- 変数選定理由: ビルドアップ型は KMeans 中心で前進パス・パス成功率・ロングパスがいずれも高く、RandomForest でも同じ3変数が上位でした。配球役としての像を最も素直に表すため、この3変数に限定しました。

### Cluster 1: 守備安定型
- スコア式: `score_cluster_1 = z_clearances_per90 + z_aerial_duel_win_rate_pct - z_medaccel_count_full_all_per_match`
- 使用変数: クリア_per90 (`z_clearances_per90`) + 空中戦勝率 (`z_aerial_duel_win_rate_pct`) - 中加速回数_per_match (`z_medaccel_count_full_all_per_match`)
- 変数選定理由: 守備安定型は KMeans 側でクリアと空中戦がプラス、RandomForest 側で中加速回数の低さが強く効いていました。危険除去と空中対応を加点しつつ、相対的に機動力が低めという像を減点項で反映しました。

### Cluster 2: 対人迎撃型
- スコア式: `score_cluster_2 = z_tackle_win_rate_pct + z_interceptions_per90`
- 使用変数: タックル奪取率 (`z_tackle_win_rate_pct`) + インターセプト_per90 (`z_interceptions_per90`)
- 変数選定理由: 対人迎撃型は少数クラスタなので、無理に変数を増やさず対人勝率と迎撃回数に絞りました。タックル奪取率とインターセプトは KMeans 中心でも強く、クラスタ像をシンプルに捉えやすい2軸です。

### Cluster 3: 平均型
- スコア式: `score_cluster_3 = - euclidean_distance(player_z_vector, cb_cluster_3_center_z_vector)`
- 使用変数: KMeans に使った全 z 列
- 変数選定理由: 平均型は単一の突出変数で定義されるクラスタではなく、10変数全体で中心に近いかどうかで見るのが自然です。そのため単純加算ではなく、KMeans に使った全 z 列で cluster 3 中心までの距離を用います。
- 距離列: `distance_to_cluster_center_3`

## 平均型だけ距離ベースにした理由
- 平均型は特定の少数変数が突出するクラスタではなく、全体ベクトルでクラスタ中心に近いかどうかを見た方が KMeans の定義に忠実です。
- 2〜3 変数の単純加算にすると specialized cluster 側の特徴量だけを拾ってしまい、平均型を平均型として評価しにくくなります。

## 各クラスタ Top10 の概要
### Cluster 0: ビルドアップ型
- Top3: 篠﨑　輝和 / 附木　雄也 / 井上　航希
- Top10 内の元同クラスタ所属: 10/10 (100.0%)
- 概要: 前進パス成功数_per90・パス成功率・ロングパス成功数_per90が高い選手が上位です。

### Cluster 1: 守備安定型
- Top3: 大武　峻 / 橋内　優也 / 都並　優太
- Top10 内の元同クラスタ所属: 9/10 (90.0%)
- 概要: クリア_per90・空中戦勝率が高く、中加速回数_per_matchは低めの選手が上位です。

### Cluster 2: 対人迎撃型
- Top3: 篠﨑　輝和 / 雪江　悠人 / 砂森　和也
- Top10 内の元同クラスタ所属: 4/10 (40.0%)
- 概要: タックル奪取率・インターセプト_per90が高い選手が上位です。

### Cluster 3: 平均型
- Top3: 広瀬　健太 / マテイ　ヨニッチ / 小林　大智
- Top10 内の元同クラスタ所属: 10/10 (100.0%)
- 概要: 全 z 列ベクトルでクラスタ中心との距離が小さい選手が上位です。
- 距離の目安: 1位の `distance_to_cluster_center_3` = 0.454

## 「クラスタ所属」と「クラスタ像へのスコア順位」がズレた代表例
- `篠﨑　輝和` (`Terukazu Shinozaki`) は元 `Cluster 0: ビルドアップ型` ですが、 `Cluster 2: 対人迎撃型` スコアで 1 位です (`score=6.947`, タックル奪取率=2.992, インターセプト_per90=3.955)。
- `深津　康太` (`Kota Fukatsu`) は元 `Cluster 3: 平均型` ですが、 `Cluster 1: 守備安定型` スコアで 7 位です (`score=3.512`, クリア_per90=1.720, 空中戦勝率=1.423, 中加速回数_per_match=-0.369)。

## スコア式の注意点
- これは総合力ランキングではありません。
- あくまで特定のクラスタ像への近さを見るためのスコアです。
- specialized cluster の式は、そのクラスタ像を表す少数変数だけを強く見ています。
- 平均型は距離ベースなので、`score = -distance` です。0 に近いほど中心に近く、より平均型らしいと解釈します。
