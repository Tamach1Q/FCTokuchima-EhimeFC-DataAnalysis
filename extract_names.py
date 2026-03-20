import pandas as pd
from pathlib import Path

# 生データの親フォルダのパス（まっちーの環境に合わせています）
base_dir = Path('/Users/machidanoboruyuu/Desktop/FCTokushima-EhimeFC-DataAnalysis/生データ')

# 重複を弾くためにset（集合）を用意
fb_players = set()
sc_players = set()

print("⚽️ Football BoxからFWの選手リストを抽出中...")
# FBは「エリア進入プレー」のExcelだけを狙い撃ちして高速化
for fb_file in base_dir.rglob('football box/**/選手データ_エリア進入プレー_試合別.xlsx'):
    try:
        # ※Excelの読み込みは少し時間がかかります
        df = pd.read_excel(fb_file, sheet_name='sheet1')
        # PosがFWの選手名だけを抽出して追加
        fws = df[df['Pos'] == 'FW']['選手名'].dropna().unique()
        fb_players.update(fws)
    except Exception as e:
        print(f"Error reading {fb_file.name}: {e}")

print("🏃‍♂️ Skill CornerからCenter Forwardの選手リストを抽出中...")
# SCは1試合1ファイルなので全CSVを読み込む
for sc_file in base_dir.rglob('skill corner/**/*.csv'):
    try:
        # 必要なカラムだけ読み込むとメモリ節約＆高速化できます
        df = pd.read_csv(sc_file, usecols=['Player', 'Position'])
        cfs = df[df['Position'] == 'Center Forward']['Player'].dropna().unique()
        sc_players.update(cfs)
    except Exception as e:
        pass # 関係ないCSV（マスタなど）はスキップ

# 抽出したリストをDataFrameにしてCSVに書き出し
# （※Excelで文字化けしないように utf-8-sig を指定）
pd.DataFrame({'FB_Name': list(fb_players)}).to_csv('fb_unique_players.csv', index=False, encoding='utf-8-sig')
pd.DataFrame({'SC_Name': list(sc_players)}).to_csv('sc_unique_players.csv', index=False, encoding='utf-8-sig')

print(f"\n✅ 抽出完了！")
print(f"Football BoxのFW: {len(fb_players)}人")
print(f"Skill CornerのCF: {len(sc_players)}人")