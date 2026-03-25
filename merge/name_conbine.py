import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CSV_DIR = PROJECT_ROOT / "csv"

def clean_sc_name(name):
    """Skill Corner側の英語名の表記揺れを修正する関数"""
    if pd.isna(name) or name in ['Not Found', 'None', '']:
        return None
    
    name = str(name)
    # 1. マクロン（長音記号）を通常のアルファベットに変換
    replacements = {
        'ū': 'u', 'ō': 'o', 'ī': 'i', 'ē': 'e', 'ā': 'a',
        'Ū': 'U', 'Ō': 'O', 'Ī': 'I', 'Ē': 'E', 'Ā': 'A'
    }
    for k, v in replacements.items():
        name = name.replace(k, v)
        
    # 2. 余分なスペース（連続するスペースなど）を1つに統一し、前後の空白を削除
    name = ' '.join(name.split())
    
    return name

# ==========================================
# 1. 3つのデータの読み込み
# ==========================================
df1 = pd.read_csv('fb_sc_name_mapping.csv')
df2 = pd.read_csv('cf_name_mapping_v3.csv')
df3 = pd.read_csv('final_mapped_players.csv')

# ==========================================
# 2. 必要なカラム（FB_Name, SC_Name）だけの抽出と統一
# ==========================================
# それぞれのDFから抽出
map1 = df1[['FB_Name', 'SC_Name']].copy()
map2 = df2[['FB_Name', 'SC_Name']].copy()
map3 = df3[['FB_Name', 'SC_Name']].copy()

# 縦に結合（上から順に優先されます）
df_combined = pd.concat([map3, map1, map2], ignore_index=True)

# ==========================================
# 3. データのクリーニング（表記揺れ修正と無効値の除外）
# ==========================================
# SC_Nameの表記揺れを修正
df_combined['SC_Name'] = df_combined['SC_Name'].apply(clean_sc_name)

# 変換後に None になった行（Not Foundなど）や、FB_Nameが空の行を削除
df_cleaned = df_combined.dropna(subset=['FB_Name', 'SC_Name']).copy()

# ==========================================
# 4. 重複の排除（FB_Nameを基準に、最も上にある有効なデータを残す）
# ==========================================
df_final = df_cleaned.drop_duplicates(subset=['FB_Name'], keep='first')

# 日本語名（FB_Name）の全角スペース等も念のため標準化したい場合はここに追加可能ですが、
# Football Box側の生データに合わせるため今回はそのまま保持します。

# ==========================================
# 5. 結果の出力
# ==========================================
output_filename = CSV_DIR / 'master_name_mapping_final.csv'
output_filename.parent.mkdir(parents=True, exist_ok=True)
df_final.to_csv(output_filename, index=False, encoding='utf-8-sig')

print(f"結合完了！総マッチング数: {len(df_final)} 人")
print(f"ファイル '{output_filename}' に出力しました。")

# 確認用プレビュー
print("\n=== クリーニング済みデータ サンプル ===")
print(df_final.head(10))
