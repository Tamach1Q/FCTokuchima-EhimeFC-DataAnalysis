# CB RandomForest Report

## 入力ファイル
- `/Users/machidanoboruyuu/Desktop/FCTokushima-EhimeFC-DataAnalysis/All-J3/J3_python/CB/output/CB_clustered_players.csv`
- `/Users/machidanoboruyuu/Desktop/FCTokushima-EhimeFC-DataAnalysis/All-J3/J3_python/CB/output/CB_cluster_centers_z.csv`
- `/Users/machidanoboruyuu/Desktop/FCTokushima-EhimeFC-DataAnalysis/All-J3/J3_python/CB/output/CB_cluster_summary.csv`
- `/Users/machidanoboruyuu/Desktop/FCTokushima-EhimeFC-DataAnalysis/All-J3/J3_python/CB/output/CB_kmeans_report.md`

## 使用した z 列
- `z_aerial_duel_win_rate_pct` (空中戦勝率)
- `z_tackle_win_rate_pct` (タックル奪取率)
- `z_interceptions_per90` (インターセプト_per90)
- `z_blocks_per90` (ブロック_per90)
- `z_clearances_per90` (クリア_per90)
- `z_pass_success_rate_pct` (パス成功率)
- `z_successful_forward_passes_per90` (前進パス成功数_per90)
- `z_successful_long_passes_per90` (ロングパス成功数_per90)
- `z_medaccel_count_full_all_per_match` (中加速回数_per_match)
- `z_highaccel_count_full_all_per_match` (高加速回数_per_match)

## データ概要
- サンプル数: 149
- cluster_id 一覧: 0, 1, 2, 3
- cluster ごとの positive / negative 件数:
  - Cluster 0: 29 / 120
  - Cluster 1: 40 / 109
  - Cluster 2: 9 / 140
  - Cluster 3: 71 / 78

## RandomForest 設定
- `RandomForestClassifier(n_estimators=1000, random_state=42, class_weight="balanced", min_samples_leaf=2, max_depth=None, n_jobs=-1)`
- one-vs-rest で各 cluster を個別に二値分類
- permutation importance: scoring=`roc_auc`, `n_repeats=30`, `random_state=42`
- 評価指標: train ROC AUC, StratifiedKFold ROC AUC
- 注記: 今回の主目的は予測精度の最適化ではなく、各クラスタを説明する変数の解釈です。

## Cluster 別結果
### Cluster 0
- positive / negative: 29 / 120
- train AUC: 1.0000
- CV AUC: 0.9861 ± 0.0158 (StratifiedKFold(5))
- KMeans candidate_expression: 配球寄り
- ラベル候補: 配球型候補 / 危険除去型候補
- KMeans 解釈との整合性コメント: KMeans の「配球寄り」候補と概ね整合します。RF でも 前進パス成功数_per90が高い、パス成功率が高い、ロングパス成功数_per90が高い が主な分離軸で、配球寄り / 危険除去寄り の解釈が妥当です。
- permutation importance 上位5:
  - 1. 前進パス成功数_per90 (`z_successful_forward_passes_per90`) / center_z=+1.315 / permutation_importance_mean=0.0283 / std=0.0072
  - 2. パス成功率 (`z_pass_success_rate_pct`) / center_z=+0.930 / permutation_importance_mean=0.0069 / std=0.0041
  - 3. ロングパス成功数_per90 (`z_successful_long_passes_per90`) / center_z=+1.076 / permutation_importance_mean=0.0045 / std=0.0026
  - 4. クリア_per90 (`z_clearances_per90`) / center_z=-0.556 / permutation_importance_mean=0.0010 / std=0.0008
  - 5. ブロック_per90 (`z_blocks_per90`) / center_z=-0.493 / permutation_importance_mean=0.0000 / std=0.0000
- impurity importance 上位5:
  - 1. 前進パス成功数_per90 (`z_successful_forward_passes_per90`) / center_z=+1.315 / impurity_importance=0.3193
  - 2. パス成功率 (`z_pass_success_rate_pct`) / center_z=+0.930 / impurity_importance=0.2220
  - 3. ロングパス成功数_per90 (`z_successful_long_passes_per90`) / center_z=+1.076 / impurity_importance=0.1963
  - 4. クリア_per90 (`z_clearances_per90`) / center_z=-0.556 / impurity_importance=0.0746
  - 5. ブロック_per90 (`z_blocks_per90`) / center_z=-0.493 / impurity_importance=0.0723
- 推薦スコア候補: `z_successful_forward_passes_per90 + z_pass_success_rate_pct` を主軸にしつつ、低値が効く z_clearances_per90 は補助条件として併用するのが自然です。

### Cluster 1
- positive / negative: 40 / 109
- train AUC: 1.0000
- CV AUC: 0.9760 ± 0.0173 (StratifiedKFold(5))
- KMeans candidate_expression: 危険除去寄り / 対人・空中戦寄り
- ラベル候補: 上下動型候補 / 配球型候補
- KMeans 解釈との整合性コメント: KMeans の「危険除去寄り / 対人・空中戦寄り」候補とは部分的に整合します。RF では 中加速回数_per_matchが低い、高加速回数_per_matchが低い、パス成功率が低い の寄与が大きく、機動力寄り / 配球寄り の軸で見た方が説明しやすいです。
- permutation importance 上位5:
  - 1. 中加速回数_per_match (`z_medaccel_count_full_all_per_match`) / center_z=-1.151 / permutation_importance_mean=0.0938 / std=0.0150
  - 2. 高加速回数_per_match (`z_highaccel_count_full_all_per_match`) / center_z=-0.933 / permutation_importance_mean=0.0127 / std=0.0053
  - 3. パス成功率 (`z_pass_success_rate_pct`) / center_z=-0.505 / permutation_importance_mean=0.0011 / std=0.0008
  - 4. 前進パス成功数_per90 (`z_successful_forward_passes_per90`) / center_z=-0.545 / permutation_importance_mean=0.0005 / std=0.0005
  - 5. インターセプト_per90 (`z_interceptions_per90`) / center_z=-0.472 / permutation_importance_mean=0.0002 / std=0.0002
- impurity importance 上位5:
  - 1. 中加速回数_per_match (`z_medaccel_count_full_all_per_match`) / center_z=-1.151 / impurity_importance=0.3438
  - 2. 高加速回数_per_match (`z_highaccel_count_full_all_per_match`) / center_z=-0.933 / impurity_importance=0.2433
  - 3. 前進パス成功数_per90 (`z_successful_forward_passes_per90`) / center_z=-0.545 / impurity_importance=0.1009
  - 4. パス成功率 (`z_pass_success_rate_pct`) / center_z=-0.505 / impurity_importance=0.0808
  - 5. クリア_per90 (`z_clearances_per90`) / center_z=+0.444 / impurity_importance=0.0553
- 推薦スコア候補: `z_aerial_duel_win_rate_pct + z_clearances_per90` を主軸にしつつ、低値が効く z_medaccel_count_full_all_per_match は補助条件として併用するのが自然です。

### Cluster 2
- positive / negative: 9 / 140
- train AUC: 1.0000
- CV AUC: 0.9321 ± 0.0833 (StratifiedKFold(5))
- KMeans candidate_expression: 危険除去寄り / 対人・空中戦寄り
- ラベル候補: 危険除去型候補 / 対人迎撃型候補
- KMeans 解釈との整合性コメント: KMeans の「危険除去寄り / 対人・空中戦寄り」候補と概ね整合します。RF でも クリア_per90が低い、空中戦勝率が低い、パス成功率が低い が主な分離軸で、危険除去寄り / 対人・空中戦寄り の解釈が妥当です。
- permutation importance 上位5:
  - 1. クリア_per90 (`z_clearances_per90`) / center_z=-1.353 / permutation_importance_mean=0.0013 / std=0.0014
  - 2. 空中戦勝率 (`z_aerial_duel_win_rate_pct`) / center_z=-2.033 / permutation_importance_mean=0.0008 / std=0.0010
  - 3. パス成功率 (`z_pass_success_rate_pct`) / center_z=-1.489 / permutation_importance_mean=0.0001 / std=0.0002
  - 4. タックル奪取率 (`z_tackle_win_rate_pct`) / center_z=+1.228 / permutation_importance_mean=0.0000 / std=0.0001
  - 5. 前進パス成功数_per90 (`z_successful_forward_passes_per90`) / center_z=-1.085 / permutation_importance_mean=0.0000 / std=0.0000
- impurity importance 上位5:
  - 1. 空中戦勝率 (`z_aerial_duel_win_rate_pct`) / center_z=-2.033 / impurity_importance=0.1975
  - 2. クリア_per90 (`z_clearances_per90`) / center_z=-1.353 / impurity_importance=0.1937
  - 3. パス成功率 (`z_pass_success_rate_pct`) / center_z=-1.489 / impurity_importance=0.1505
  - 4. ロングパス成功数_per90 (`z_successful_long_passes_per90`) / center_z=-1.090 / impurity_importance=0.1344
  - 5. タックル奪取率 (`z_tackle_win_rate_pct`) / center_z=+1.228 / impurity_importance=0.1144
- 推薦スコア候補: `z_tackle_win_rate_pct + z_interceptions_per90` を主軸にしつつ、低値が効く z_clearances_per90 は補助条件として併用するのが自然です。

### Cluster 3
- positive / negative: 71 / 78
- train AUC: 1.0000
- CV AUC: 0.9561 ± 0.0253 (StratifiedKFold(5))
- KMeans candidate_expression: 機動力寄り / 危険除去寄り
- ラベル候補: 平均型候補
- KMeans 解釈との整合性コメント: KMeans の平均型候補と整合します。RF では 高加速回数_per_matchが高い、中加速回数_per_matchが高い、前進パス成功数_per90が中庸 が上位ですが、いずれも specialized cluster 側の極端さを弾く軸として効いており、単一ラベルより『平均型候補』として扱う方が自然です。
- permutation importance 上位5:
  - 1. 高加速回数_per_match (`z_highaccel_count_full_all_per_match`) / center_z=+0.589 / permutation_importance_mean=0.0434 / std=0.0096
  - 2. 中加速回数_per_match (`z_medaccel_count_full_all_per_match`) / center_z=+0.559 / permutation_importance_mean=0.0392 / std=0.0085
  - 3. 前進パス成功数_per90 (`z_successful_forward_passes_per90`) / center_z=-0.092 / permutation_importance_mean=0.0115 / std=0.0030
  - 4. ロングパス成功数_per90 (`z_successful_long_passes_per90`) / center_z=-0.182 / permutation_importance_mean=0.0038 / std=0.0012
  - 5. パス成功率 (`z_pass_success_rate_pct`) / center_z=+0.093 / permutation_importance_mean=0.0031 / std=0.0011
- impurity importance 上位5:
  - 1. 高加速回数_per_match (`z_highaccel_count_full_all_per_match`) / center_z=+0.589 / impurity_importance=0.2746
  - 2. 中加速回数_per_match (`z_medaccel_count_full_all_per_match`) / center_z=+0.559 / impurity_importance=0.1970
  - 3. 前進パス成功数_per90 (`z_successful_forward_passes_per90`) / center_z=-0.092 / impurity_importance=0.1190
  - 4. パス成功率 (`z_pass_success_rate_pct`) / center_z=+0.093 / impurity_importance=0.0954
  - 5. ロングパス成功数_per90 (`z_successful_long_passes_per90`) / center_z=-0.182 / impurity_importance=0.0830
- 推薦スコア候補: 平均型候補は 2〜3 変数の単純加算より、`CB_cluster_centers_z.csv` の cluster 3 中心への距離ベースが適切です。

## 全体所見
- 平均型候補は Cluster 3 です。他クラスタとの分岐で目立った変数は z_highaccel_count_full_all_per_match, z_medaccel_count_full_all_per_match, z_successful_forward_passes_per90 でした。
- Cluster 0 の specialized な分離軸は z_successful_forward_passes_per90, z_pass_success_rate_pct, z_successful_long_passes_per90 でした。
- Cluster 1 の specialized な分離軸は z_medaccel_count_full_all_per_match, z_highaccel_count_full_all_per_match, z_pass_success_rate_pct でした。
- Cluster 2 の specialized な分離軸は z_clearances_per90, z_aerial_duel_win_rate_pct, z_pass_success_rate_pct でした。
- ラベル解釈は断定ではなく候補です。KMeans 中心の高低と RF の判別寄与が同時に揃う変数を優先して読んでいます。

## 推薦スコア設計メモ
- Cluster 0: `z_successful_forward_passes_per90 + z_pass_success_rate_pct` を主候補。
- Cluster 1: `z_aerial_duel_win_rate_pct + z_clearances_per90` を主候補。
- Cluster 2: `z_tackle_win_rate_pct + z_interceptions_per90` を主候補。
- Cluster 3: 平均型候補のため、単純加算ではなくクラスタ中心への距離ベース推奨。

## CV 安定性メモ
- 変動がやや大きかった cluster: 2
