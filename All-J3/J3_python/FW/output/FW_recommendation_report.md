# FW Recommendation Report

## 入力ファイル
- `/Users/machidanoboruyuu/Desktop/FCTokushima-EhimeFC-DataAnalysis/All-J3/J3_python/FW/output/FW_clustered_players.csv`
- `/Users/machidanoboruyuu/Desktop/FCTokushima-EhimeFC-DataAnalysis/All-J3/J3_python/FW/output/FW_cluster_centers_z.csv`
- `/Users/machidanoboruyuu/Desktop/FCTokushima-EhimeFC-DataAnalysis/All-J3/J3_python/FW/output/FW_rf_report.md`

## 採用したクラスタラベル
- 今回のラベルは分析用の作業ラベルです。
- Cluster 0: 平均型
- Cluster 1: フィニッシュ型
- Cluster 2: 空中戦・前進関与型
- Cluster 3: 前線守備・回収型

## スコア設計方針
- 10変数全部の単純合算は使わず、専門型クラスタは KMeans 中心と RandomForest 解釈の両方で効いていた 2〜3 変数だけを使いました。
- 平均型クラスタだけは単純加算にせず、KMeans で使った全 z 列ベクトルのクラスタ中心とのユークリッド距離で評価しました。
- スコアはクラスタ像への近さを見るもので、選手の総合力順位ではありません。

## 各クラスタのスコア式と変数選定理由
### Cluster 0: 平均型
- スコア式: `score_cluster_0 = - euclidean_distance(player_z_vector, fw_cluster_0_center_z_vector)`
- 使用変数: KMeans に使った全 z 列
- 変数選定理由: Cluster 0 は原点に最も近い平均型でした。突出変数よりも、10変数全体で中心にどれだけ近いかを見た方が KMeans の定義と整合するため、距離ベースで評価します。
- 距離列: `distance_to_cluster_center_0`

### Cluster 1: フィニッシュ型
- スコア式: `score_cluster_1 = z_shot_conversion_rate_pct + z_goals_per90 + z_shot_on_target_rate_pct`
- 使用変数: 決定率 (`z_shot_conversion_rate_pct`) + 得点_per90 (`z_goals_per90`) + 枠内率 (`z_shot_on_target_rate_pct`)
- 変数選定理由: Cluster 1 は少数ながら決定率・得点_per90・枠内率が極端に高いクラスタでした。 KMeans 中心でもこの3変数が最も突出し、RF 側でも分離軸は同じ3変数に集中していたため、 フィニッシュ性能に絞って評価します。

### Cluster 2: 空中戦・前進関与型
- スコア式: `score_cluster_2 = z_last_passes_per90 + z_aerial_wins_per90 + z_box_shots_per90`
- 使用変数: ラストパス_per90 (`z_last_passes_per90`) + 空中戦勝利数_per90 (`z_aerial_wins_per90`) + ボックス内シュート_per90 (`z_box_shots_per90`)
- 変数選定理由: Cluster 2 はラストパス・空中戦勝利・ボックス内シュートが同時に高く、 前進関与とターゲット性能の両方が見えるクラスタでした。 KMeans 中心と RF 上位の重なりから、この3変数に絞って像を表現します。

### Cluster 3: 前線守備・回収型
- スコア式: `score_cluster_3 = z_successful_forward_passes_per90 + z_attacking_third_gains_per90`
- 使用変数: 前進パス成功数_per90 (`z_successful_forward_passes_per90`) + 攻撃3rd奪回_per90 (`z_attacking_third_gains_per90`)
- 変数選定理由: Cluster 3 は得点・ボックス内シュートが低い一方、前進パス成功数と攻撃3rd奪回が高く、 前線での回収から前進局面に関わる色が強く出ました。 RF でもこの2変数が上位だったため、前線守備・回収型の核として採用します。

## 平均型だけ距離ベースにした理由
- 平均型は特定の少数変数が突出するクラスタではなく、全体ベクトルでクラスタ中心に近いかどうかを見た方が KMeans の定義に忠実です。
- 2〜3 変数の単純加算にすると specialized cluster 側の特徴量だけを拾ってしまい、平均型を平均型として評価しにくくなります。

## imputed_ratio フィルタ方針
- 公式 Top10 は原則 `imputed_ratio <= 0.25` の選手だけを対象にしました。
- 10 人未満しか残らないクラスタだけ `imputed_ratio <= 0.40` に緩和しました。
- 全選手版のスコア CSV はフィルタせず全員分を保持しています。

## 各クラスタの公式 Top10
### Cluster 0: 平均型
- Top10 内の元同クラスタ所属: 10/10 (100.0%)
- 概要: 全 z 列ベクトルでクラスタ中心との距離が小さい選手が上位です。
- imputed_ratio フィルタ: `<= 0.25` を適用 (strict eligible=82)
- 距離の目安: 1位の `distance_to_cluster_center_0` = 1.195
- 公式 Top10:
  - 1. `丹羽　詩温` (`Shion Niwa`) / score=-1.195 / 元Cluster=0:平均型 / imputed_ratio=0.000
  - 2. `島田　拓海` (`Takumi Shimada`) / score=-1.514 / 元Cluster=0:平均型 / imputed_ratio=0.000
  - 3. `パトリック　グスタフソン` (`Patrik Gustavsson`) / score=-1.560 / 元Cluster=0:平均型 / imputed_ratio=0.000
  - 4. `田口　裕也` (`Yuya Taguchi`) / score=-1.582 / 元Cluster=0:平均型 / imputed_ratio=0.000
  - 5. `マリソン` (`Marlyson Conceição Oliveira`) / score=-1.835 / 元Cluster=0:平均型 / imputed_ratio=0.000
  - 6. `髙木　彰人` (`Akito Takagi`) / score=-1.885 / 元Cluster=0:平均型 / imputed_ratio=0.000
  - 7. `安藤　翼` (`Tsubasa Ando`) / score=-1.922 / 元Cluster=0:平均型 / imputed_ratio=0.000
  - 8. `冨永　虹七` (`Niina Tominaga`) / score=-1.967 / 元Cluster=0:平均型 / imputed_ratio=0.000
  - 9. `澤上　竜二` (`Ryuji Sawakami`) / score=-1.978 / 元Cluster=0:平均型 / imputed_ratio=0.000
  - 10. `和田　育` (`Hagumi Wada`) / score=-2.072 / 元Cluster=0:平均型 / imputed_ratio=0.000
- フィルタで除外された有力候補:
  - `ラファエル　フルタード` (`Rafael Victor de Oliveira Furtado`): 無条件順位 1 位 / score=-0.473 / imputed_ratio=0.900
  - `太田　龍之介` (`Ryunosuke Ota`): 無条件順位 2 位 / score=-0.473 / imputed_ratio=0.900
  - `平岡　将豪` (`Masahide Hiraoka`): 無条件順位 3 位 / score=-0.476 / imputed_ratio=0.900

### Cluster 1: フィニッシュ型
- Top10 内の元同クラスタ所属: 2/10 (20.0%)
- 概要: 決定率・得点_per90・枠内率が高い選手が上位です。
- imputed_ratio フィルタ: `<= 0.25` を適用 (strict eligible=82)
- 公式 Top10:
  - 1. `進　昂平` (`Kohei Shin`) / score=12.326 / 元Cluster=1:フィニッシュ型 / imputed_ratio=0.000
  - 2. `望月　想空` (`Sora Mochizuki`) / score=11.686 / 元Cluster=1:フィニッシュ型 / imputed_ratio=0.000
  - 3. `ウェズレイ　タンキ` (`Wesley Tanque da Silva`) / score=4.741 / 元Cluster=2:空中戦・前進関与型 / imputed_ratio=0.000
  - 4. `武藤　雄樹` (`Yuki Muto`) / score=4.223 / 元Cluster=0:平均型 / imputed_ratio=0.000
  - 5. `浅川　隼人` (`Hayato Asakawa`) / score=4.164 / 元Cluster=0:平均型 / imputed_ratio=0.000
  - 6. `白井　陽斗` (`Haruto Shirai`) / score=4.124 / 元Cluster=0:平均型 / imputed_ratio=0.000
  - 7. `松木　駿之介` (`Shunnosuke Matsuki`) / score=3.982 / 元Cluster=0:平均型 / imputed_ratio=0.000
  - 8. `ファビアン　ゴンザレス` (`Fabián Andrés González Lasso`) / score=3.962 / 元Cluster=2:空中戦・前進関与型 / imputed_ratio=0.000
  - 9. `日野　友貴` (`Tomoki Hino`) / score=3.848 / 元Cluster=0:平均型 / imputed_ratio=0.000
  - 10. `藤岡　浩介` (`Kosuke Fujioka`) / score=3.839 / 元Cluster=0:平均型 / imputed_ratio=0.000
- フィルタで除外された有力候補: 目立つ候補はありません。

### Cluster 2: 空中戦・前進関与型
- Top10 内の元同クラスタ所属: 8/10 (80.0%)
- 概要: ラストパス_per90・空中戦勝利数_per90・ボックス内シュート_per90が高い選手が上位です。
- imputed_ratio フィルタ: `<= 0.25` を適用 (strict eligible=82)
- 公式 Top10:
  - 1. `渡邉　颯太` (`Sota Watanabe`) / score=7.433 / 元Cluster=2:空中戦・前進関与型 / imputed_ratio=0.000
  - 2. `ジョップ　セリンサリウ` (`Serigne Diop`) / score=6.133 / 元Cluster=0:平均型 / imputed_ratio=0.000
  - 3. `ファビアン　ゴンザレス` (`Fabián Andrés González Lasso`) / score=5.603 / 元Cluster=2:空中戦・前進関与型 / imputed_ratio=0.000
  - 4. `マルクス　ヴィニシウス` (`Marcus Vinicius Ferreira Teixeira`) / score=5.256 / 元Cluster=2:空中戦・前進関与型 / imputed_ratio=0.000
  - 5. `ウェズレイ　タンキ` (`Wesley Tanque da Silva`) / score=4.883 / 元Cluster=2:空中戦・前進関与型 / imputed_ratio=0.000
  - 6. `望月　想空` (`Sora Mochizuki`) / score=4.776 / 元Cluster=1:フィニッシュ型 / imputed_ratio=0.000
  - 7. `赤星　魁麻` (`Kaima Akahoshi`) / score=4.723 / 元Cluster=2:空中戦・前進関与型 / imputed_ratio=0.000
  - 8. `妹尾　直哉` (`Naoya Senoo`) / score=4.334 / 元Cluster=2:空中戦・前進関与型 / imputed_ratio=0.000
  - 9. `杉浦　恭平` (`Kyohei Sugiura`) / score=4.089 / 元Cluster=2:空中戦・前進関与型 / imputed_ratio=0.000
  - 10. `吉澤　柊` (`Shu Yoshizawa`) / score=3.939 / 元Cluster=2:空中戦・前進関与型 / imputed_ratio=0.000
- フィルタで除外された有力候補: 目立つ候補はありません。

### Cluster 3: 前線守備・回収型
- Top10 内の元同クラスタ所属: 8/10 (80.0%)
- 概要: 前進パス成功数_per90・攻撃3rd奪回_per90が高い選手が上位です。
- imputed_ratio フィルタ: `<= 0.25` を適用 (strict eligible=82)
- 公式 Top10:
  - 1. `増田　隼司` (`Shunji Masuda`) / score=4.457 / 元Cluster=3:前線守備・回収型 / imputed_ratio=0.000
  - 2. `川西　翔太` (`Shota Kawanishi`) / score=4.444 / 元Cluster=3:前線守備・回収型 / imputed_ratio=0.000
  - 3. `髙尾　流星` (`Ryusei Takao`) / score=4.328 / 元Cluster=3:前線守備・回収型 / imputed_ratio=0.000
  - 4. `渡邉　颯太` (`Sota Watanabe`) / score=4.308 / 元Cluster=2:空中戦・前進関与型 / imputed_ratio=0.000
  - 5. `アンジェロッティ` (`Rodrigo Luiz Angelotti`) / score=4.016 / 元Cluster=3:前線守備・回収型 / imputed_ratio=0.000
  - 6. `清水　一雅` (`Kazumasa  Shimizu`) / score=3.949 / 元Cluster=2:空中戦・前進関与型 / imputed_ratio=0.000
  - 7. `岩渕　良太` (`Ryota Iwabuchi`) / score=3.672 / 元Cluster=3:前線守備・回収型 / imputed_ratio=0.000
  - 8. `中村　充孝` (`Atsutaka Nakamura`) / score=2.901 / 元Cluster=3:前線守備・回収型 / imputed_ratio=0.000
  - 9. `山本　宗太朗` (`Sotaro Yamamoto`) / score=2.594 / 元Cluster=3:前線守備・回収型 / imputed_ratio=0.000
  - 10. `脇坂　崚平` (`Ryohei Wakizaka`) / score=2.520 / 元Cluster=3:前線守備・回収型 / imputed_ratio=0.000
- フィルタで除外された有力候補: 目立つ候補はありません。

## 「クラスタ所属」と「クラスタ像へのスコア順位」がズレた代表例
- `ジョップ　セリンサリウ` (`Serigne Diop`) は元 `Cluster 0: 平均型` ですが、 `Cluster 2: 空中戦・前進関与型` スコアで 2 位です (`score=6.133`, ラストパス_per90=0.350, 空中戦勝利数_per90=2.557, ボックス内シュート_per90=3.226)。
- `ウェズレイ　タンキ` (`Wesley Tanque da Silva`) は元 `Cluster 2: 空中戦・前進関与型` ですが、 `Cluster 1: フィニッシュ型` スコアで 3 位です (`score=4.741`, 決定率=1.511, 得点_per90=2.111, 枠内率=1.120)。

## スコア式の注意点
- これは総合力ランキングではありません。
- あくまで特定のクラスタ像への近さを見るためのスコアです。
- specialized cluster の式は、そのクラスタ像を表す少数変数だけを強く見ています。
- 平均型は距離ベースなので、`score = -distance` です。0 に近いほど中心に近く、より平均型らしいと解釈します。
