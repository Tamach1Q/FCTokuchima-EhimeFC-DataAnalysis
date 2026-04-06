# SDD: 2024-2025 純J3 全ポジション前処理

## 目的

`football box` と `skill corner` の生データから、`2024-2025` シーズンの `J3` を対象にした選手単位の前処理データを作成する。

前回までの J3 前処理は、既存の `master_name_mapping_final.csv` に依存していたため、実質的に `FW中心` のデータになっていた。  
本仕様では、前線限定の状態から `DF / MF / FW` へ対象を広げ、`全ポジション版` の土台を作る。

## 対象

- 対象年度: `2024`, `2025`
- 対象リーグ: `J3`
- 対象ソース: `football box`, `skill corner`
- 対象ポジション: `DF`, `MF`, `FW`
- 出力用途: クラスタリング前のベースデータ作成

## 対象外

- `2026` シーズン
- `J1`, `J2`, ルヴァンカップ
- `既存 clustering_base_data.csv` の置き換え
- `GK` の FB+SC 統合
- 自動拡張した名前マッピングの `master_name_mapping_final.csv` への自動書き戻し

### なぜ 2026 を対象外にしたか

`2026` を除外した理由は、現時点の生データ構造では `J3のみ` を安全に切り出せないため。

- `football box` の `2026` データは `J2・J3百年構想リーグ` という単一フォルダにまとまっている
- `skill corner` の `2026` データも `J2・J3百年構想リーグ` という単一フォルダにまとまっている
- `football box` 側の `大会` 列も `J2/J3 100` に統一されており、行単位で `J2` と `J3` を区別できない
- `skill corner` 側の `Competition` 列も `J2/J3 100 Year Vision League` に統一されており、同様に行単位で `J2` と `J3` を区別できない

そのため、`2026` を含めるにはリーグ名だけでは不十分で、少なくとも `season + team -> league` を持つ補助マスターが必要になる。

今回は、

- `純J3` を明確に作ること
- 手順を単純化して再現性を持たせること
- まず `2024-2025` の J3 で全ポジション版の前処理を固めること

を優先し、`2026` は意図的に対象外とした。

### なぜ GK を対象外にしたか

今回の全ポジション化は `DF / MF / FW` までであり、`GK` は統合対象外とする。

- `football box` 側には `GK` が存在する
- 一方で `skill corner/2024/J3` と `skill corner/2025/J3` には `GK` の `Position Group` が存在しない
- そのため、現行の `FB + SC` 統合前処理では、`GK` だけ `inner join` の相手がいない

`2024-2025 / J3 / football box` では、`出場時間 >= 300分` の `GK` が `53名` いるが、現時点の SkillCorner データ構造では安全に統合できない。  
従って、本仕様の `全ポジション版` は `フィールドプレーヤー全体` を意味する。

## 入力

- `football box/2024/J3/*.xlsx`
- `football box/2025/J3/*.xlsx`
- `skill corner/2024/J3/*.csv`
- `skill corner/2025/J3/*.csv`
- `csv/master_name_mapping_final.csv`

## 出力

- `csv/clustering_base_data_j3_2024_2025.csv`
  - J3限定の統合済みベースデータ
- `csv/j3_2024_2025_valid_name_mapping.csv`
  - J3対象として採用した名前マッピング
  - `manual_master` と `auto_j3_outfield` を区別して保持する
- `csv/j3_2024_2025_mapping_issues.csv`
  - 自動採用に至らなかった候補一覧
  - `low_confidence_top_candidate`, `sc_goalkeeper_not_available` などを記録する

## 運用メモ

### 引退選手について

`2026年4月1日` 時点で、関連CSVに含まれる名前のうち、公式に現役引退が確認できている選手は以下の2名。

- `豊田　陽平`
- `富山　貴光`

根拠:

- `豊田　陽平` は `2024シーズン限り` での現役引退が `Jリーグ公式` で発表済み
- `富山　貴光` は `2025シーズン限り` での現役引退が `RB大宮アルディージャ公式` で発表済み

現行の前処理では、引退を理由にした自動除外は行わない。  
この情報は、分析結果の解釈時に参照する注記として扱う。

### 手動で確定した名前マッピング補正

`master_name_mapping_final.csv` には、以下の手動補正を反映済み。

- `宇高　魁人 -> Kaito Utaka`
  - SC 実データ上の表記に合わせて `Kaito Utaka` を採用
- `木實　快斗 -> Kaito Konomi`
- `鈴木　国友 -> Kunitomo Suzuki`
- `鈴木　拳士郎 -> Kenshiro Suzuki`
- `大野　耀平 -> Yohei Ono`
- `豊田　陽平 -> Yohei Toyoda`

### 現行出力の件数

`2026-04-01` 時点の全ポジション版再生成結果は以下。

- `csv/j3_2024_2025_valid_name_mapping.csv`: `380件`
  - `manual_master: 127件`
  - `auto_j3_outfield: 253件`
- `csv/j3_2024_2025_mapping_issues.csv`: `341件`
  - `low_confidence_top_candidate: 287件`
  - `sc_goalkeeper_not_available: 53件`
  - `unsupported_fb_position: 1件`
- `csv/clustering_base_data_j3_2024_2025.csv`: `360件`
  - `DF: 139件`
  - `MF: 99件`
  - `FW: 122件`

## 設計方針

### 1. 取り込み範囲をフォルダで限定する

年・リーグの条件は、出力後にフィルタするのではなく、入力ファイル収集時点で `2024-2025/J3` に限定する。

### 2. FB と SC は別々に選手単位集計する

- FB は既存 `merge_files.py` と同じ考え方でカテゴリ別ファイルを試合単位で横結合し、その後に選手単位へ集計する
- SC は試合別CSVを縦結合し、選手単位へ集計する

### 3. SC 2024 の列名を標準化する

`skill corner` の `2024/J3` は snake_case、`2025/J3` は Title Case になっている。  
実装では `2025` の列名を標準スキーマとし、`2024` の主要列をそれに揃える。

### 4. 名前マッピングは 2 段階で作る

#### 4-1. 手修正済みマスターを seed にする

最初に `master_name_mapping_final.csv` を読み込み、

- `FB_Name` が `2024-2025/J3` の FB 集計に存在する
- `SC_Name` が `2024-2025/J3` の SC 集計に存在する

行だけを採用候補にする。

この段階で `FB_Name` または `SC_Name` が重複する行は除外し、監査CSVへ送る。

#### 4-2. J3 限定で自動拡張する

手修正済みマスターで拾えない `DF / MF / FW` を対象に、J3 のみで自動マッチングを行う。  
この自動拡張は `master_name_mapping_final.csv` を書き換えず、J3 前処理の生成時だけ適用する。

### 5. 自動マッチングは名前だけで決めない

自動拡張では、以下の情報を併用する。

- `年度 + チーム` ごとの出場時間ベクトル
- 日本語名をローマ字化した名前類似度
- 総出場時間の近さ
- FB の `Pos` と SC の `Position Group` を粗く揃えたポジション一致

#### SC のポジションを FB に揃えるルール

- `Central Defender -> DF`
- `Full Back -> DF`
- `Midfield -> MF`
- `Wide Attacker -> FW`
- `Center Forward -> FW`

### 6. 自動採用は高信頼帯に限定する

候補ごとに以下の総合スコアを作る。

- `vector similarity * 0.52`
- `name similarity * 0.30`
- `minutes ratio * 0.10`
- `position match * 0.08`

自動採用条件は次の 3 つをすべて満たすこと。

- `Top_Score >= 82`
- `Gap_to_Second >= 12`
- `Name_Score >= 70`

ここを満たさない候補は、`csv/j3_2024_2025_mapping_issues.csv` に残して人手確認対象にする。

### 7. 最終マージ後に出場時間閾値を適用する

現行ロジックに合わせて、FB の `出場時間` が `300分以上` の選手のみを最終出力に残す。

自動マッチングも、最終出力対象に直結するよう `FB 出場時間 >= 300分` の未対応選手を優先して行う。

## 処理手順

1. `football box/2024/J3` と `football box/2025/J3` から対象カテゴリの Excel を収集する
2. FB のカテゴリ別データを `season + チーム名 + 選手名 + 試合日` で横結合する
3. FB の数値列を整形し、選手単位に `sum / mean / per90` を作る
4. `skill corner/2024/J3` と `skill corner/2025/J3` の CSV を収集する
5. SC 2024 の列名を 2025 形式へ正規化する
6. SC の数値列を整形し、選手単位に `sum / mean / per90` を作る
7. `master_name_mapping_final.csv` を seed にして J3 で存在確認する
8. 手修正済み seed で拾えない `DF / MF / FW` について、自動マッチング候補を作る
9. `Top_Score`, `Gap_to_Second`, `Name_Score` の閾値で高信頼候補だけを採用する
10. 低信頼候補と `GK` を `csv/j3_2024_2025_mapping_issues.csv` に残す
11. `FB_Name -> 選手名`, `SC_Name -> Player` で `inner join` する
12. `出場時間 >= 300` を適用する
13. ベースデータと監査CSVを出力する

## 実行手順

1. 仮想環境を有効化する

```bash
source env/bin/activate
```

2. J3 前処理スクリプトを実行する

```bash
python build_j3_2024_2025_base_data.py
```

3. 出力件数と監査CSVを確認する

- `csv/clustering_base_data_j3_2024_2025.csv`
- `csv/j3_2024_2025_valid_name_mapping.csv`
- `csv/j3_2024_2025_mapping_issues.csv`

## 検証観点

- SC 2024 と SC 2025 の両方が集計対象に入っていること
- `FB_Name`, `SC_Name`, `Player` が最終出力でユニークであること
- 前線以外の `DF / MF` が最終出力に含まれていること
- `GK` は `sc_goalkeeper_not_available` として監査CSVに残ること
- `manual_master` と `auto_j3_outfield` の両方が `valid_name_mapping` に記録されること
- `出場時間 >= 300` が効いていること
- 手動補正が `master_name_mapping_final.csv` に反映されていること
- 引退選手情報は除外条件ではなく注記として扱われていること

## 実装ファイル

- `build_j3_2024_2025_base_data.py`
