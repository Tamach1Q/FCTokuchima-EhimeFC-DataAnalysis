# ST Archetype Report

## 入力ファイル
- `/Users/machidanoboruyuu/Desktop/FCTokushima-EhimeFC-DataAnalysis/All-J3/J3_csv/SC_position_clustering/ST/ST_features_preprocessed.csv`

## 使用した z 列
- `z_shot_conversion_rate_pct` (決定率)
- `z_box_shots_per90` (ボックス内シュート_per90)
- `z_goals_per90` (得点_per90)
- `z_sprint_count_full_all_per_match` (スプリント回数_per_match)
- `z_last_passes_per90` (ラストパス_per90)
- `z_successful_through_passes_per90` (スルーパス成功数_per90)
- `z_attacking_third_gains_per90` (攻撃3rd奪回_per90)

## 3類型のスコア式
- ラインレシーバー: `score_line_receiver = z_last_passes_per90 + z_successful_through_passes_per90`
- シャドーストライカー: `score_shadow_striker = z_box_shots_per90 + z_goals_per90 + z_shot_conversion_rate_pct`
- ハイプレス・イニシエーター: `score_high_press_initiator = z_attacking_third_gains_per90 + z_sprint_count_full_all_per_match`

## KMeans をやらなかった理由
- ST はサンプル数が 11 名と少なく、KMeans / RandomForest のクラスタ安定性が低いため、今回は 3 類型の直接スコアリングだけにしました。

## imputed_ratio フィルタ方針
- 公式 Top10 は原則 `imputed_ratio <= 0.25` を適用しました。
- 10 人未満しか残らない類型のみ `imputed_ratio <= 0.40` に緩和しました。
- 全選手版 CSV はフィルタせず全員分を保持しています。

## 補完メモ
- 入力 `imputed_*` と残存 z 欠損の中央値補完を合算して `imputed_count` / `imputed_ratio` を計算しています。
- 追加で中央値補完した列と件数:
  - 追加補完は発生していません。

## 類型別公式 Top10
### ラインレシーバー
- imputed_ratio フィルタ: `<= 0.25` を適用
- 公式 Top10:
  - 1. `井上　直輝` (`Naoki Inoue`) / score=4.729 / imputed_ratio=0.000
  - 2. `矢田　旭` (`Asahi Yada`) / score=2.046 / imputed_ratio=0.000
  - 3. `上野　瑶介` (`Yosuke Ueno`) / score=0.482 / imputed_ratio=0.000
  - 4. `佐々木　陽次` (`Yoji Sasaki`) / score=0.208 / imputed_ratio=0.000
  - 5. `髙橋　馨希` (`Yoshiki Takahashi`) / score=-0.710 / imputed_ratio=0.000
  - 6. `三田　尚希` (`Naoki Sanda`) / score=-0.967 / imputed_ratio=0.000
  - 7. `平原　隆暉` (`Ryuki Hirahara`) / score=-0.994 / imputed_ratio=0.000
  - 8. `加藤　潤也` (`Junya Kato`) / score=-1.142 / imputed_ratio=0.000
  - 9. `菊谷　篤資` (`Atsushi  Kikutani`) / score=-1.259 / imputed_ratio=0.000
  - 10. `奥村　晃司` (`Koji Okumura`) / score=-1.569 / imputed_ratio=0.000
- フィルタで除外された有力候補:
  - `樺山　諒乃介` (`Ryonosuke Kabayama`): 無条件順位 6 位 / score=-0.824 / imputed_ratio=0.857

### シャドーストライカー
- imputed_ratio フィルタ: `<= 0.25` を適用
- 公式 Top10:
  - 1. `佐々木　陽次` (`Yoji Sasaki`) / score=2.993 / imputed_ratio=0.000
  - 2. `加藤　潤也` (`Junya Kato`) / score=2.433 / imputed_ratio=0.000
  - 3. `菊谷　篤資` (`Atsushi  Kikutani`) / score=1.143 / imputed_ratio=0.000
  - 4. `井上　直輝` (`Naoki Inoue`) / score=0.570 / imputed_ratio=0.000
  - 5. `奥村　晃司` (`Koji Okumura`) / score=0.535 / imputed_ratio=0.000
  - 6. `髙橋　馨希` (`Yoshiki Takahashi`) / score=-0.140 / imputed_ratio=0.000
  - 7. `上野　瑶介` (`Yosuke Ueno`) / score=-0.886 / imputed_ratio=0.000
  - 8. `三田　尚希` (`Naoki Sanda`) / score=-1.725 / imputed_ratio=0.000
  - 9. `平原　隆暉` (`Ryuki Hirahara`) / score=-2.000 / imputed_ratio=0.000
  - 10. `矢田　旭` (`Asahi Yada`) / score=-3.551 / imputed_ratio=0.000
- フィルタで除外された有力候補:
  - `樺山　諒乃介` (`Ryonosuke Kabayama`): 無条件順位 4 位 / score=0.627 / imputed_ratio=0.857

### ハイプレス・イニシエーター
- imputed_ratio フィルタ: `<= 0.25` を適用
- 公式 Top10:
  - 1. `髙橋　馨希` (`Yoshiki Takahashi`) / score=1.982 / imputed_ratio=0.000
  - 2. `加藤　潤也` (`Junya Kato`) / score=1.390 / imputed_ratio=0.000
  - 3. `奥村　晃司` (`Koji Okumura`) / score=1.112 / imputed_ratio=0.000
  - 4. `菊谷　篤資` (`Atsushi  Kikutani`) / score=1.065 / imputed_ratio=0.000
  - 5. `三田　尚希` (`Naoki Sanda`) / score=0.918 / imputed_ratio=0.000
  - 6. `佐々木　陽次` (`Yoji Sasaki`) / score=0.172 / imputed_ratio=0.000
  - 7. `井上　直輝` (`Naoki Inoue`) / score=-1.334 / imputed_ratio=0.000
  - 8. `矢田　旭` (`Asahi Yada`) / score=-1.419 / imputed_ratio=0.000
  - 9. `上野　瑶介` (`Yosuke Ueno`) / score=-2.294 / imputed_ratio=0.000
  - 10. `平原　隆暉` (`Ryuki Hirahara`) / score=-2.964 / imputed_ratio=0.000
- フィルタで除外された有力候補:
  - `樺山　諒乃介` (`Ryonosuke Kabayama`): 無条件順位 3 位 / score=1.373 / imputed_ratio=0.857
