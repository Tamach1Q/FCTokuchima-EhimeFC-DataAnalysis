import pandas as pd

df = pd.read_csv('cf_name_mapping_fixed.csv')

# 1. 同じ日本語名(FB_Name)が複数の英語名(SC_Name)に割り当てられていないかチェック
# これに引っかかるのは、ほぼ間違いなく誤マッチングです
duplicates = df[df['FB_Name'].duplicated(keep=False)].dropna(subset=['FB_Name'])

# 2. スコアが100未満かつNoneではないものを抽出
check_needed = df[(df['Match_Score'] < 100) & (df['FB_Name'].notna())]

print("⚠️ 重複割り当て（要修正）:")
print(duplicates.sort_values('FB_Name')[['SC_Name', 'FB_Name', 'Match_Score']])

print("\n🔍 スコア100未満（目視推奨）:")
print(check_needed[['SC_Name', 'FB_Name', 'Match_Score']])