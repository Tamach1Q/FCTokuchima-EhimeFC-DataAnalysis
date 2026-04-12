# SB KMeans / RandomForest

## 入力ファイル

- `All-J3/J3_csv/SC_position_clustering/SB/SB_features_preprocessed.csv`

## 使用変数

KMeans では以下の `z_*` 10 変数のみを使います。

- `z_running_distance_full_all_per_match`
- `z_hi_distance_full_all_per_match`
- `z_sprint_count_full_all_per_match`
- `z_crosses_per90`
- `z_cross_success_rate_pct`
- `z_pa_entry_per90`
- `z_tackle_win_rate_pct`
- `z_blocks_per90`
- `z_forward_long_pass_success_rate_pct`
- `z_regain_within_5s_per90`

## 実行方法

`All-J3` ディレクトリをカレントにして実行します。

```bash
python3 J3_python/SB/run_sb_kmeans.py
```

## 出力ファイル

- `All-J3/J3_python/SB/output/SB_clustered_players.csv`
- `All-J3/J3_python/SB/output/SB_cluster_centers_z.csv`
- `All-J3/J3_python/SB/output/SB_cluster_summary.csv`
- `All-J3/J3_python/SB/output/SB_kmeans_report.md`

## KMeans 設定

- `n_clusters=4`
- `random_state=42`
- `n_init=50`
- `max_iter=300`

## メモ

- 実装は標準ライブラリのみで完結しており、`pandas` や `scikit-learn` が未導入でも動作します。
- `run_sb_randomforest.py` は次工程用の雛形です。今回は未実行です。
