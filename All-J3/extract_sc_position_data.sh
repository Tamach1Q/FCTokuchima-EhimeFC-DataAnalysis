#!/bin/bash
# ============================================================================
# extract_sc_position_data.sh
# ============================================================================
# 目的: 生データ/skill corner の raw CSV から position 関連列を抽出し、
#       中間CSV (sc_raw_position_data.csv) を All-J3/J3_csv/ に出力する
#
# 使い方:
#   1. macOS「システム設定 > プライバシーとセキュリティ > フルディスクアクセス」で
#      Terminal.app (または iTerm 等) を許可する
#   2. このスクリプトを実行:
#      bash All-J3/extract_sc_position_data.sh
# ============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
OUTPUT_DIR="${SCRIPT_DIR}/J3_csv"
OUTPUT_FILE="${OUTPUT_DIR}/sc_raw_position_data.csv"

# raw データの場所 (シンボリックリンク経由)
RAW_SC_DIR="${SCRIPT_DIR}/../生データ/skill corner"

# Google Drive パスもフォールバックとして
GDRIVE_SC_DIR="/Users/machidanoboruyuu/Library/CloudStorage/GoogleDrive-kmc2434@kamiyama.ac.jp/.shortcut-targets-by-id/15hhq0OywBt77uy9iydunzXsnyWMxZPhe/生データ/skill corner"

# アクセス可能なパスを選択
SC_DIR=""
if [ -d "$RAW_SC_DIR" ] && ls "$RAW_SC_DIR" >/dev/null 2>&1; then
    SC_DIR="$RAW_SC_DIR"
elif [ -d "$GDRIVE_SC_DIR" ] && ls "$GDRIVE_SC_DIR" >/dev/null 2>&1; then
    SC_DIR="$GDRIVE_SC_DIR"
else
    echo "ERROR: SkillCorner raw データにアクセスできません。"
    echo "macOS「システム設定 > プライバシーとセキュリティ > フルディスクアクセス」で"
    echo "Terminal.app を許可してから再実行してください。"
    exit 1
fi

echo "SC raw データディレクトリ: $SC_DIR"
echo "出力先: $OUTPUT_FILE"

mkdir -p "$OUTPUT_DIR"

# ヘッダー出力
echo "source_year,player_name,team_name,match_id,match_date,competition_name,season_name,position,position_group,minutes_full_all" > "$OUTPUT_FILE"

file_count=0
record_count=0

for year in 2024 2025; do
    j3_dir="${SC_DIR}/${year}/J3"
    if [ ! -d "$j3_dir" ]; then
        echo "WARNING: $j3_dir が見つかりません。スキップします。"
        continue
    fi

    for csv_file in "${j3_dir}"/*.csv; do
        [ -f "$csv_file" ] || continue
        file_count=$((file_count + 1))

        # ヘッダー行から列インデックスを特定
        # player_name(1), team_name(5), match_id(8), match_date(9),
        # competition_name(10), season_name(12), position(15), position_group(16), minutes_full_all(17)
        # (0-indexed from the raw file)
        awk -F',' -v year="$year" '
        NR == 1 {
            # ヘッダーから列インデックスを動的に取得
            for (i = 1; i <= NF; i++) {
                gsub(/^[[:space:]]+|[[:space:]]+$/, "", $i)
                if ($i == "player_name") col_player = i
                if ($i == "team_name") col_team = i
                if ($i == "match_id") col_match_id = i
                if ($i == "match_date") col_match_date = i
                if ($i == "competition_name") col_comp = i
                if ($i == "season_name") col_season = i
                if ($i == "position") col_pos = i
                if ($i == "position_group") col_pos_group = i
                if ($i == "minutes_full_all") col_minutes = i
            }
            next
        }
        NR > 1 && $col_player != "" {
            printf "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n", \
                year, $col_player, $col_team, $col_match_id, $col_match_date, \
                $col_comp, $col_season, $col_pos, $col_pos_group, $col_minutes
        }
        ' "$csv_file" >> "$OUTPUT_FILE"
    done

    echo "  ${year}/J3: 処理済み"
done

record_count=$(tail -n +2 "$OUTPUT_FILE" | wc -l | tr -d ' ')
echo ""
echo "完了: ${file_count} ファイル, ${record_count} レコード"
echo "出力: $OUTPUT_FILE"
