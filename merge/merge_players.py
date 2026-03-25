import pandas as pd
import requests
import time
import re
from pathlib import Path
from difflib import SequenceMatcher

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CSV_DIR = PROJECT_ROOT / "csv"

# --- 1. データ読み込み ---
df_fb = pd.read_csv(CSV_DIR / 'fb_unique_players.csv')
df_sc = pd.read_csv(CSV_DIR / 'sc_unique_players.csv')

def normalize_name(text):
    """ローマ字の長音記号を取り除き、小文字化し、空白や記号を消す"""
    text = str(text).lower()
    for k, v in {'ū':'u', 'ō':'o', 'ā':'a', 'ī':'i', 'ē':'e', '-':'', "'":''}.items():
        text = text.replace(k, v)
    return text.replace(' ', '')

# SC側データを正規化（検索用）
sc_names_norm = {sc: normalize_name(sc) for sc in df_sc['SC_Name'].dropna()}
unmatched_sc = list(sc_names_norm.keys())

def fetch_romaji_from_wikipedia(player_name):
    """Wikipedia APIを使って正しい英語名・ローマ字を取得する"""
    name_clean = str(player_name).replace('　', ' ').strip()
    session = requests.Session()
    url = "https://ja.wikipedia.org/w/api.php"
    
    # 1. Wikipediaで「〇〇 サッカー」として検索し、ページを特定
    search_params = {
        "action": "query", "list": "search", "format": "json",
        "srsearch": f"{name_clean} サッカー"
    }
    try:
        res = session.get(url, params=search_params, timeout=5).json()
        if not res['query']['search']:
            return None
        title = res['query']['search'][0]['title']
        
        # 2. 英語版のタイトル、または日本語版の冒頭文を取得
        page_params = {
            "action": "query", "prop": "langlinks|extracts", "format": "json",
            "titles": title, "lllang": "en", "exintro": True, "explaintext": True
        }
        page_res = session.get(url, params=page_params, timeout=5).json()
        pages = page_res['query']['pages']
        
        for page_id, info in pages.items():
            # パターンA: 英語版Wikipediaのタイトルを取得 (一番確実)
            if 'langlinks' in info:
                en_title = info['langlinks'][0]['*']
                en_title = re.sub(r'\s*\(.*\)', '', en_title) # (footballer) 等を削除
                return en_title.lower()
                
            # パターンB: 英語ページがない場合、日本語版の冒頭文からローマ字を抽出
            if 'extract' in info:
                extract = info['extract']
                # 例: 「（Sano Ryuma、2000年...）」からローマ字を抽出
                match = re.search(r'\(([A-Za-z\s\-]+)[、,]', extract)
                if match:
                    return match.group(1).lower().strip()
    except Exception:
        pass
    return None

# --- 3. メイン処理 ---
results = []
print("Wikipediaから選手名を検索してマージを開始します。（※API制限を避けるため数分かかります）")

for idx, row in df_fb.iterrows():
    fb_name = row['FB_Name']
    if pd.isna(fb_name): continue
    
    print(f"[{idx+1}/{len(df_fb)}] 検索中: {fb_name} ... ", end="")
    
    # ネットから正しいローマ字を取得
    wiki_romaji = fetch_romaji_from_wikipedia(fb_name)
    best_match = None
    best_score = 0
    
    if wiki_romaji:
        wiki_norm = normalize_name(wiki_romaji)
        
        # SC側のデータと照合
        for sc_name in unmatched_sc:
            sc_norm = sc_names_norm[sc_name]
            
            # 完全一致 または 包含関係
            if wiki_norm == sc_norm or wiki_norm in sc_norm or sc_norm in wiki_norm:
                best_match = sc_name
                best_score = 100
                break
                
            # 部分一致 (姓名逆転などに備える)
            similarity = SequenceMatcher(None, wiki_norm, sc_norm).ratio() * 100
            if similarity > best_score:
                best_score = similarity
                best_match = sc_name

    # スコアが80以上なら同一人物として採用
    if best_match and best_score >= 80:
        results.append({
            'FB_Name': fb_name,
            'Fetched_Romaji': wiki_romaji,
            'SC_Name': best_match,
            'Score': round(best_score, 1)
        })
        unmatched_sc.remove(best_match)
        print(f"✓ マッチ成功 ({best_match})")
    else:
        results.append({
            'FB_Name': fb_name,
            'Fetched_Romaji': wiki_romaji if wiki_romaji else "情報取得できず",
            'SC_Name': "Not Found",
            'Score': round(best_score, 1)
        })
        print("✗ マッチ失敗")
    
    # サーバー負荷軽減のため0.5秒待機
    time.sleep(0.5) 

# --- 4. 結果保存 ---
df_results = pd.DataFrame(results)
df_results.sort_values(by='Score', ascending=False, inplace=True)
output_file = CSV_DIR / 'wiki_mapped_players.csv'
output_file.parent.mkdir(parents=True, exist_ok=True)
df_results.to_csv(output_file, index=False, encoding='utf-8-sig')

print(f"\n処理完了！ 結果を '{output_file}' に保存しました。")
