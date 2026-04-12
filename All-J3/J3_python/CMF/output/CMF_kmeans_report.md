# CMF KMeans Report

## 入力概要
- 入力ファイル: `/Users/machidanoboruyuu/Desktop/FCTokushima-EhimeFC-DataAnalysis/All-J3/J3_csv/SC_position_clustering/CMF/CMF_features_preprocessed.csv`
- サンプル数: 32
- 識別列: `FB_Name`, `SC_Name`, `analysis_position_code`, `analysis_position_jp`
- 使用した z 列:
  - `z_running_distance_full_all_per_match` (走行距離_per_match)
  - `z_ball_gains_per90` (ボール奪取_per90)
  - `z_interceptions_per90` (インターセプト_per90)
  - `z_pass_success_rate_pct` (パス成功率)
  - `z_forward_pass_success_rate_pct` (前進パス成功率)
  - `z_short_pass_share_pct` (ショートパス比率)
  - `z_long_pass_share_pct` (ロングパス比率)
  - `z_opponent_half_gain_share_pct` (敵陣奪回比率)

## 使用対象列
- 指定 z 列に対応する raw / win / z / imputed 列を使用しました。
- `raw_running_distance_full_all_per_match` / `win_running_distance_full_all_per_match` / `z_running_distance_full_all_per_match` / `imputed_running_distance_full_all_per_match`
- `raw_ball_gains_per90` / `win_ball_gains_per90` / `z_ball_gains_per90` / `imputed_ball_gains_per90`
- `raw_interceptions_per90` / `win_interceptions_per90` / `z_interceptions_per90` / `imputed_interceptions_per90`
- `raw_pass_success_rate_pct` / `win_pass_success_rate_pct` / `z_pass_success_rate_pct` / `imputed_pass_success_rate_pct`
- `raw_forward_pass_success_rate_pct` / `win_forward_pass_success_rate_pct` / `z_forward_pass_success_rate_pct` / `imputed_forward_pass_success_rate_pct`
- `raw_short_pass_share_pct` / `win_short_pass_share_pct` / `z_short_pass_share_pct` / `imputed_short_pass_share_pct`
- `raw_long_pass_share_pct` / `win_long_pass_share_pct` / `z_long_pass_share_pct` / `imputed_long_pass_share_pct`
- `raw_opponent_half_gain_share_pct` / `win_opponent_half_gain_share_pct` / `z_opponent_half_gain_share_pct` / `imputed_opponent_half_gain_share_pct`

## 欠損補完メモ
- 残存 z 欠損はポジション内中央値で補完しました。
- `imputed_count > 0` の選手数: 8
- 出力列として `imputed_count` / `imputed_ratio` を付与しています。
- 入力 `imputed_*` 列の件数:
  - `z_running_distance_full_all_per_match`: 0 件
  - `z_ball_gains_per90`: 8 件
  - `z_interceptions_per90`: 8 件
  - `z_pass_success_rate_pct`: 8 件
  - `z_forward_pass_success_rate_pct`: 8 件
  - `z_short_pass_share_pct`: 8 件
  - `z_long_pass_share_pct`: 8 件
  - `z_opponent_half_gain_share_pct`: 8 件
- 追加で中央値補完した列と件数:
  - 追加補完は発生していません。

## KMeans 設定
- n_clusters: 3
- random_state: 42
- n_init: 50
- max_iter: 300
- k=3 の inertia: 152.626487
- k=3 の silhouette score: 0.247566

## 参考指標 (k=2, 3, 4, 5, 6)
| k | inertia | silhouette_score | 採用 seed |
| --- | ---: | ---: | ---: |
| 2 | 185.725672 | 0.318350 | 42 |
| 3 | 152.626487 | 0.247566 | 63 |
| 4 | 132.995140 | 0.238597 | 46 |
| 5 | 118.814952 | 0.244014 | 47 |
| 6 | 104.424112 | 0.229443 | 62 |

- silhouette score の最大は k=2 (0.318350) でした。
- 今回は要件どおり k=3 を採用しています。 参考上は k=2 の方が分離度は高めでした。
- k=3 の silhouette score は 0.247566 で、 クラスタ解釈と業務用途の両立を前提に見る必要があります。

## 各クラスタ人数
- Cluster 0: 9 名
- Cluster 1: 18 名
- Cluster 2: 5 名

## 原点に最も近いクラスタ
- Cluster 1 が最も原点に近く、「平均型候補」として扱います。
- 距離: 0.663756 / 判定メモ: はい。原点にかなり近く、平均型候補とみなしやすいです。

## クラスタ中心の特徴
### Cluster 0
- 人数: 9 名
- 原点からの距離: 2.048946
- 絶対値上位3変数: パス成功率 (-1.170168), 敵陣奪回比率 (-0.864058), 前進パス成功率 (-0.810454)
- 高い z 値の主軸: ロングパス比率 (0.802577), ボール奪取_per90 (0.425331)
- 解釈候補: ボックストゥボックス寄り / ボールハント寄り。 最終ラベルは RandomForest と代表選手確認で詰める前提です。
- クラスタ中心の z 値:
  - 走行距離_per_match: -0.355889
  - ボール奪取_per90: 0.425331
  - インターセプト_per90: -0.433058
  - パス成功率: -1.170168
  - 前進パス成功率: -0.810454
  - ショートパス比率: -0.534998
  - ロングパス比率: 0.802577
  - 敵陣奪回比率: -0.864058

### Cluster 1
- 人数: 18 名
- 原点からの距離: 0.663756
- 絶対値上位3変数: 走行距離_per_match (0.402119), 敵陣奪回比率 (0.351991), ショートパス比率 (-0.269853)
- 高い z 値の主軸: 走行距離_per_match (0.402119), 敵陣奪回比率 (0.351991), パス成功率 (0.243553)
- 解釈: 平均型候補。はい。原点にかなり近く、平均型候補とみなしやすいです。
- クラスタ中心の z 値:
  - 走行距離_per_match: 0.402119
  - ボール奪取_per90: 0.039764
  - インターセプト_per90: 0.120614
  - パス成功率: 0.243553
  - 前進パス成功率: 0.041611
  - ショートパス比率: -0.269853
  - ロングパス比率: 0.070539
  - 敵陣奪回比率: 0.351991

### Cluster 2
- 人数: 5 名
- 原点からの距離: 3.395868
- 絶対値上位3変数: ショートパス比率 (1.934467), ロングパス比率 (-1.698578), 前進パス成功率 (1.309016)
- 高い z 値の主軸: ショートパス比率 (1.934467), 前進パス成功率 (1.309016), パス成功率 (1.229512)
- 解釈候補: ゲームメイク寄り / ボールハント寄り。 最終ラベルは RandomForest と代表選手確認で詰める前提です。
- クラスタ中心の z 値:
  - 走行距離_per_match: -0.807030
  - ボール奪取_per90: -0.908746
  - インターセプト_per90: 0.345294
  - パス成功率: 1.229512
  - 前進パス成功率: 1.309016
  - ショートパス比率: 1.934467
  - ロングパス比率: -1.698578
  - 敵陣奪回比率: 0.288136

## 他クラスタの大まかな特徴
- Cluster 0: ボックストゥボックス寄り / ボールハント寄り を示す候補。 原点距離は 2.048946。
- Cluster 2: ゲームメイク寄り / ボールハント寄り を示す候補。 原点距離は 3.395868。

## 今後 RandomForest で見るべき論点
- Cluster 1 を one-vs-rest にして、 平均型候補を他クラスタから最も分ける変数が何かを確認する。
- 各 specialized cluster 候補について、上位変数が本当に判別寄与でも上位に来るかを確認する。
- 走力系と技術系、守備系と配球系のような相関の強い軸で重要度が偏りすぎないかを確認する。
- 代表選手をクラスタ距離の近い順に見て、クラスタ中心の解釈が現場感覚と矛盾しないか確認する。
