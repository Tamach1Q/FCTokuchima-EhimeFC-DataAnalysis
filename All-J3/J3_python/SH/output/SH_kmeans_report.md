# SH KMeans Report

## 入力概要
- 入力ファイル: `/Users/machidanoboruyuu/Desktop/FCTokushima-EhimeFC-DataAnalysis/All-J3/J3_csv/SC_position_clustering/SH/SH_features_preprocessed.csv`
- サンプル数: 215
- 識別列: `FB_Name`, `SC_Name`, `analysis_position_code`, `analysis_position_jp`
- 使用した z 列:
  - `z_sprint_distance_full_all_per_match` (スプリント距離_per_match)
  - `z_hsr_count_full_all_per_match` (HSR回数_per_match)
  - `z_dribble_success_rate_pct` (ドリブル成功率)
  - `z_crosses_per90` (クロス数_per90)
  - `z_cross_success_rate_pct` (クロス成功率)
  - `z_last_passes_per90` (ラストパス_per90)
  - `z_pa_entry_per90` (PA進入_per90)
  - `z_shot_conversion_rate_pct` (決定率)
  - `z_regain_within_5s_per90` (ロスト後5秒未満リゲイン_per90)

## 使用対象列
- 指定 z 列に対応する raw / win / z / imputed 列を使用しました。
- `raw_sprint_distance_full_all_per_match` / `win_sprint_distance_full_all_per_match` / `z_sprint_distance_full_all_per_match` / `imputed_sprint_distance_full_all_per_match`
- `raw_hsr_count_full_all_per_match` / `win_hsr_count_full_all_per_match` / `z_hsr_count_full_all_per_match` / `imputed_hsr_count_full_all_per_match`
- `raw_dribble_success_rate_pct` / `win_dribble_success_rate_pct` / `z_dribble_success_rate_pct` / `imputed_dribble_success_rate_pct`
- `raw_crosses_per90` / `win_crosses_per90` / `z_crosses_per90` / `imputed_crosses_per90`
- `raw_cross_success_rate_pct` / `win_cross_success_rate_pct` / `z_cross_success_rate_pct` / `imputed_cross_success_rate_pct`
- `raw_last_passes_per90` / `win_last_passes_per90` / `z_last_passes_per90` / `imputed_last_passes_per90`
- `raw_pa_entry_per90` / `win_pa_entry_per90` / `z_pa_entry_per90` / `imputed_pa_entry_per90`
- `raw_shot_conversion_rate_pct` / `win_shot_conversion_rate_pct` / `z_shot_conversion_rate_pct` / `imputed_shot_conversion_rate_pct`
- `raw_regain_within_5s_per90` / `win_regain_within_5s_per90` / `z_regain_within_5s_per90` / `imputed_regain_within_5s_per90`

## 欠損補完メモ
- 残存 z 欠損はポジション内中央値で補完しました。
- `imputed_count > 0` の選手数: 69
- 出力列として `imputed_count` / `imputed_ratio` を付与しています。
- 入力 `imputed_*` 列の件数:
  - `z_sprint_distance_full_all_per_match`: 0 件
  - `z_hsr_count_full_all_per_match`: 0 件
  - `z_dribble_success_rate_pct`: 69 件
  - `z_crosses_per90`: 69 件
  - `z_cross_success_rate_pct`: 69 件
  - `z_last_passes_per90`: 69 件
  - `z_pa_entry_per90`: 69 件
  - `z_shot_conversion_rate_pct`: 69 件
  - `z_regain_within_5s_per90`: 69 件
- 追加で中央値補完した列と件数:
  - 追加補完は発生していません。

## KMeans 設定
- n_clusters: 4
- random_state: 42
- n_init: 50
- max_iter: 300
- k=4 の inertia: 1246.992616
- k=4 の silhouette score: 0.175126

## 参考指標 (k=2, 3, 4, 5, 6)
| k | inertia | silhouette_score | 採用 seed |
| --- | ---: | ---: | ---: |
| 2 | 1614.174453 | 0.164759 | 49 |
| 3 | 1399.139666 | 0.170743 | 42 |
| 4 | 1246.992616 | 0.175126 | 46 |
| 5 | 1143.778237 | 0.176551 | 86 |
| 6 | 1066.789826 | 0.155734 | 69 |

- silhouette score の最大は k=5 (0.176551) でした。
- 今回は要件どおり k=4 を採用しています。 参考上は k=5 の方が分離度は高めでした。
- k=4 の silhouette score は 0.175126 で、 クラスタ解釈と業務用途の両立を前提に見る必要があります。

## 各クラスタ人数
- Cluster 0: 65 名
- Cluster 1: 34 名
- Cluster 2: 5 名
- Cluster 3: 111 名

## 原点に最も近いクラスタ
- Cluster 3 が最も原点に近く、「平均型候補」として扱います。
- 距離: 0.718479 / 判定メモ: はい。原点にかなり近く、平均型候補とみなしやすいです。

## クラスタ中心の特徴
### Cluster 0
- 人数: 65 名
- 原点からの距離: 1.690004
- 絶対値上位3変数: スプリント距離_per_match (1.171660), HSR回数_per_match (1.075149), ドリブル成功率 (0.287410)
- 高い z 値の主軸: スプリント距離_per_match (1.171660), HSR回数_per_match (1.075149), ドリブル成功率 (0.287410)
- 解釈候補: 縦突破寄り / 守備回収寄り。 最終ラベルは RandomForest と代表選手確認で詰める前提です。
- クラスタ中心の z 値:
  - スプリント距離_per_match: 1.171660
  - HSR回数_per_match: 1.075149
  - ドリブル成功率: 0.287410
  - クロス数_per90: 0.253417
  - クロス成功率: 0.067919
  - ラストパス_per90: 0.157119
  - PA進入_per90: 0.279084
  - 決定率: 0.069209
  - ロスト後5秒未満リゲイン_per90: -0.261875

### Cluster 1
- 人数: 34 名
- 原点からの距離: 2.500293
- 絶対値上位3変数: ロスト後5秒未満リゲイン_per90 (1.457024), ドリブル成功率 (-1.379810), スプリント距離_per_match (-0.752359)
- 高い z 値の主軸: ロスト後5秒未満リゲイン_per90 (1.457024), クロス成功率 (0.273332)
- 解釈候補: 守備回収寄り / クロス供給寄り。 最終ラベルは RandomForest と代表選手確認で詰める前提です。
- クラスタ中心の z 値:
  - スプリント距離_per_match: -0.752359
  - HSR回数_per_match: -0.574753
  - ドリブル成功率: -1.379810
  - クロス数_per90: -0.682191
  - クロス成功率: 0.273332
  - ラストパス_per90: -0.319731
  - PA進入_per90: -0.674564
  - 決定率: -0.480552
  - ロスト後5秒未満リゲイン_per90: 1.457024

### Cluster 2
- 人数: 5 名
- 原点からの距離: 6.819246
- 絶対値上位3変数: PA進入_per90 (4.392454), クロス数_per90 (4.366515), ラストパス_per90 (1.919453)
- 高い z 値の主軸: PA進入_per90 (4.392454), クロス数_per90 (4.366515), ラストパス_per90 (1.919453)
- 解釈候補: フィニッシュ関与寄り / 縦突破寄り。 最終ラベルは RandomForest と代表選手確認で詰める前提です。
- クラスタ中心の z 値:
  - スプリント距離_per_match: -0.842237
  - HSR回数_per_match: -1.289218
  - ドリブル成功率: 0.796795
  - クロス数_per90: 4.366515
  - クロス成功率: -0.134877
  - ラストパス_per90: 1.919453
  - PA進入_per90: 4.392454
  - 決定率: 1.051264
  - ロスト後5秒未満リゲイン_per90: -0.572746

### Cluster 3
- 人数: 111 名
- 原点からの距離: 0.718479
- 絶対値上位3変数: スプリント距離_per_match (-0.417717), HSR回数_per_match (-0.395468), ロスト後5秒未満リゲイン_per90 (-0.267146)
- 高い z 値の主軸: ドリブル成功率 (0.218450), 決定率 (0.059314)
- 解釈: 平均型候補。はい。原点にかなり近く、平均型候補とみなしやすいです。
- クラスタ中心の z 値:
  - スプリント距離_per_match: -0.417717
  - HSR回数_per_match: -0.395468
  - ドリブル成功率: 0.218450
  - クロス数_per90: -0.136128
  - クロス成功率: -0.117420
  - ラストパス_per90: -0.080533
  - PA進入_per90: -0.154663
  - 決定率: 0.059314
  - ロスト後5秒未満リゲイン_per90: -0.267146

## 他クラスタの大まかな特徴
- Cluster 0: 縦突破寄り / 守備回収寄り を示す候補。 原点距離は 1.690004。
- Cluster 1: 守備回収寄り / クロス供給寄り を示す候補。 原点距離は 2.500293。
- Cluster 2: フィニッシュ関与寄り / 縦突破寄り を示す候補。 原点距離は 6.819246。

## 今後 RandomForest で見るべき論点
- Cluster 3 を one-vs-rest にして、 平均型候補を他クラスタから最も分ける変数が何かを確認する。
- 各 specialized cluster 候補について、上位変数が本当に判別寄与でも上位に来るかを確認する。
- 走力系と技術系、守備系と配球系のような相関の強い軸で重要度が偏りすぎないかを確認する。
- 代表選手をクラスタ距離の近い順に見て、クラスタ中心の解釈が現場感覚と矛盾しないか確認する。
