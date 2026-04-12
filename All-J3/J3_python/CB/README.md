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
python3 J3_python/CB/run_cb_kmeans.py
```

## 出力ファイル

- `All-J3/J3_python/CB/output/CB_clustered_players.csv`
- `All-J3/J3_python/CB/output/CB_cluster_centers_z.csv`
- `All-J3/J3_python/CB/output/CB_cluster_summary.csv`
- `All-J3/J3_python/CB/output/CB_kmeans_report.md`

## KMeans 設定

- `n_clusters=4`
- `random_state=42`
- `n_init=50`
- `max_iter=300`

## メモ

- 実装は標準ライブラリのみで完結しており、`pandas` や `scikit-learn` が未導入でも動作します。
- `run_cb_randomforest.py` は次工程用の雛形です。今回は未実行です。
