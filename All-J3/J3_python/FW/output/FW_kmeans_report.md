# FW KMeans Report

## 入力概要
- 入力ファイル: `/Users/machidanoboruyuu/Desktop/FCTokushima-EhimeFC-DataAnalysis/All-J3/J3_csv/SC_position_clustering/FW/FW_features_preprocessed.csv`
- サンプル数: 117
- 識別列: `FB_Name`, `SC_Name`, `analysis_position_code`, `analysis_position_jp`
- 使用した z 列:
  - `z_shot_conversion_rate_pct` (決定率)
  - `z_out_box_shots_per90` (ボックス外シュート_per90)
  - `z_box_shots_per90` (ボックス内シュート_per90)
  - `z_shot_on_target_rate_pct` (枠内率)
  - `z_goals_per90` (得点_per90)
  - `z_aerial_wins_per90` (空中戦勝利数_per90)
  - `z_successful_forward_passes_per90` (前進パス成功数_per90)
  - `z_last_passes_per90` (ラストパス_per90)
  - `z_attacking_third_gains_per90` (攻撃3rd奪回_per90)
  - `z_sprint_count_full_all_per_match` (スプリント回数_per_match)

## 使用対象列
- 指定 z 列に対応する raw / win / z / imputed 列を使用しました。
- `raw_shot_conversion_rate_pct` / `win_shot_conversion_rate_pct` / `z_shot_conversion_rate_pct` / `imputed_shot_conversion_rate_pct`
- `raw_out_box_shots_per90` / `win_out_box_shots_per90` / `z_out_box_shots_per90` / `imputed_out_box_shots_per90`
- `raw_box_shots_per90` / `win_box_shots_per90` / `z_box_shots_per90` / `imputed_box_shots_per90`
- `raw_shot_on_target_rate_pct` / `win_shot_on_target_rate_pct` / `z_shot_on_target_rate_pct` / `imputed_shot_on_target_rate_pct`
- `raw_goals_per90` / `win_goals_per90` / `z_goals_per90` / `imputed_goals_per90`
- `raw_aerial_wins_per90` / `win_aerial_wins_per90` / `z_aerial_wins_per90` / `imputed_aerial_wins_per90`
- `raw_successful_forward_passes_per90` / `win_successful_forward_passes_per90` / `z_successful_forward_passes_per90` / `imputed_successful_forward_passes_per90`
- `raw_last_passes_per90` / `win_last_passes_per90` / `z_last_passes_per90` / `imputed_last_passes_per90`
- `raw_attacking_third_gains_per90` / `win_attacking_third_gains_per90` / `z_attacking_third_gains_per90` / `imputed_attacking_third_gains_per90`
- `raw_sprint_count_full_all_per_match` / `win_sprint_count_full_all_per_match` / `z_sprint_count_full_all_per_match` / `imputed_sprint_count_full_all_per_match`

## 欠損補完メモ
- 残存 z 欠損はポジション内中央値で補完しました。
- `imputed_count > 0` の選手数: 35
- 出力列として `imputed_count` / `imputed_ratio` を付与しています。
- 入力 `imputed_*` 列の件数:
  - `z_shot_conversion_rate_pct`: 35 件
  - `z_out_box_shots_per90`: 35 件
  - `z_box_shots_per90`: 35 件
  - `z_shot_on_target_rate_pct`: 35 件
  - `z_goals_per90`: 35 件
  - `z_aerial_wins_per90`: 35 件
  - `z_successful_forward_passes_per90`: 35 件
  - `z_last_passes_per90`: 35 件
  - `z_attacking_third_gains_per90`: 35 件
  - `z_sprint_count_full_all_per_match`: 0 件
- 追加で中央値補完した列と件数:
  - 追加補完は発生していません。

## KMeans 設定
- n_clusters: 4
- random_state: 42
- n_init: 50
- max_iter: 300
- k=4 の inertia: 793.839769
- k=4 の silhouette score: 0.276585

## 参考指標 (k=2, 3, 4, 5, 6)
| k | inertia | silhouette_score | 採用 seed |
| --- | ---: | ---: | ---: |
| 2 | 1001.353667 | 0.299243 | 73 |
| 3 | 882.492271 | 0.248850 | 44 |
| 4 | 793.839769 | 0.276585 | 54 |
| 5 | 696.624380 | 0.258914 | 88 |
| 6 | 640.945410 | 0.210722 | 62 |

- silhouette score の最大は k=2 (0.299243) でした。
- 今回は要件どおり k=4 を採用しています。 参考上は k=2 の方が分離度は高めでした。
- k=4 の silhouette score は 0.276585 で、 クラスタ解釈と業務用途の両立を前提に見る必要があります。

## 各クラスタ人数
- Cluster 0: 82 名
- Cluster 1: 2 名
- Cluster 2: 16 名
- Cluster 3: 17 名

## 原点に最も近いクラスタ
- Cluster 0 が最も原点に近く、「平均型候補」として扱います。
- 距離: 0.673148 / 判定メモ: はい。原点にかなり近く、平均型候補とみなしやすいです。

## クラスタ中心の特徴
### Cluster 0
- 人数: 82 名
- 原点からの距離: 0.673148
- 絶対値上位3変数: 前進パス成功数_per90 (-0.422966), 攻撃3rd奪回_per90 (-0.328221), ラストパス_per90 (-0.298377)
- 高い z 値の主軸: スプリント回数_per_match (0.177754), ボックス内シュート_per90 (0.043147), 決定率 (0.031171)
- 解釈: 平均型候補。はい。原点にかなり近く、平均型候補とみなしやすいです。
- クラスタ中心の z 値:
  - 決定率: 0.031171
  - ボックス外シュート_per90: -0.149406
  - ボックス内シュート_per90: 0.043147
  - 枠内率: -0.111961
  - 得点_per90: -0.004590
  - 空中戦勝利数_per90: -0.090345
  - 前進パス成功数_per90: -0.422966
  - ラストパス_per90: -0.298377
  - 攻撃3rd奪回_per90: -0.328221
  - スプリント回数_per_match: 0.177754

### Cluster 1
- 人数: 2 名
- 原点からの距離: 7.540777
- 絶対値上位3変数: 決定率 (4.726680), 枠内率 (4.073561), 得点_per90 (3.205707)
- 高い z 値の主軸: 決定率 (4.726680), 枠内率 (4.073561), 得点_per90 (3.205707)
- 解釈候補: フィニッシュ寄り / 空中戦・前進関与寄り。 最終ラベルは RandomForest と代表選手確認で詰める前提です。
- クラスタ中心の z 値:
  - 決定率: 4.726680
  - ボックス外シュート_per90: -1.816666
  - ボックス内シュート_per90: 0.252766
  - 枠内率: 4.073561
  - 得点_per90: 3.205707
  - 空中戦勝利数_per90: 1.122181
  - 前進パス成功数_per90: 0.036340
  - ラストパス_per90: 0.986545
  - 攻撃3rd奪回_per90: -0.734778
  - スプリント回数_per_match: -1.230209

### Cluster 2
- 人数: 16 名
- 原点からの距離: 2.680051
- 絶対値上位3変数: ラストパス_per90 (1.450350), ボックス内シュート_per90 (1.083838), 空中戦勝利数_per90 (1.040615)
- 高い z 値の主軸: ラストパス_per90 (1.450350), ボックス内シュート_per90 (1.083838), 空中戦勝利数_per90 (1.040615)
- 解釈候補: 空中戦・前進関与寄り / ミドルレンジ関与寄り。 最終ラベルは RandomForest と代表選手確認で詰める前提です。
- クラスタ中心の z 値:
  - 決定率: 0.018349
  - ボックス外シュート_per90: 0.986969
  - ボックス内シュート_per90: 1.083838
  - 枠内率: -0.177768
  - 得点_per90: 0.711060
  - 空中戦勝利数_per90: 1.040615
  - 前進パス成功数_per90: 0.743161
  - ラストパス_per90: 1.450350
  - 攻撃3rd奪回_per90: 0.726974
  - スプリント回数_per_match: -0.478686

### Cluster 3
- 人数: 17 名
- 原点からの距離: 2.547829
- 絶対値上位3変数: 前進パス成功数_per90 (1.336467), ボックス内シュート_per90 (-1.257940), 得点_per90 (-1.024234)
- 高い z 値の主軸: 前進パス成功数_per90 (1.336467), 攻撃3rd奪回_per90 (0.985416), 枠内率 (0.228118)
- 解釈候補: 空中戦・前進関与寄り / 前線守備・回収寄り。 最終ラベルは RandomForest と代表選手確認で詰める前提です。
- クラスタ中心の z 値:
  - 決定率: -0.723703
  - ボックス外シュート_per90: 0.005475
  - ボックス内シュート_per90: -1.257940
  - 枠内率: 0.228118
  - 得点_per90: -1.024234
  - 空中戦勝利数_per90: -0.675641
  - 前進パス成功数_per90: 1.336467
  - ラストパス_per90: -0.041869
  - 攻撃3rd奪回_per90: 0.985416
  - スプリント回数_per_match: -0.262142

## 他クラスタの大まかな特徴
- Cluster 1: フィニッシュ寄り / 空中戦・前進関与寄り を示す候補。 原点距離は 7.540777。
- Cluster 2: 空中戦・前進関与寄り / ミドルレンジ関与寄り を示す候補。 原点距離は 2.680051。
- Cluster 3: 空中戦・前進関与寄り / 前線守備・回収寄り を示す候補。 原点距離は 2.547829。

## 今後 RandomForest で見るべき論点
- Cluster 0 を one-vs-rest にして、 平均型候補を他クラスタから最も分ける変数が何かを確認する。
- 各 specialized cluster 候補について、上位変数が本当に判別寄与でも上位に来るかを確認する。
- 走力系と技術系、守備系と配球系のような相関の強い軸で重要度が偏りすぎないかを確認する。
- 代表選手をクラスタ距離の近い順に見て、クラスタ中心の解釈が現場感覚と矛盾しないか確認する。
