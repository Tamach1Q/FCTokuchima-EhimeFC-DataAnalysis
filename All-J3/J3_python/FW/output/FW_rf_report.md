# FW RandomForest Report

## 入力ファイル
- `/Users/machidanoboruyuu/Desktop/FCTokushima-EhimeFC-DataAnalysis/All-J3/J3_python/FW/output/FW_clustered_players.csv`
- `/Users/machidanoboruyuu/Desktop/FCTokushima-EhimeFC-DataAnalysis/All-J3/J3_python/FW/output/FW_cluster_centers_z.csv`
- `/Users/machidanoboruyuu/Desktop/FCTokushima-EhimeFC-DataAnalysis/All-J3/J3_python/FW/output/FW_cluster_summary.csv`
- `/Users/machidanoboruyuu/Desktop/FCTokushima-EhimeFC-DataAnalysis/All-J3/J3_python/FW/output/FW_kmeans_report.md`

## 使用した z 列
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

## データ概要
- サンプル数: 117
- cluster_id 一覧: 0, 1, 2, 3
- cluster ごとの positive / negative 件数:
  - Cluster 0: 82 / 35
  - Cluster 1: 2 / 115
  - Cluster 2: 16 / 101
  - Cluster 3: 17 / 100

## RandomForest 設定
- `RandomForestClassifier(n_estimators=1000, random_state=42, class_weight="balanced", min_samples_leaf=2, max_depth=None, n_jobs=-1)`
- one-vs-rest で各 cluster を個別に二値分類
- permutation importance: scoring=`roc_auc`, `n_repeats=30`, `random_state=42`
- 評価指標: train ROC AUC, StratifiedKFold ROC AUC
- 注記: 今回の主目的は予測精度の最適化ではなく、各クラスタを説明する変数の解釈です。

## Cluster 別結果
### Cluster 0
- positive / negative: 82 / 35
- train AUC: 1.0000
- CV AUC: 0.9655 ± 0.0220 (StratifiedKFold(5))
- KMeans candidate_expression: 前線守備・回収寄り
- ラベル候補: 平均型候補
- KMeans 解釈との整合性コメント: KMeans の平均型候補と整合します。RF では 前進パス成功数_per90が低い、攻撃3rd奪回_per90が低い、ラストパス_per90が低い が上位ですが、いずれも specialized cluster 側の極端さを弾く軸として効いており、単一ラベルより『平均型候補』として扱う方が自然です。
- permutation importance 上位5:
  - 1. 前進パス成功数_per90 (`z_successful_forward_passes_per90`) / center_z=-0.423 / permutation_importance_mean=0.0607 / std=0.0167
  - 2. 攻撃3rd奪回_per90 (`z_attacking_third_gains_per90`) / center_z=-0.328 / permutation_importance_mean=0.0120 / std=0.0052
  - 3. ラストパス_per90 (`z_last_passes_per90`) / center_z=-0.298 / permutation_importance_mean=0.0013 / std=0.0009
  - 4. ボックス外シュート_per90 (`z_out_box_shots_per90`) / center_z=-0.149 / permutation_importance_mean=0.0002 / std=0.0003
  - 5. 枠内率 (`z_shot_on_target_rate_pct`) / center_z=-0.112 / permutation_importance_mean=0.0001 / std=0.0001
- impurity importance 上位5:
  - 1. 前進パス成功数_per90 (`z_successful_forward_passes_per90`) / center_z=-0.423 / impurity_importance=0.3100
  - 2. 攻撃3rd奪回_per90 (`z_attacking_third_gains_per90`) / center_z=-0.328 / impurity_importance=0.2090
  - 3. ラストパス_per90 (`z_last_passes_per90`) / center_z=-0.298 / impurity_importance=0.1420
  - 4. 得点_per90 (`z_goals_per90`) / center_z=-0.005 / impurity_importance=0.0666
  - 5. ボックス内シュート_per90 (`z_box_shots_per90`) / center_z=+0.043 / impurity_importance=0.0576
- 推薦スコア候補: 平均型候補は 2〜3 変数の単純加算より、`FW_cluster_centers_z.csv` の cluster 0 中心への距離ベースが適切です。

### Cluster 1
- positive / negative: 2 / 115
- train AUC: 1.0000
- CV AUC: 1.0000 ± 0.0000 (StratifiedKFold(2))
- KMeans candidate_expression: フィニッシュ寄り / 空中戦・前進関与寄り
- ラベル候補: フィニッシュ型候補
- KMeans 解釈との整合性コメント: KMeans の「フィニッシュ寄り / 空中戦・前進関与寄り」候補と概ね整合します。RF でも 決定率が高い、得点_per90が高い、枠内率が高い が主な分離軸で、フィニッシュ寄り の解釈が妥当です。
- permutation importance 上位5:
  - 1. 決定率 (`z_shot_conversion_rate_pct`) / center_z=+4.727 / permutation_importance_mean=0.0000 / std=0.0000
  - 2. 得点_per90 (`z_goals_per90`) / center_z=+3.206 / permutation_importance_mean=0.0000 / std=0.0000
  - 3. 枠内率 (`z_shot_on_target_rate_pct`) / center_z=+4.074 / permutation_importance_mean=0.0000 / std=0.0000
  - 4. スプリント回数_per_match (`z_sprint_count_full_all_per_match`) / center_z=-1.230 / permutation_importance_mean=0.0000 / std=0.0000
  - 5. ラストパス_per90 (`z_last_passes_per90`) / center_z=+0.987 / permutation_importance_mean=0.0000 / std=0.0000
- impurity importance 上位5:
  - 1. 決定率 (`z_shot_conversion_rate_pct`) / center_z=+4.727 / impurity_importance=0.2465
  - 2. 得点_per90 (`z_goals_per90`) / center_z=+3.206 / impurity_importance=0.2442
  - 3. 枠内率 (`z_shot_on_target_rate_pct`) / center_z=+4.074 / impurity_importance=0.1859
  - 4. ボックス外シュート_per90 (`z_out_box_shots_per90`) / center_z=-1.817 / impurity_importance=0.1152
  - 5. スプリント回数_per_match (`z_sprint_count_full_all_per_match`) / center_z=-1.230 / impurity_importance=0.0690
- 推薦スコア候補: `z_shot_conversion_rate_pct + z_goals_per90` を主軸にしつつ、低値が効く z_sprint_count_full_all_per_match は補助条件として併用するのが自然です。

### Cluster 2
- positive / negative: 16 / 101
- train AUC: 1.0000
- CV AUC: 0.9633 ± 0.0618 (StratifiedKFold(5))
- KMeans candidate_expression: 空中戦・前進関与寄り / ミドルレンジ関与寄り
- ラベル候補: 空中戦・前進関与型候補 / ミドルレンジ関与型候補
- KMeans 解釈との整合性コメント: KMeans の「空中戦・前進関与寄り / ミドルレンジ関与寄り」候補と概ね整合します。RF でも ラストパス_per90が高い、ボックス内シュート_per90が高い、空中戦勝利数_per90が高い が主な分離軸で、空中戦・前進関与寄り / ミドルレンジ関与寄り の解釈が妥当です。
- permutation importance 上位5:
  - 1. ラストパス_per90 (`z_last_passes_per90`) / center_z=+1.450 / permutation_importance_mean=0.0326 / std=0.0131
  - 2. ボックス内シュート_per90 (`z_box_shots_per90`) / center_z=+1.084 / permutation_importance_mean=0.0034 / std=0.0030
  - 3. 空中戦勝利数_per90 (`z_aerial_wins_per90`) / center_z=+1.041 / permutation_importance_mean=0.0007 / std=0.0008
  - 4. 攻撃3rd奪回_per90 (`z_attacking_third_gains_per90`) / center_z=+0.727 / permutation_importance_mean=0.0006 / std=0.0006
  - 5. ボックス外シュート_per90 (`z_out_box_shots_per90`) / center_z=+0.987 / permutation_importance_mean=0.0003 / std=0.0004
- impurity importance 上位5:
  - 1. ラストパス_per90 (`z_last_passes_per90`) / center_z=+1.450 / impurity_importance=0.3269
  - 2. ボックス内シュート_per90 (`z_box_shots_per90`) / center_z=+1.084 / impurity_importance=0.1596
  - 3. 空中戦勝利数_per90 (`z_aerial_wins_per90`) / center_z=+1.041 / impurity_importance=0.1148
  - 4. 前進パス成功数_per90 (`z_successful_forward_passes_per90`) / center_z=+0.743 / impurity_importance=0.1070
  - 5. ボックス外シュート_per90 (`z_out_box_shots_per90`) / center_z=+0.987 / impurity_importance=0.0736
- 推薦スコア候補: `z_last_passes_per90 + z_box_shots_per90` の z 合算が自然です。

### Cluster 3
- positive / negative: 17 / 100
- train AUC: 1.0000
- CV AUC: 0.9900 ± 0.0200 (StratifiedKFold(5))
- KMeans candidate_expression: 空中戦・前進関与寄り / 前線守備・回収寄り
- ラベル候補: フィニッシュ型候補 / 空中戦・前進関与型候補
- KMeans 解釈との整合性コメント: KMeans の「空中戦・前進関与寄り / 前線守備・回収寄り」候補と概ね整合します。RF でも ボックス内シュート_per90が低い、前進パス成功数_per90が高い、攻撃3rd奪回_per90が高い が主な分離軸で、フィニッシュ寄り / 空中戦・前進関与寄り の解釈が妥当です。
- permutation importance 上位5:
  - 1. ボックス内シュート_per90 (`z_box_shots_per90`) / center_z=-1.258 / permutation_importance_mean=0.0152 / std=0.0071
  - 2. 前進パス成功数_per90 (`z_successful_forward_passes_per90`) / center_z=+1.336 / permutation_importance_mean=0.0095 / std=0.0046
  - 3. 攻撃3rd奪回_per90 (`z_attacking_third_gains_per90`) / center_z=+0.985 / permutation_importance_mean=0.0023 / std=0.0019
  - 4. 得点_per90 (`z_goals_per90`) / center_z=-1.024 / permutation_importance_mean=0.0003 / std=0.0004
  - 5. 空中戦勝利数_per90 (`z_aerial_wins_per90`) / center_z=-0.676 / permutation_importance_mean=0.0000 / std=0.0000
- impurity importance 上位5:
  - 1. ボックス内シュート_per90 (`z_box_shots_per90`) / center_z=-1.258 / impurity_importance=0.2881
  - 2. 前進パス成功数_per90 (`z_successful_forward_passes_per90`) / center_z=+1.336 / impurity_importance=0.1883
  - 3. 得点_per90 (`z_goals_per90`) / center_z=-1.024 / impurity_importance=0.1760
  - 4. 攻撃3rd奪回_per90 (`z_attacking_third_gains_per90`) / center_z=+0.985 / impurity_importance=0.1096
  - 5. 空中戦勝利数_per90 (`z_aerial_wins_per90`) / center_z=-0.676 / impurity_importance=0.0841
- 推薦スコア候補: `z_successful_forward_passes_per90 + z_attacking_third_gains_per90` を主軸にしつつ、低値が効く z_box_shots_per90 は補助条件として併用するのが自然です。

## 全体所見
- 平均型候補は Cluster 0 です。他クラスタとの分岐で目立った変数は z_successful_forward_passes_per90, z_attacking_third_gains_per90, z_last_passes_per90 でした。
- Cluster 1 の specialized な分離軸は z_shot_conversion_rate_pct, z_goals_per90, z_shot_on_target_rate_pct でした。
- Cluster 2 の specialized な分離軸は z_last_passes_per90, z_box_shots_per90, z_aerial_wins_per90 でした。
- Cluster 3 の specialized な分離軸は z_box_shots_per90, z_successful_forward_passes_per90, z_attacking_third_gains_per90 でした。
- ラベル解釈は断定ではなく候補です。KMeans 中心の高低と RF の判別寄与が同時に揃う変数を優先して読んでいます。

## 推薦スコア設計メモ
- Cluster 0: 平均型候補のため、単純加算ではなくクラスタ中心への距離ベース推奨。
- Cluster 1: `z_shot_conversion_rate_pct + z_goals_per90` を主候補。
- Cluster 2: `z_last_passes_per90 + z_box_shots_per90` を主候補。
- Cluster 3: `z_successful_forward_passes_per90 + z_attacking_third_gains_per90` を主候補。

## CV 安定性メモ
- 変動がやや大きかった cluster: 2
