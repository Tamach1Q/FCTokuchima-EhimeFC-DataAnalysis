import os
import glob
import pandas as pd

# ==========================================
# 1. 3年分のデータを網羅するためのパス設定
# ==========================================
BASE_DIR = '/Users/machidanoboruyuu/Library/CloudStorage/GoogleDrive-kmc2434@kamiyama.ac.jp/.shortcut-targets-by-id/15hhq0OywBt77uy9iydunzXsnyWMxZPhe/生データ/'

# 「2026」の指定を外し、football box / skill corner フォルダ全体を対象にする
FB_DIR = os.path.join(BASE_DIR, 'football box')
SC_DIR = os.path.join(BASE_DIR, 'skill corner')

print("3年分（2024〜2026年）のファイルを検索中...")
# サブフォルダ（各年度・各リーグ）内のファイルをすべて再帰的に取得
fb_files = glob.glob(os.path.join(FB_DIR, '**', '*.xlsx'), recursive=True)
sc_files = glob.glob(os.path.join(SC_DIR, '**', '*.csv'), recursive=True)

print(f"見つかったFBファイル (Excel): {len(fb_files)}件")
print(f"見つかったSCファイル (CSV): {len(sc_files)}件")

# ==========================================
# 2. 読み込みテスト（ヘッダーのズレを修正）
# ==========================================
if fb_files:
    print("\n--- FBデータの読み込みテスト ---")
    # skiprows=1 を削除し、0行目を正しくヘッダーとして読み込む
    df_fb_test = pd.read_excel(fb_files[0], engine='openpyxl')
    print(f"ファイル: {os.path.basename(fb_files[0])}")
    print(f"正しいカラム名が取れているか確認: {df_fb_test.columns.tolist()[:10]}")

if sc_files:
    print("\n--- SCデータの読み込みテスト ---")
    df_sc_test = pd.read_csv(sc_files[0])
    print(f"ファイル: {os.path.basename(sc_files[0])}")
    print(f"カラム: {df_sc_test.columns.tolist()[:10]}")