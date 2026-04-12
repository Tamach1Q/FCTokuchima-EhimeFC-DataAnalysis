# SB RandomForest Report

## 入力ファイル
- `/Users/machidanoboruyuu/Desktop/FCTokushima-EhimeFC-DataAnalysis/All-J3/J3_python/SB/output/SB_clustered_players.csv`
- `/Users/machidanoboruyuu/Desktop/FCTokushima-EhimeFC-DataAnalysis/All-J3/J3_python/SB/output/SB_cluster_centers_z.csv`
- `/Users/machidanoboruyuu/Desktop/FCTokushima-EhimeFC-DataAnalysis/All-J3/J3_python/SB/output/SB_cluster_summary.csv`
- `/Users/machidanoboruyuu/Desktop/FCTokushima-EhimeFC-DataAnalysis/All-J3/J3_python/SB/output/SB_kmeans_report.md`

## 使用した z 列
- `z_running_distance_full_all_per_match` (走行距離_per_match)
- `z_hi_distance_full_all_per_match` (HI距離_per_match)
- `z_sprint_count_full_all_per_match` (スプリント回数_per_match)
- `z_crosses_per90` (クロス数_per90)
- `z_cross_success_rate_pct` (クロス成功率)
- `z_pa_entry_per90` (PA進入_per90)
- `z_tackle_win_rate_pct` (タックル奪取率)
- `z_blocks_per90` (ブロック_per90)
- `z_forward_long_pass_success_rate_pct` (前方向ロングパス成功率)
- `z_regain_within_5s_per90` (ロスト後5秒未満リゲイン_per90)

## データ概要
- サンプル数: 123
- cluster_id 一覧: 0, 1, 2, 3
- cluster ごとの positive / negative 件数:
  - Cluster 0: 44 / 79
  - Cluster 1: 16 / 107
  - Cluster 2: 47 / 76
  - Cluster 3: 16 / 107

## RandomForest 設定
- `RandomForestClassifier(n_estimators=1000, random_state=42, class_weight="balanced", min_samples_leaf=2, max_depth=None, n_jobs=-1)`
- one-vs-rest で各 cluster を個別に二値分類
- permutation importance: scoring=`roc_auc`, `n_repeats=30`, `random_state=42`
- 評価指標: train ROC AUC, StratifiedKFold ROC AUC
- 注記: 今回の主目的は予測精度の最適化ではなく、各クラスタを説明する変数の解釈です。

## Cluster 別結果
### Cluster 0
- positive / negative: 44 / 79
- train AUC: 1.0000
- CV AUC: 0.9885 ± 0.0073 (StratifiedKFold(5))
- KMeans candidate_expression: 上下動・侵入寄り
- ラベル候補: 上下動型候補 / 守備回収型候補
- KMeans 解釈との整合性コメント: KMeans の「上下動・侵入寄り」候補と概ね整合します。RF でも HI距離_per_matchが高い、走行距離_per_matchが高い、PA進入_per90が低い が主な分離軸で、上下動・侵入寄り / 守備回収寄り の解釈が妥当です。
- permutation importance 上位5:
  - 1. HI距離_per_match (`z_hi_distance_full_all_per_match`) / center_z=+0.861 / permutation_importance_mean=0.1397 / std=0.0279
  - 2. 走行距離_per_match (`z_running_distance_full_all_per_match`) / center_z=+0.935 / permutation_importance_mean=0.0143 / std=0.0059
  - 3. PA進入_per90 (`z_pa_entry_per90`) / center_z=-0.237 / permutation_importance_mean=0.0037 / std=0.0014
  - 4. タックル奪取率 (`z_tackle_win_rate_pct`) / center_z=-0.205 / permutation_importance_mean=0.0008 / std=0.0007
  - 5. 前方向ロングパス成功率 (`z_forward_long_pass_success_rate_pct`) / center_z=+0.141 / permutation_importance_mean=0.0007 / std=0.0004
- impurity importance 上位5:
  - 1. HI距離_per_match (`z_hi_distance_full_all_per_match`) / center_z=+0.861 / impurity_importance=0.3672
  - 2. 走行距離_per_match (`z_running_distance_full_all_per_match`) / center_z=+0.935 / impurity_importance=0.2602
  - 3. スプリント回数_per_match (`z_sprint_count_full_all_per_match`) / center_z=+0.707 / impurity_importance=0.1383
  - 4. PA進入_per90 (`z_pa_entry_per90`) / center_z=-0.237 / impurity_importance=0.0653
  - 5. クロス数_per90 (`z_crosses_per90`) / center_z=-0.273 / impurity_importance=0.0534
- 推薦スコア候補: `z_hi_distance_full_all_per_match + z_running_distance_full_all_per_match` を主軸にしつつ、低値が効く z_pa_entry_per90 は補助条件として併用するのが自然です。

### Cluster 1
- positive / negative: 16 / 107
- train AUC: 1.0000
- CV AUC: 0.9802 ± 0.0323 (StratifiedKFold(5))
- KMeans candidate_expression: 守備回収寄り / 配球寄り
- ラベル候補: 守備回収型候補 / 攻撃参加型候補
- KMeans 解釈との整合性コメント: KMeans の「守備回収寄り / 配球寄り」候補と概ね整合します。RF でも ブロック_per90が高い、クロス成功率が低い、スプリント回数_per_matchが低い が主な分離軸で、守備回収寄り / クロス供給寄り の解釈が妥当です。
- permutation importance 上位5:
  - 1. ブロック_per90 (`z_blocks_per90`) / center_z=+0.850 / permutation_importance_mean=0.0011 / std=0.0009
  - 2. クロス成功率 (`z_cross_success_rate_pct`) / center_z=-1.217 / permutation_importance_mean=0.0007 / std=0.0004
  - 3. スプリント回数_per_match (`z_sprint_count_full_all_per_match`) / center_z=-1.512 / permutation_importance_mean=0.0005 / std=0.0014
  - 4. ロスト後5秒未満リゲイン_per90 (`z_regain_within_5s_per90`) / center_z=+1.164 / permutation_importance_mean=0.0001 / std=0.0003
  - 5. クロス数_per90 (`z_crosses_per90`) / center_z=-0.863 / permutation_importance_mean=0.0001 / std=0.0002
- impurity importance 上位5:
  - 1. スプリント回数_per_match (`z_sprint_count_full_all_per_match`) / center_z=-1.512 / impurity_importance=0.2641
  - 2. HI距離_per_match (`z_hi_distance_full_all_per_match`) / center_z=-1.488 / impurity_importance=0.2222
  - 3. 走行距離_per_match (`z_running_distance_full_all_per_match`) / center_z=-1.250 / impurity_importance=0.1186
  - 4. クロス成功率 (`z_cross_success_rate_pct`) / center_z=-1.217 / impurity_importance=0.0870
  - 5. クロス数_per90 (`z_crosses_per90`) / center_z=-0.863 / impurity_importance=0.0773
- 推薦スコア候補: `z_blocks_per90 + z_regain_within_5s_per90` を主軸にしつつ、低値が効く z_cross_success_rate_pct は補助条件として併用するのが自然です。

### Cluster 2
- positive / negative: 47 / 76
- train AUC: 1.0000
- CV AUC: 0.9583 ± 0.0441 (StratifiedKFold(5))
- KMeans candidate_expression: クロス供給寄り
- ラベル候補: 平均型候補
- KMeans 解釈との整合性コメント: KMeans の平均型候補と整合します。RF では HI距離_per_matchが低い、走行距離_per_matchが低い、ブロック_per90が低い が上位ですが、いずれも specialized cluster 側の極端さを弾く軸として効いており、単一ラベルより『平均型候補』として扱う方が自然です。
- permutation importance 上位5:
  - 1. HI距離_per_match (`z_hi_distance_full_all_per_match`) / center_z=-0.450 / permutation_importance_mean=0.1214 / std=0.0219
  - 2. 走行距離_per_match (`z_running_distance_full_all_per_match`) / center_z=-0.527 / permutation_importance_mean=0.0088 / std=0.0049
  - 3. ブロック_per90 (`z_blocks_per90`) / center_z=-0.343 / permutation_importance_mean=0.0069 / std=0.0026
  - 4. 前方向ロングパス成功率 (`z_forward_long_pass_success_rate_pct`) / center_z=-0.235 / permutation_importance_mean=0.0011 / std=0.0006
  - 5. PA進入_per90 (`z_pa_entry_per90`) / center_z=-0.067 / permutation_importance_mean=0.0007 / std=0.0002
- impurity importance 上位5:
  - 1. HI距離_per_match (`z_hi_distance_full_all_per_match`) / center_z=-0.450 / impurity_importance=0.2926
  - 2. 走行距離_per_match (`z_running_distance_full_all_per_match`) / center_z=-0.527 / impurity_importance=0.2062
  - 3. スプリント回数_per_match (`z_sprint_count_full_all_per_match`) / center_z=-0.364 / impurity_importance=0.1333
  - 4. ブロック_per90 (`z_blocks_per90`) / center_z=-0.343 / impurity_importance=0.0929
  - 5. ロスト後5秒未満リゲイン_per90 (`z_regain_within_5s_per90`) / center_z=-0.296 / impurity_importance=0.0687
- 推薦スコア候補: 平均型候補は 2〜3 変数の単純加算より、`SB_cluster_centers_z.csv` の cluster 2 中心への距離ベースが適切です。

### Cluster 3
- positive / negative: 16 / 107
- train AUC: 1.0000
- CV AUC: 0.9929 ± 0.0143 (StratifiedKFold(5))
- KMeans candidate_expression: 上下動・侵入寄り / クロス供給寄り
- ラベル候補: 上下動型候補 / 守備回収型候補
- KMeans 解釈との整合性コメント: KMeans の「上下動・侵入寄り / クロス供給寄り」候補と概ね整合します。RF でも PA進入_per90が高い、タックル奪取率が高い、クロス数_per90が高い が主な分離軸で、上下動・侵入寄り / 守備回収寄り の解釈が妥当です。
- permutation importance 上位5:
  - 1. PA進入_per90 (`z_pa_entry_per90`) / center_z=+1.522 / permutation_importance_mean=0.0377 / std=0.0129
  - 2. タックル奪取率 (`z_tackle_win_rate_pct`) / center_z=+0.908 / permutation_importance_mean=0.0041 / std=0.0033
  - 3. クロス数_per90 (`z_crosses_per90`) / center_z=+1.514 / permutation_importance_mean=0.0023 / std=0.0013
  - 4. クロス成功率 (`z_cross_success_rate_pct`) / center_z=+0.619 / permutation_importance_mean=0.0000 / std=0.0000
  - 5. ロスト後5秒未満リゲイン_per90 (`z_regain_within_5s_per90`) / center_z=-0.315 / permutation_importance_mean=0.0000 / std=0.0000
- impurity importance 上位5:
  - 1. PA進入_per90 (`z_pa_entry_per90`) / center_z=+1.522 / impurity_importance=0.3505
  - 2. クロス数_per90 (`z_crosses_per90`) / center_z=+1.514 / impurity_importance=0.2417
  - 3. タックル奪取率 (`z_tackle_win_rate_pct`) / center_z=+0.908 / impurity_importance=0.1745
  - 4. クロス成功率 (`z_cross_success_rate_pct`) / center_z=+0.619 / impurity_importance=0.0652
  - 5. ロスト後5秒未満リゲイン_per90 (`z_regain_within_5s_per90`) / center_z=-0.315 / impurity_importance=0.0422
- 推薦スコア候補: `z_pa_entry_per90 + z_tackle_win_rate_pct` を主軸にしつつ、低値が効く z_regain_within_5s_per90 は補助条件として併用するのが自然です。

## 全体所見
- 平均型候補は Cluster 2 です。他クラスタとの分岐で目立った変数は z_hi_distance_full_all_per_match, z_running_distance_full_all_per_match, z_blocks_per90 でした。
- Cluster 0 の specialized な分離軸は z_hi_distance_full_all_per_match, z_running_distance_full_all_per_match, z_pa_entry_per90 でした。
- Cluster 1 の specialized な分離軸は z_blocks_per90, z_cross_success_rate_pct, z_sprint_count_full_all_per_match でした。
- Cluster 3 の specialized な分離軸は z_pa_entry_per90, z_tackle_win_rate_pct, z_crosses_per90 でした。
- ラベル解釈は断定ではなく候補です。KMeans 中心の高低と RF の判別寄与が同時に揃う変数を優先して読んでいます。

## 推薦スコア設計メモ
- Cluster 0: `z_hi_distance_full_all_per_match + z_running_distance_full_all_per_match` を主候補。
- Cluster 1: `z_blocks_per90 + z_regain_within_5s_per90` を主候補。
- Cluster 2: 平均型候補のため、単純加算ではなくクラスタ中心への距離ベース推奨。
- Cluster 3: `z_pa_entry_per90 + z_tackle_win_rate_pct` を主候補。

## CV 安定性メモ
- 今回は全 cluster で 5-fold CV が実行でき、極端に不安定な cluster はありませんでした。
