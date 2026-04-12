# SH Recommendation Report

## 入力ファイル
- `/Users/machidanoboruyuu/Desktop/FCTokushima-EhimeFC-DataAnalysis/All-J3/J3_python/SH/output/SH_clustered_players.csv`
- `/Users/machidanoboruyuu/Desktop/FCTokushima-EhimeFC-DataAnalysis/All-J3/J3_python/SH/output/SH_cluster_centers_z.csv`
- `/Users/machidanoboruyuu/Desktop/FCTokushima-EhimeFC-DataAnalysis/All-J3/J3_python/SH/output/SH_rf_report.md`

## 採用したクラスタラベル
- 今回のラベルは分析用の作業ラベルです。
- Cluster 0: 縦突破型
- Cluster 1: 守備回収型
- Cluster 2: クロス供給型
- Cluster 3: 平均型

## スコア設計方針
- 10変数全部の単純合算は使わず、専門型クラスタは KMeans 中心と RandomForest 解釈の両方で効いていた 2〜3 変数だけを使いました。
- 平均型クラスタだけは単純加算にせず、KMeans で使った全 z 列ベクトルのクラスタ中心とのユークリッド距離で評価しました。
- スコアはクラスタ像への近さを見るもので、選手の総合力順位ではありません。

## 各クラスタのスコア式と変数選定理由
### Cluster 0: 縦突破型
- スコア式: `score_cluster_0 = z_sprint_distance_full_all_per_match + z_hsr_count_full_all_per_match + z_pa_entry_per90`
- 使用変数: スプリント距離_per_match (`z_sprint_distance_full_all_per_match`) + HSR回数_per_match (`z_hsr_count_full_all_per_match`) + PA進入_per90 (`z_pa_entry_per90`)
- 変数選定理由: Cluster 0 はスプリント距離と HSR 回数が大きく、PA 進入もプラスでした。 RF でも縦方向のスピードと侵入量が主な分離軸だったため、縦突破型はこの3変数で表現します。

### Cluster 1: 守備回収型
- スコア式: `score_cluster_1 = z_regain_within_5s_per90 - z_dribble_success_rate_pct`
- 使用変数: ロスト後5秒未満リゲイン_per90 (`z_regain_within_5s_per90`) - ドリブル成功率 (`z_dribble_success_rate_pct`)
- 変数選定理由: Cluster 1 は即時奪回が非常に高く、逆にドリブル成功率が低い守備寄りクラスタでした。 KMeans 中心と RF の双方でこの対比が最も明確だったため、守備回収型は 2 変数で素直に切ります。

### Cluster 2: クロス供給型
- スコア式: `score_cluster_2 = z_crosses_per90 + z_pa_entry_per90 + z_last_passes_per90`
- 使用変数: クロス数_per90 (`z_crosses_per90`) + PA進入_per90 (`z_pa_entry_per90`) + ラストパス_per90 (`z_last_passes_per90`)
- 変数選定理由: Cluster 2 はクロス数と PA 進入が突出し、ラストパスも高い供給特化クラスタでした。 RF と KMeans 中心の共通項として、この3変数でクロス供給型を表します。

### Cluster 3: 平均型
- スコア式: `score_cluster_3 = - euclidean_distance(player_z_vector, sh_cluster_3_center_z_vector)`
- 使用変数: KMeans に使った全 z 列
- 変数選定理由: Cluster 3 は原点に最も近い平均型でした。速度・供給・回収のいずれか一つだけで説明しにくいため、 9変数全体の中心距離で評価します。
- 距離列: `distance_to_cluster_center_3`

## 平均型だけ距離ベースにした理由
- 平均型は特定の少数変数が突出するクラスタではなく、全体ベクトルでクラスタ中心に近いかどうかを見た方が KMeans の定義に忠実です。
- 2〜3 変数の単純加算にすると specialized cluster 側の特徴量だけを拾ってしまい、平均型を平均型として評価しにくくなります。

## imputed_ratio フィルタ方針
- 公式 Top10 は原則 `imputed_ratio <= 0.25` の選手だけを対象にしました。
- 10 人未満しか残らないクラスタだけ `imputed_ratio <= 0.40` に緩和しました。
- 全選手版のスコア CSV はフィルタせず全員分を保持しています。

## 各クラスタの公式 Top10
### Cluster 0: 縦突破型
- Top10 内の元同クラスタ所属: 8/10 (80.0%)
- 概要: スプリント距離_per_match・HSR回数_per_match・PA進入_per90が高い選手が上位です。
- imputed_ratio フィルタ: `<= 0.25` を適用 (strict eligible=146)
- 公式 Top10:
  - 1. `長野　星輝` (`Shoki  Nagano`) / score=7.973 / 元Cluster=0:縦突破型 / imputed_ratio=0.000
  - 2. `森　晃太` (`Kota Mori`) / score=6.330 / 元Cluster=0:縦突破型 / imputed_ratio=0.000
  - 3. `稲積　大介` (`Daisuke Inazumi`) / score=6.159 / 元Cluster=0:縦突破型 / imputed_ratio=0.000
  - 4. `久保　吏久斗` (`Rikuto Kubo`) / score=5.979 / 元Cluster=0:縦突破型 / imputed_ratio=0.000
  - 5. `岡田　優希` (`Yuki Okada`) / score=4.181 / 元Cluster=0:縦突破型 / imputed_ratio=0.000
  - 6. `梶浦　勇輝` (`Yuki Kajiura`) / score=4.085 / 元Cluster=0:縦突破型 / imputed_ratio=0.000
  - 7. `吉長　真優` (`Mahiro Yoshinaga`) / score=4.025 / 元Cluster=2:クロス供給型 / imputed_ratio=0.000
  - 8. `塩浜　遼` (`Ryo Shiohama`) / score=3.977 / 元Cluster=0:縦突破型 / imputed_ratio=0.000
  - 9. `泉澤　仁` (`Jin Izumisawa`) / score=3.970 / 元Cluster=2:クロス供給型 / imputed_ratio=0.000
  - 10. `大関　友翔` (`Yuto  Ozeki`) / score=3.857 / 元Cluster=0:縦突破型 / imputed_ratio=0.000
- フィルタで除外された有力候補:
  - `芦部　晃生` (`Kosei Ashibe`): 無条件順位 5 位 / score=4.826 / imputed_ratio=0.778
  - `バスケス　バイロン` (`Byron Gustavo Andrés Vásquez Maragaño`): 無条件順位 6 位 / score=4.464 / imputed_ratio=0.778
  - `山中　惇希` (`Atsuki Yamanaka`): 無条件順位 7 位 / score=4.324 / imputed_ratio=0.778

### Cluster 1: 守備回収型
- Top10 内の元同クラスタ所属: 10/10 (100.0%)
- 概要: ロスト後5秒未満リゲイン_per90が高く、ドリブル成功率は低めの選手が上位です。
- imputed_ratio フィルタ: `<= 0.25` を適用 (strict eligible=146)
- 公式 Top10:
  - 1. `弓削　翼` (`Tsubasa  Yuge`) / score=5.402 / 元Cluster=1:守備回収型 / imputed_ratio=0.000
  - 2. `鍵山　慶司` (`Keiji Kagiyama`) / score=5.402 / 元Cluster=1:守備回収型 / imputed_ratio=0.000
  - 3. `下上　昇大` (`Shota Shimogami`) / score=5.360 / 元Cluster=1:守備回収型 / imputed_ratio=0.000
  - 4. `土館　賢人` (`Kento Dodate`) / score=4.583 / 元Cluster=1:守備回収型 / imputed_ratio=0.000
  - 5. `住田　将` (`Sho Sumida`) / score=4.265 / 元Cluster=1:守備回収型 / imputed_ratio=0.000
  - 6. `森田　凜` (`Rin Morita`) / score=4.142 / 元Cluster=1:守備回収型 / imputed_ratio=0.000
  - 7. `禹　相皓` (`Sang-Ho Woo`) / score=4.056 / 元Cluster=1:守備回収型 / imputed_ratio=0.000
  - 8. `澤崎　凌大` (`Ryota Sawazaki`) / score=3.624 / 元Cluster=1:守備回収型 / imputed_ratio=0.000
  - 9. `萩野　滉大` (`Kodai Hagino`) / score=3.543 / 元Cluster=1:守備回収型 / imputed_ratio=0.000
  - 10. `熊谷　アンドリュー` (`Andrew Kumagai`) / score=3.477 / 元Cluster=1:守備回収型 / imputed_ratio=0.000
- フィルタで除外された有力候補: 目立つ候補はありません。

### Cluster 2: クロス供給型
- Top10 内の元同クラスタ所属: 5/10 (50.0%)
- 概要: クロス数_per90・PA進入_per90・ラストパス_per90が高い選手が上位です。
- imputed_ratio フィルタ: `<= 0.25` を適用 (strict eligible=146)
- 公式 Top10:
  - 1. `泉澤　仁` (`Jin Izumisawa`) / score=13.091 / 元Cluster=2:クロス供給型 / imputed_ratio=0.000
  - 2. `齋藤　学` (`Manabu Saito`) / score=12.873 / 元Cluster=2:クロス供給型 / imputed_ratio=0.000
  - 3. `永長　鷹虎` (`Takatora Einaga`) / score=10.922 / 元Cluster=2:クロス供給型 / imputed_ratio=0.000
  - 4. `若谷　拓海` (`Takumi Wakaya`) / score=8.903 / 元Cluster=2:クロス供給型 / imputed_ratio=0.000
  - 5. `吉長　真優` (`Mahiro Yoshinaga`) / score=7.603 / 元Cluster=2:クロス供給型 / imputed_ratio=0.000
  - 6. `稲積　大介` (`Daisuke Inazumi`) / score=5.674 / 元Cluster=0:縦突破型 / imputed_ratio=0.000
  - 7. `長野　星輝` (`Shoki  Nagano`) / score=5.577 / 元Cluster=0:縦突破型 / imputed_ratio=0.000
  - 8. `井上　怜` (`Ren Inoue`) / score=5.418 / 元Cluster=0:縦突破型 / imputed_ratio=0.000
  - 9. `菊井　悠介` (`Yusuke Kikui`) / score=4.772 / 元Cluster=0:縦突破型 / imputed_ratio=0.000
  - 10. `布施谷　翔` (`Sho Fuseya`) / score=4.716 / 元Cluster=0:縦突破型 / imputed_ratio=0.000
- フィルタで除外された有力候補: 目立つ候補はありません。

### Cluster 3: 平均型
- Top10 内の元同クラスタ所属: 10/10 (100.0%)
- 概要: 全 z 列ベクトルでクラスタ中心との距離が小さい選手が上位です。
- imputed_ratio フィルタ: `<= 0.25` を適用 (strict eligible=146)
- 距離の目安: 1位の `distance_to_cluster_center_3` = 1.176
- 公式 Top10:
  - 1. `安永　玲央` (`Reo Yasunaga`) / score=-1.176 / 元Cluster=3:平均型 / imputed_ratio=0.000
  - 2. `牛之濵　拓` (`Taku Ushinohama`) / score=-1.185 / 元Cluster=3:平均型 / imputed_ratio=0.000
  - 3. `横山　智也` (`Tomoya Yokoyama`) / score=-1.467 / 元Cluster=3:平均型 / imputed_ratio=0.000
  - 4. `徳永　裕大` (`Yudai Tokunaga`) / score=-1.576 / 元Cluster=3:平均型 / imputed_ratio=0.000
  - 5. `利根　瑠偉` (`Rui Tone`) / score=-1.603 / 元Cluster=3:平均型 / imputed_ratio=0.000
  - 6. `山本　康裕` (`Kosuke Yamamoto`) / score=-1.629 / 元Cluster=3:平均型 / imputed_ratio=0.000
  - 7. `鈴木　拳士郎` (`Kenshiro Suzuki`) / score=-1.640 / 元Cluster=3:平均型 / imputed_ratio=0.000
  - 8. `佐相　壱明` (`Kazuaki Saso`) / score=-1.716 / 元Cluster=3:平均型 / imputed_ratio=0.000
  - 9. `東出　壮太` (`Sota Higashide`) / score=-1.766 / 元Cluster=3:平均型 / imputed_ratio=0.000
  - 10. `前川　大河` (`Taiga Maekawa`) / score=-1.770 / 元Cluster=3:平均型 / imputed_ratio=0.000
- フィルタで除外された有力候補:
  - `小堀　空` (`Sora Kobori`): 無条件順位 1 位 / score=-0.274 / imputed_ratio=0.778
  - `宇都木　峻` (`Shun Utsugi`): 無条件順位 2 位 / score=-0.311 / imputed_ratio=0.778
  - `狩野　海晟` (`Kaisei  Kano`): 無条件順位 3 位 / score=-0.334 / imputed_ratio=0.778

## 「クラスタ所属」と「クラスタ像へのスコア順位」がズレた代表例
- `稲積　大介` (`Daisuke Inazumi`) は元 `Cluster 0: 縦突破型` ですが、 `Cluster 2: クロス供給型` スコアで 6 位です (`score=5.674`, クロス数_per90=3.818, PA進入_per90=0.923, ラストパス_per90=0.933)。
- `吉長　真優` (`Mahiro Yoshinaga`) は元 `Cluster 2: クロス供給型` ですが、 `Cluster 0: 縦突破型` スコアで 10 位です (`score=4.025`, スプリント距離_per_match=-0.376, HSR回数_per_match=-0.814, PA進入_per90=5.216)。

## スコア式の注意点
- これは総合力ランキングではありません。
- あくまで特定のクラスタ像への近さを見るためのスコアです。
- specialized cluster の式は、そのクラスタ像を表す少数変数だけを強く見ています。
- 平均型は距離ベースなので、`score = -distance` です。0 に近いほど中心に近く、より平均型らしいと解釈します。
