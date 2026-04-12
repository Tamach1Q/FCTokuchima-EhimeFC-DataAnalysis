# SH RandomForest Report

## 入力ファイル
- `/Users/machidanoboruyuu/Desktop/FCTokushima-EhimeFC-DataAnalysis/All-J3/J3_python/SH/output/SH_clustered_players.csv`
- `/Users/machidanoboruyuu/Desktop/FCTokushima-EhimeFC-DataAnalysis/All-J3/J3_python/SH/output/SH_cluster_centers_z.csv`
- `/Users/machidanoboruyuu/Desktop/FCTokushima-EhimeFC-DataAnalysis/All-J3/J3_python/SH/output/SH_cluster_summary.csv`
- `/Users/machidanoboruyuu/Desktop/FCTokushima-EhimeFC-DataAnalysis/All-J3/J3_python/SH/output/SH_kmeans_report.md`

## 使用した z 列
- `z_sprint_distance_full_all_per_match` (スプリント距離_per_match)
- `z_hsr_count_full_all_per_match` (HSR回数_per_match)
- `z_dribble_success_rate_pct` (ドリブル成功率)
- `z_crosses_per90` (クロス数_per90)
- `z_cross_success_rate_pct` (クロス成功率)
- `z_last_passes_per90` (ラストパス_per90)
- `z_pa_entry_per90` (PA進入_per90)
- `z_shot_conversion_rate_pct` (決定率)
- `z_regain_within_5s_per90` (ロスト後5秒未満リゲイン_per90)

## データ概要
- サンプル数: 215
- cluster_id 一覧: 0, 1, 2, 3
- cluster ごとの positive / negative 件数:
  - Cluster 0: 65 / 150
  - Cluster 1: 34 / 181
  - Cluster 2: 5 / 210
  - Cluster 3: 111 / 104

## RandomForest 設定
- `RandomForestClassifier(n_estimators=1000, random_state=42, class_weight="balanced", min_samples_leaf=2, max_depth=None, n_jobs=-1)`
- one-vs-rest で各 cluster を個別に二値分類
- permutation importance: scoring=`roc_auc`, `n_repeats=30`, `random_state=42`
- 評価指標: train ROC AUC, StratifiedKFold ROC AUC
- 注記: 今回の主目的は予測精度の最適化ではなく、各クラスタを説明する変数の解釈です。

## Cluster 別結果
### Cluster 0
- positive / negative: 65 / 150
- train AUC: 1.0000
- CV AUC: 0.9908 ± 0.0087 (StratifiedKFold(5))
- KMeans candidate_expression: 縦突破寄り / 守備回収寄り
- ラベル候補: 縦突破型候補 / 守備回収型候補
- KMeans 解釈との整合性コメント: KMeans の「縦突破寄り / 守備回収寄り」候補と概ね整合します。RF でも スプリント距離_per_matchが高い、HSR回数_per_matchが高い、PA進入_per90が高い が主な分離軸で、縦突破寄り / 守備回収寄り の解釈が妥当です。
- permutation importance 上位5:
  - 1. スプリント距離_per_match (`z_sprint_distance_full_all_per_match`) / center_z=+1.172 / permutation_importance_mean=0.1627 / std=0.0194
  - 2. HSR回数_per_match (`z_hsr_count_full_all_per_match`) / center_z=+1.075 / permutation_importance_mean=0.0619 / std=0.0124
  - 3. PA進入_per90 (`z_pa_entry_per90`) / center_z=+0.279 / permutation_importance_mean=0.0015 / std=0.0006
  - 4. ドリブル成功率 (`z_dribble_success_rate_pct`) / center_z=+0.287 / permutation_importance_mean=0.0010 / std=0.0005
  - 5. ラストパス_per90 (`z_last_passes_per90`) / center_z=+0.157 / permutation_importance_mean=0.0002 / std=0.0002
- impurity importance 上位5:
  - 1. スプリント距離_per_match (`z_sprint_distance_full_all_per_match`) / center_z=+1.172 / impurity_importance=0.4704
  - 2. HSR回数_per_match (`z_hsr_count_full_all_per_match`) / center_z=+1.075 / impurity_importance=0.3407
  - 3. PA進入_per90 (`z_pa_entry_per90`) / center_z=+0.279 / impurity_importance=0.0415
  - 4. ラストパス_per90 (`z_last_passes_per90`) / center_z=+0.157 / impurity_importance=0.0406
  - 5. クロス数_per90 (`z_crosses_per90`) / center_z=+0.253 / impurity_importance=0.0360
- 推薦スコア候補: `z_sprint_distance_full_all_per_match + z_hsr_count_full_all_per_match` の z 合算が自然です。

### Cluster 1
- positive / negative: 34 / 181
- train AUC: 1.0000
- CV AUC: 0.9871 ± 0.0121 (StratifiedKFold(5))
- KMeans candidate_expression: 守備回収寄り / クロス供給寄り
- ラベル候補: 守備回収型候補 / 縦突破型候補
- KMeans 解釈との整合性コメント: KMeans の「守備回収寄り / クロス供給寄り」候補と概ね整合します。RF でも ロスト後5秒未満リゲイン_per90が高い、ドリブル成功率が低い、スプリント距離_per_matchが低い が主な分離軸で、守備回収寄り / 縦突破寄り の解釈が妥当です。
- permutation importance 上位5:
  - 1. ロスト後5秒未満リゲイン_per90 (`z_regain_within_5s_per90`) / center_z=+1.457 / permutation_importance_mean=0.0718 / std=0.0123
  - 2. ドリブル成功率 (`z_dribble_success_rate_pct`) / center_z=-1.380 / permutation_importance_mean=0.0294 / std=0.0067
  - 3. スプリント距離_per_match (`z_sprint_distance_full_all_per_match`) / center_z=-0.752 / permutation_importance_mean=0.0005 / std=0.0005
  - 4. PA進入_per90 (`z_pa_entry_per90`) / center_z=-0.675 / permutation_importance_mean=0.0000 / std=0.0000
  - 5. クロス数_per90 (`z_crosses_per90`) / center_z=-0.682 / permutation_importance_mean=0.0000 / std=0.0000
- impurity importance 上位5:
  - 1. ロスト後5秒未満リゲイン_per90 (`z_regain_within_5s_per90`) / center_z=+1.457 / impurity_importance=0.3501
  - 2. ドリブル成功率 (`z_dribble_success_rate_pct`) / center_z=-1.380 / impurity_importance=0.2327
  - 3. クロス数_per90 (`z_crosses_per90`) / center_z=-0.682 / impurity_importance=0.1200
  - 4. PA進入_per90 (`z_pa_entry_per90`) / center_z=-0.675 / impurity_importance=0.1129
  - 5. スプリント距離_per_match (`z_sprint_distance_full_all_per_match`) / center_z=-0.752 / impurity_importance=0.0545
- 推薦スコア候補: `z_regain_within_5s_per90 + z_cross_success_rate_pct` を主軸にしつつ、低値が効く z_dribble_success_rate_pct は補助条件として併用するのが自然です。

### Cluster 2
- positive / negative: 5 / 210
- train AUC: 1.0000
- CV AUC: 1.0000 ± 0.0000 (StratifiedKFold(5))
- KMeans candidate_expression: フィニッシュ関与寄り / 縦突破寄り
- ラベル候補: クロス供給型候補 / 縦突破型候補
- KMeans 解釈との整合性コメント: KMeans の「フィニッシュ関与寄り / 縦突破寄り」候補と概ね整合します。RF でも クロス数_per90が高い、PA進入_per90が高い、ドリブル成功率が高い が主な分離軸で、クロス供給寄り / 縦突破寄り の解釈が妥当です。
- permutation importance 上位5:
  - 1. クロス数_per90 (`z_crosses_per90`) / center_z=+4.367 / permutation_importance_mean=0.0005 / std=0.0013
  - 2. PA進入_per90 (`z_pa_entry_per90`) / center_z=+4.392 / permutation_importance_mean=0.0002 / std=0.0009
  - 3. ドリブル成功率 (`z_dribble_success_rate_pct`) / center_z=+0.797 / permutation_importance_mean=0.0000 / std=0.0000
  - 4. スプリント距離_per_match (`z_sprint_distance_full_all_per_match`) / center_z=-0.842 / permutation_importance_mean=0.0000 / std=0.0000
  - 5. ラストパス_per90 (`z_last_passes_per90`) / center_z=+1.919 / permutation_importance_mean=0.0000 / std=0.0000
- impurity importance 上位5:
  - 1. PA進入_per90 (`z_pa_entry_per90`) / center_z=+4.392 / impurity_importance=0.3383
  - 2. クロス数_per90 (`z_crosses_per90`) / center_z=+4.367 / impurity_importance=0.3357
  - 3. ラストパス_per90 (`z_last_passes_per90`) / center_z=+1.919 / impurity_importance=0.1241
  - 4. HSR回数_per_match (`z_hsr_count_full_all_per_match`) / center_z=-1.289 / impurity_importance=0.0780
  - 5. ロスト後5秒未満リゲイン_per90 (`z_regain_within_5s_per90`) / center_z=-0.573 / impurity_importance=0.0447
- 推薦スコア候補: `z_crosses_per90 + z_pa_entry_per90` を主軸にしつつ、低値が効く z_sprint_distance_full_all_per_match は補助条件として併用するのが自然です。

### Cluster 3
- positive / negative: 111 / 104
- train AUC: 1.0000
- CV AUC: 0.9779 ± 0.0093 (StratifiedKFold(5))
- KMeans candidate_expression: 縦突破寄り
- ラベル候補: 平均型候補
- KMeans 解釈との整合性コメント: KMeans の平均型候補と整合します。RF では スプリント距離_per_matchが低い、HSR回数_per_matchが低い、ロスト後5秒未満リゲイン_per90が低い が上位ですが、いずれも specialized cluster 側の極端さを弾く軸として効いており、単一ラベルより『平均型候補』として扱う方が自然です。
- permutation importance 上位5:
  - 1. スプリント距離_per_match (`z_sprint_distance_full_all_per_match`) / center_z=-0.418 / permutation_importance_mean=0.0858 / std=0.0118
  - 2. HSR回数_per_match (`z_hsr_count_full_all_per_match`) / center_z=-0.395 / permutation_importance_mean=0.0747 / std=0.0144
  - 3. ロスト後5秒未満リゲイン_per90 (`z_regain_within_5s_per90`) / center_z=-0.267 / permutation_importance_mean=0.0349 / std=0.0045
  - 4. ドリブル成功率 (`z_dribble_success_rate_pct`) / center_z=+0.218 / permutation_importance_mean=0.0088 / std=0.0017
  - 5. PA進入_per90 (`z_pa_entry_per90`) / center_z=-0.155 / permutation_importance_mean=0.0032 / std=0.0008
- impurity importance 上位5:
  - 1. HSR回数_per_match (`z_hsr_count_full_all_per_match`) / center_z=-0.395 / impurity_importance=0.2675
  - 2. スプリント距離_per_match (`z_sprint_distance_full_all_per_match`) / center_z=-0.418 / impurity_importance=0.2385
  - 3. ロスト後5秒未満リゲイン_per90 (`z_regain_within_5s_per90`) / center_z=-0.267 / impurity_importance=0.1420
  - 4. ドリブル成功率 (`z_dribble_success_rate_pct`) / center_z=+0.218 / impurity_importance=0.0986
  - 5. PA進入_per90 (`z_pa_entry_per90`) / center_z=-0.155 / impurity_importance=0.0835
- 推薦スコア候補: 平均型候補は 2〜3 変数の単純加算より、`SH_cluster_centers_z.csv` の cluster 3 中心への距離ベースが適切です。

## 全体所見
- 平均型候補は Cluster 3 です。他クラスタとの分岐で目立った変数は z_sprint_distance_full_all_per_match, z_hsr_count_full_all_per_match, z_regain_within_5s_per90 でした。
- Cluster 0 の specialized な分離軸は z_sprint_distance_full_all_per_match, z_hsr_count_full_all_per_match, z_pa_entry_per90 でした。
- Cluster 1 の specialized な分離軸は z_regain_within_5s_per90, z_dribble_success_rate_pct, z_sprint_distance_full_all_per_match でした。
- Cluster 2 の specialized な分離軸は z_crosses_per90, z_pa_entry_per90, z_dribble_success_rate_pct でした。
- ラベル解釈は断定ではなく候補です。KMeans 中心の高低と RF の判別寄与が同時に揃う変数を優先して読んでいます。

## 推薦スコア設計メモ
- Cluster 0: `z_sprint_distance_full_all_per_match + z_hsr_count_full_all_per_match` を主候補。
- Cluster 1: `z_regain_within_5s_per90 + z_cross_success_rate_pct` を主候補。
- Cluster 2: `z_crosses_per90 + z_pa_entry_per90` を主候補。
- Cluster 3: 平均型候補のため、単純加算ではなくクラスタ中心への距離ベース推奨。

## CV 安定性メモ
- 今回は全 cluster で 5-fold CV が実行でき、極端に不安定な cluster はありませんでした。
