# CMF Recommendation Report

## 入力ファイル
- `/Users/machidanoboruyuu/Desktop/FCTokushima-EhimeFC-DataAnalysis/All-J3/J3_python/CMF/output/CMF_clustered_players.csv`
- `/Users/machidanoboruyuu/Desktop/FCTokushima-EhimeFC-DataAnalysis/All-J3/J3_python/CMF/output/CMF_cluster_centers_z.csv`
- `/Users/machidanoboruyuu/Desktop/FCTokushima-EhimeFC-DataAnalysis/All-J3/J3_python/CMF/output/CMF_rf_report.md`

## 採用したクラスタラベル
- 今回のラベルは分析用の作業ラベルです。
- Cluster 0: ボールハンター型
- Cluster 1: ボックストゥボックス型
- Cluster 2: ゲームオーガナイザー型

## スコア設計方針
- 10変数全部の単純合算は使わず、専門型クラスタは KMeans 中心と RandomForest 解釈の両方で効いていた 2〜3 変数だけを使いました。
- 平均型クラスタだけは単純加算にせず、KMeans で使った全 z 列ベクトルのクラスタ中心とのユークリッド距離で評価しました。
- スコアはクラスタ像への近さを見るもので、選手の総合力順位ではありません。

## 各クラスタのスコア式と変数選定理由
### Cluster 0: ボールハンター型
- スコア式: `score_cluster_0 = z_ball_gains_per90 + z_long_pass_share_pct - z_pass_success_rate_pct`
- 使用変数: ボール奪取_per90 (`z_ball_gains_per90`) + ロングパス比率 (`z_long_pass_share_pct`) - パス成功率 (`z_pass_success_rate_pct`)
- 変数選定理由: Cluster 0 はボール奪取とロングパス比率が高く、パス成功率は低めのダイレクト志向でした。 KMeans 中心と RF 上位の重なりから、奪って前へ運ぶボールハンター型としてこの3変数で評価します。

### Cluster 1: ボックストゥボックス型
- スコア式: `score_cluster_1 = - euclidean_distance(player_z_vector, cmf_cluster_1_center_z_vector)`
- 使用変数: KMeans に使った全 z 列
- 変数選定理由: Cluster 1 は原点に最も近い一方で、走行距離と敵陣奪回比率がプラスの二方向型でした。 平均寄りのボックストゥボックス像として、少数変数の合算ではなく全体ベクトルの距離で見ます。
- 距離列: `distance_to_cluster_center_1`

### Cluster 2: ゲームオーガナイザー型
- スコア式: `score_cluster_2 = z_short_pass_share_pct + z_forward_pass_success_rate_pct + z_pass_success_rate_pct`
- 使用変数: ショートパス比率 (`z_short_pass_share_pct`) + 前進パス成功率 (`z_forward_pass_success_rate_pct`) + パス成功率 (`z_pass_success_rate_pct`)
- 変数選定理由: Cluster 2 はショートパス比率、前進パス成功率、パス成功率がいずれも高いゲームメイク特化型でした。 KMeans 中心と RF の両方でこの3変数が揃っていたため、そのまま採用します。

## 平均型だけ距離ベースにした理由
- 平均型は特定の少数変数が突出するクラスタではなく、全体ベクトルでクラスタ中心に近いかどうかを見た方が KMeans の定義に忠実です。
- 2〜3 変数の単純加算にすると specialized cluster 側の特徴量だけを拾ってしまい、平均型を平均型として評価しにくくなります。

## imputed_ratio フィルタ方針
- 公式 Top10 は原則 `imputed_ratio <= 0.25` の選手だけを対象にしました。
- 10 人未満しか残らないクラスタだけ `imputed_ratio <= 0.40` に緩和しました。
- 全選手版のスコア CSV はフィルタせず全員分を保持しています。

## 各クラスタの公式 Top10
### Cluster 0: ボールハンター型
- Top10 内の元同クラスタ所属: 8/10 (80.0%)
- 概要: ボール奪取_per90・ロングパス比率が高く、パス成功率は低めの選手が上位です。
- imputed_ratio フィルタ: `<= 0.25` を適用 (strict eligible=24)
- 公式 Top10:
  - 1. `前澤　甲気` (`Koki Maezawa`) / score=5.770 / 元Cluster=0:ボールハンター型 / imputed_ratio=0.000
  - 2. `山田　尚幸` (`Naoyuki Yamada`) / score=4.298 / 元Cluster=0:ボールハンター型 / imputed_ratio=0.000
  - 3. `ガブリエル　エンリケ` (`Gabriel Nascimento`) / score=3.384 / 元Cluster=0:ボールハンター型 / imputed_ratio=0.000
  - 4. `岩上　祐三` (`Yuzo Iwakami`) / score=2.826 / 元Cluster=0:ボールハンター型 / imputed_ratio=0.000
  - 5. `柴田　壮介` (`Sosuke Shibata`) / score=2.793 / 元Cluster=1:ボックストゥボックス型 / imputed_ratio=0.000
  - 6. `喜山　康平` (`Kohei Kiyama`) / score=2.411 / 元Cluster=0:ボールハンター型 / imputed_ratio=0.000
  - 7. `高橋　耕平` (`Kohei Takahashi`) / score=1.724 / 元Cluster=0:ボールハンター型 / imputed_ratio=0.000
  - 8. `坪川　潤之` (`Hiroyuki Tsubokawa`) / score=1.263 / 元Cluster=0:ボールハンター型 / imputed_ratio=0.000
  - 9. `米原　秀亮` (`Shusuke Yonehara`) / score=0.903 / 元Cluster=0:ボールハンター型 / imputed_ratio=0.000
  - 10. `安田　虎士朗` (`Kojiro Yasuda`) / score=0.883 / 元Cluster=1:ボックストゥボックス型 / imputed_ratio=0.000
- フィルタで除外された有力候補: 目立つ候補はありません。

### Cluster 1: ボックストゥボックス型
- Top10 内の元同クラスタ所属: 9/10 (90.0%)
- 概要: 全 z 列ベクトルでクラスタ中心との距離が小さい選手が上位です。
- imputed_ratio フィルタ: `<= 0.25` を適用 (strict eligible=24)
- 距離の目安: 1位の `distance_to_cluster_center_1` = 1.082
- 公式 Top10:
  - 1. `高吉　正真` (`Shoma Takayoshi`) / score=-1.082 / 元Cluster=1:ボックストゥボックス型 / imputed_ratio=0.000
  - 2. `小島　秀仁` (`Shuto Kojima`) / score=-1.544 / 元Cluster=1:ボックストゥボックス型 / imputed_ratio=0.000
  - 3. `力安　祥伍` (`Shogo Rikiyasu`) / score=-2.116 / 元Cluster=1:ボックストゥボックス型 / imputed_ratio=0.000
  - 4. `菅井　拓也` (`Takuya Sugai`) / score=-2.232 / 元Cluster=1:ボックストゥボックス型 / imputed_ratio=0.000
  - 5. `井澤　春輝` (`Haruki Izawa`) / score=-2.267 / 元Cluster=1:ボックストゥボックス型 / imputed_ratio=0.000
  - 6. `米原　秀亮` (`Shusuke Yonehara`) / score=-2.415 / 元Cluster=0:ボールハンター型 / imputed_ratio=0.000
  - 7. `末木　裕也` (`Hiroya Sueki`) / score=-2.444 / 元Cluster=1:ボックストゥボックス型 / imputed_ratio=0.000
  - 8. `堀内　颯人` (`Hayato Horiuchi`) / score=-2.610 / 元Cluster=1:ボックストゥボックス型 / imputed_ratio=0.000
  - 9. `河井　陽介` (`Yosuke Kawai`) / score=-2.660 / 元Cluster=1:ボックストゥボックス型 / imputed_ratio=0.000
  - 10. `安田　虎士朗` (`Kojiro Yasuda`) / score=-2.796 / 元Cluster=1:ボックストゥボックス型 / imputed_ratio=0.000
- フィルタで除外された有力候補:
  - `渡邉　綾平` (`Ryohei Watanabe`): 無条件順位 1 位 / score=-0.553 / imputed_ratio=0.875
  - `工藤　真人` (`Manato Kudo`): 無条件順位 2 位 / score=-0.574 / imputed_ratio=0.875
  - `岡庭　裕貴` (`Yuki Okaniwa`): 無条件順位 3 位 / score=-0.577 / imputed_ratio=0.875

### Cluster 2: ゲームオーガナイザー型
- Top10 内の元同クラスタ所属: 5/10 (50.0%)
- 概要: ショートパス比率・前進パス成功率・パス成功率が高い選手が上位です。
- imputed_ratio フィルタ: `<= 0.25` を適用 (strict eligible=24)
- 公式 Top10:
  - 1. `宮崎　智彦` (`Tomohiko Miyazaki`) / score=4.834 / 元Cluster=2:ゲームオーガナイザー型 / imputed_ratio=0.000
  - 2. `針谷　岳晃` (`Takeaki Harigaya`) / score=4.810 / 元Cluster=2:ゲームオーガナイザー型 / imputed_ratio=0.000
  - 3. `加藤　匠人` (`Takuto Kato`) / score=4.773 / 元Cluster=2:ゲームオーガナイザー型 / imputed_ratio=0.000
  - 4. `岩本　翔` (`Sho Iwamoto`) / score=4.533 / 元Cluster=2:ゲームオーガナイザー型 / imputed_ratio=0.000
  - 5. `佐藤　祐太` (`Yuta Sato`) / score=3.415 / 元Cluster=2:ゲームオーガナイザー型 / imputed_ratio=0.000
  - 6. `末木　裕也` (`Hiroya Sueki`) / score=2.174 / 元Cluster=1:ボックストゥボックス型 / imputed_ratio=0.000
  - 7. `河井　陽介` (`Yosuke Kawai`) / score=0.879 / 元Cluster=1:ボックストゥボックス型 / imputed_ratio=0.000
  - 8. `堀内　颯人` (`Hayato Horiuchi`) / score=0.874 / 元Cluster=1:ボックストゥボックス型 / imputed_ratio=0.000
  - 9. `高橋　耕平` (`Kohei Takahashi`) / score=0.800 / 元Cluster=0:ボールハンター型 / imputed_ratio=0.000
  - 10. `高吉　正真` (`Shoma Takayoshi`) / score=0.488 / 元Cluster=1:ボックストゥボックス型 / imputed_ratio=0.000
- フィルタで除外された有力候補: 目立つ候補はありません。

## 「クラスタ所属」と「クラスタ像へのスコア順位」がズレた代表例
- `柴田　壮介` (`Sosuke Shibata`) は元 `Cluster 1: ボックストゥボックス型` ですが、 `Cluster 0: ボールハンター型` スコアで 5 位です (`score=2.793`, ボール奪取_per90=2.176, ロングパス比率=0.050, パス成功率=-0.567)。
- `末木　裕也` (`Hiroya Sueki`) は元 `Cluster 1: ボックストゥボックス型` ですが、 `Cluster 2: ゲームオーガナイザー型` スコアで 6 位です (`score=2.174`, ショートパス比率=0.266, 前進パス成功率=1.128, パス成功率=0.781)。

## スコア式の注意点
- これは総合力ランキングではありません。
- あくまで特定のクラスタ像への近さを見るためのスコアです。
- specialized cluster の式は、そのクラスタ像を表す少数変数だけを強く見ています。
- 平均型は距離ベースなので、`score = -distance` です。0 に近いほど中心に近く、より平均型らしいと解釈します。
