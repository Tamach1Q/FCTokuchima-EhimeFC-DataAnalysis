import pandas as pd
import pykakasi
from thefuzz import process

# 1. カカシ（漢字→ローマ字変換）の初期化
kks = pykakasi.kakasi()

def to_romaji(text):
    if pd.isna(text): return ""
    # 全角スペースを消して純粋な名前にする
    text = str(text).replace("　", "").replace(" ", "")
    # ヘボン式ローマ字に変換して結合（例: 山見大登 -> yamamihirito）
    return "".join([item['hepburn'] for item in kks.convert(text)])

# 2. データの読み込み
df_sc = pd.read_csv('sc_unique_players.csv')
df_fb = pd.read_csv('fb_unique_players.csv')

# 3. FB（漢字）の辞書作成: {'romaji': '漢字（全角スペースあり）'}
fb_map = {}
for kanji_name in df_fb['FB_Name'].dropna():
    romaji = to_romaji(kanji_name)
    fb_map[romaji] = kanji_name

fb_romaji_list = list(fb_map.keys())

# 4. SC（英語）と文字列類似度マッチング
results = []
for sc_name in df_sc['SC_Name'].dropna():
    # 英語名もスペースを消して小文字に（例: Naoto Miki -> naotomiki）
    sc_clean = str(sc_name).replace(" ", "").lower()
    
    # thefuzzで最も文字列が近いローマ字を探し出し、一致度スコア（0〜100）を取得
    best_match, score = process.extractOne(sc_clean, fb_romaji_list)
    
    # スコアが70点以上なら「同一人物」とみなす（閾値は調整可能）
    if score >= 70:
        fb_kanji = fb_map[best_match]
    else:
        fb_kanji = None # 見つからなかった場合は空欄
        
    results.append({'SC_Name': sc_name, 'FB_Name': fb_kanji, 'Match_Score': score})

# 5. 結果の保存
df_result = pd.DataFrame(results)
# 精度確認のため、スコアが低い順に並べ替えて出力
df_result.sort_values('Match_Score').to_csv('cf_name_mapping_fixed.csv', index=False, encoding='utf-8-sig')

print("✅ 名寄せ完了！低スコアの抽出結果プレビュー:")
print(df_result.sort_values('Match_Score').head(10))