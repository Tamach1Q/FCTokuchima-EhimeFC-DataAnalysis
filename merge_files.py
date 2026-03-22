import os
import glob
import pandas as pd
import numpy as np

# ==========================================
# 1. パスと基本設定
# ==========================================
BASE_DIR = '/Users/machidanoboruyuu/Library/CloudStorage/GoogleDrive-kmc2434@kamiyama.ac.jp/.shortcut-targets-by-id/15hhq0OywBt77uy9iydunzXsnyWMxZPhe/生データ/'
FB_DIR = os.path.join(BASE_DIR, 'football box')
SC_DIR = os.path.join(BASE_DIR, 'skill corner')
MASTER_FILE = 'master_name_mapping_final.csv'

# 分析対象とする最小の合計出場時間（分）。短すぎる選手をノイズとして弾く
MIN_MINUTES_THRESHOLD = 300 

print("--- Step 1: ファイルの収集 ---")
fb_files = glob.glob(os.path.join(FB_DIR, '**', '*.xlsx'), recursive=True)
sc_files = glob.glob(os.path.join(SC_DIR, '**', '*.csv'), recursive=True)
print(f"対象ファイル: FB {len(fb_files)}件 / SC {len(sc_files)}件")

# ==========================================
# 2. FBデータの結合と集計
# ==========================================
print("\n--- Step 2: FBデータの統合 ---")
# カテゴリ別に縦結合するための辞書
fb_categories = ['攻撃サマリー', 'エリア別シュート', 'エリア進入プレー', 'セットプレー得点', 
                 '守備サマリー', 'ゲインエリア', 'ゲイン結果', '方向別パス', '基本サマリー']

fb_dict = {cat: [] for cat in fb_categories}

# ファイル名からカテゴリを判定して読み込む
for f in fb_files:
    for cat in fb_categories:
        if cat in os.path.basename(f):
            df = pd.read_excel(f, engine='openpyxl')
            fb_dict[cat].append(df)
            break

# カテゴリごとに縦結合し、その後共通キーで横結合
df_fb_merged = None
merge_keys = ['チーム名', '選手名', '試合日']

for cat, dfs in fb_dict.items():
    if not dfs: continue
    df_cat = pd.concat(dfs, ignore_index=True)
    
    # 結合時の重複を防ぐため、キー以外の重複カラム名を削除（結果、Posなど）
    if df_fb_merged is not None:
        drop_cols = [c for c in df_cat.columns if c in df_fb_merged.columns and c not in merge_keys]
        df_cat = df_cat.drop(columns=drop_cols)
        df_fb_merged = pd.merge(df_fb_merged, df_cat, on=merge_keys, how='outer')
    else:
        df_fb_merged = df_cat

print(f"FBの全試合データを横結合しました（総レコード数: {len(df_fb_merged)}）")

# FBの指定変数リスト
fb_sum_vars = [
    'シュート', 'PA内シュート', 'PA内ゴール', 'PA外ゴール', 'PA進入', 'PA進入3プレー以内得点',
    'セットプレー5プレー以内得点', 'ボールゲイン', '相手陣での回数', 'ATでの回数',
    'ゲイン後至シュート', 'ゲイン後至PA進入', 'ゲイン後10秒未満でシュート', 
    'パス', '後方向パス', 'ラストパス', '30m進入', 'ニアゾーン進入', 'ドリブル'
]
fb_mean_vars = [
    'PA内シュート枠内率(%)', 'PA内シュート決定率(%)', 'タックル奪取率(%)', 
    '相手陣割合(%)', '平均ゲインライン(m)', '空中戦勝率(%)', 'パス成功率(%)', '後方向パス成功率(%)'
]

# 数値型への変換と欠損値埋め
for col in ['出場時間'] + fb_sum_vars + fb_mean_vars:
    if col in df_fb_merged.columns:
        df_fb_merged[col] = pd.to_numeric(df_fb_merged[col], errors='coerce').fillna(0)

# 選手ごとに集計
fb_agg_dict = {'出場時間': 'sum'}
for v in fb_sum_vars: 
    if v in df_fb_merged.columns: fb_agg_dict[v] = 'sum'
for v in fb_mean_vars: 
    if v in df_fb_merged.columns: fb_agg_dict[v] = 'mean'

df_fb_agg = df_fb_merged.groupby('選手名').agg(fb_agg_dict).reset_index()

# FB変数の90分換算 (per90)
for v in fb_sum_vars:
    if v in df_fb_agg.columns:
        df_fb_agg[f'{v}_per90'] = np.where(df_fb_agg['出場時間'] > 0, 
                                           (df_fb_agg[v] / df_fb_agg['出場時間']) * 90, 0)

# ==========================================
# 3. SCデータの結合と集計
# ==========================================
print("\n--- Step 3: SCデータの統合 ---")
df_sc_all = pd.concat([pd.read_csv(f) for f in sc_files], ignore_index=True)
print(f"SCの全試合データを結合しました（総レコード数: {len(df_sc_all)}）")

# SCの指定変数リスト
sc_sum_vars_tip = [
    'Sprint Count TIP', 'Sprint Distance TIP', 'Explosive Acceleration to Sprint Count TIP',
    'Explosive Acceleration to HSR Count TIP', 'High Acceleration Count TIP', 
    'Medium Acceleration Count TIP', 'High Deceleration Count TIP', 
    'Medium Deceleration Count TIP', 'Change of Direction Count TIP', 'HI Count TIP',
    'HSR Distance TIP', 'HSR Count TIP', 'Running Distance TIP', 'Distance TIP', 'HI Distance TIP'
]
sc_sum_vars_otip = [
    'Distance OTIP', 'Running Distance OTIP', 'HSR Distance OTIP', 'HSR Count OTIP',
    'Sprint Distance OTIP', 'Sprint Count OTIP', 'High Acceleration Count OTIP', 'HI Distance OTIP'
]
sc_sum_vars_all = [
    'High Acceleration Count', 'Explosive Acceleration to HSR Count', 
    'Explosive Acceleration to Sprint Count', 'Change of Direction Count'
]

# 数値型変換
for col in ['Minutes', 'Minutes TIP', 'Minutes OTIP', 'M/min OTIP', 'M/min', 'PSV-99'] + sc_sum_vars_tip + sc_sum_vars_otip + sc_sum_vars_all:
    if col in df_sc_all.columns:
        df_sc_all[col] = pd.to_numeric(df_sc_all[col], errors='coerce').fillna(0)

sc_agg_dict = {
    'Minutes': 'sum', 'Minutes TIP': 'sum', 'Minutes OTIP': 'sum',
    'M/min OTIP': 'mean', 'M/min': 'mean',
    'PSV-99': 'max'
}
for v in sc_sum_vars_tip + sc_sum_vars_otip + sc_sum_vars_all:
    if v in df_sc_all.columns: sc_agg_dict[v] = 'sum'

df_sc_agg = df_sc_all.groupby('Player').agg(sc_agg_dict).reset_index()

# SC変数の90分換算 (per90)
for v in sc_sum_vars_tip:
    if v in df_sc_agg.columns:
        df_sc_agg[f'{v}_per90'] = np.where(df_sc_agg['Minutes TIP'] > 0, (df_sc_agg[v] / df_sc_agg['Minutes TIP']) * 90, 0)
for v in sc_sum_vars_otip:
    if v in df_sc_agg.columns:
        df_sc_agg[f'{v}_per90'] = np.where(df_sc_agg['Minutes OTIP'] > 0, (df_sc_agg[v] / df_sc_agg['Minutes OTIP']) * 90, 0)
for v in sc_sum_vars_all:
    if v in df_sc_agg.columns:
        df_sc_agg[f'{v}_per90'] = np.where(df_sc_agg['Minutes'] > 0, (df_sc_agg[v] / df_sc_agg['Minutes']) * 90, 0)

# ==========================================
# 4. マスターリストを使ったFBとSCのマージ
# ==========================================
print("\n--- Step 4: 最終マージと出力 ---")
master = pd.read_csv(MASTER_FILE)
# 正しくマージされた366人（+手動で追加した分）のみを対象とする
# ※不要な末尾のゴミデータを除外したい場合は、事前に master.csv をエディタで整理しておくことを推奨します

df_final = pd.merge(master, df_fb_agg, left_on='FB_Name', right_on='選手名', how='inner')
df_final = pd.merge(df_final, df_sc_agg, left_on='SC_Name', right_on='Player', how='inner')

# 出場時間によるノイズ除去（例: 3年で合計300分未満の選手は足切り）
initial_len = len(df_final)
df_final = df_final[df_final['出場時間'] >= MIN_MINUTES_THRESHOLD]
filtered_len = len(df_final)

# ファイルへ出力
output_file = 'clustering_base_data.csv'
df_final.to_csv(output_file, index=False, encoding='utf-8-sig')

print(f"\n✨ 完了！ {output_file} を作成しました。")
print(f"✅ マスター名簿のうち {initial_len} 名のデータを結合成功。")
print(f"✅ 出場時間 {MIN_MINUTES_THRESHOLD}分未満の選手を除外した結果、最終的な分析対象は 【 {filtered_len} 名 】 です。")