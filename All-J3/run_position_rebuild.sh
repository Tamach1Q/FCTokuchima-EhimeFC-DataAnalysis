#!/bin/bash
# ============================================================================
# ワンショット実行スクリプト: SC 細分類ポジション復元
# ============================================================================
# 使い方: conda ehime_fc 環境で実行
#   conda activate ehime_fc
#   cd /Users/machidanoboruyuu/Desktop/FCTokushima-EhimeFC-DataAnalysis
#   bash All-J3/run_position_rebuild.sh
# ============================================================================

set -e

cd /Users/machidanoboruyuu/Desktop/FCTokushima-EhimeFC-DataAnalysis

echo "=== Step 1: SC raw データから中間CSV抽出 (Python) ==="
python All-J3/extract_sc_position_data.py

echo ""
echo "=== Step 2: ポジション復元・マージ処理 ==="
python All-J3/rebuild_sc_detailed_positions.py

echo ""
echo "=== 全処理完了 ==="
