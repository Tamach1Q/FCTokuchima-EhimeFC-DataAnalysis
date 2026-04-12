# CB KMeans / RandomForest

## 入力ファイル

- `All-J3/J3_csv/SC_position_clustering/CB/CB_features_preprocessed.csv`

## 使用変数

KMeans では以下の `z_*` 10 変数のみを使います。

- `z_aerial_duel_win_rate_pct`
- `z_tackle_win_rate_pct`
- `z_interceptions_per90`
- `z_blocks_per90`
- `z_clearances_per90`
- `z_pass_success_rate_pct`
- `z_successful_forward_passes_per90`
- `z_successful_long_passes_per90`
- `z_medaccel_count_full_all_per_match`
- `z_highaccel_count_full_all_per_match`

## 実行方法

`All-J3` ディレクトリをカレントにして実行します。

```bash
../env/bin/python J3_python/CB/run_cb_kmeans.py
../env/bin/python J3_python/CB/run_cb_randomforest.py
```

## 出力ファイル

- `All-J3/J3_python/CB/output/CB_clustered_players.csv`
- `All-J3/J3_python/CB/output/CB_cluster_centers_z.csv`
- `All-J3/J3_python/CB/output/CB_cluster_summary.csv`
- `All-J3/J3_python/CB/output/CB_kmeans_report.md`
- `All-J3/J3_python/CB/output/CB_rf_overall_summary.csv`
- `All-J3/J3_python/CB/output/CB_rf_cluster_0_importance.csv`
- `All-J3/J3_python/CB/output/CB_rf_cluster_1_importance.csv`
- `All-J3/J3_python/CB/output/CB_rf_cluster_2_importance.csv`
- `All-J3/J3_python/CB/output/CB_rf_cluster_3_importance.csv`
- `All-J3/J3_python/CB/output/CB_rf_report.md`

## KMeans 設定

- `n_clusters=4`
- `random_state=42`
- `n_init=50`
- `max_iter=300`

## メモ

- KMeans は標準ライブラリのみで動作します。
- RandomForest は `pandas` / `numpy` / `scikit-learn` を使うため、リポジトリ同梱の `../env/bin/python` での実行を前提にしています。
