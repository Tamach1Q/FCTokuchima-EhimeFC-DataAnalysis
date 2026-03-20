import pandas as pd
from pathlib import Path
from difflib import SequenceMatcher
import pykakasi

def normalize_text(s):
    if pd.isna(s):
        return ""
    s = str(s).lower().strip()
    s = s.replace('　', ' ')
    return s

def romaji_to_hiragana(romaji_str):
    """ローマ字をひらがなに変換"""
    romaji_map = {
        'a': 'あ', 'i': 'い', 'u': 'う', 'e': 'え', 'o': 'お',
        'ka': 'か', 'ki': 'き', 'ku': 'く', 'ke': 'け', 'ko': 'こ',
        'ga': 'が', 'gi': 'ぎ', 'gu': 'ぐ', 'ge': 'げ', 'go': 'ご',
        'sa': 'さ', 'si': 'し', 'shi': 'し', 'su': 'す', 'se': 'せ', 'so': 'そ',
        'za': 'ざ', 'zi': 'じ', 'ji': 'じ', 'zu': 'ず', 'ze': 'ぜ', 'zo': 'ぞ',
        'ta': 'た', 'ti': 'ち', 'chi': 'ち', 'tu': 'つ', 'tsu': 'つ', 'te': 'て', 'to': 'と',
        'da': 'だ', 'di': 'ぢ', 'du': 'づ', 'de': 'で', 'do': 'ど',
        'na': 'な', 'ni': 'に', 'nu': 'ぬ', 'ne': 'ね', 'no': 'の',
        'ha': 'は', 'hi': 'ひ', 'hu': 'ふ', 'fu': 'ふ', 'he': 'へ', 'ho': 'ほ',
        'ba': 'ば', 'bi': 'び', 'bu': 'ぶ', 'be': 'べ', 'bo': 'ぼ',
        'pa': 'ぱ', 'pi': 'ぴ', 'pu': 'ぷ', 'pe': 'ぺ', 'po': 'ぽ',
        'ma': 'ま', 'mi': 'み', 'mu': 'む', 'me': 'め', 'mo': 'も',
        'ya': 'や', 'yu': 'ゆ', 'yo': 'よ',
        'ra': 'ら', 'ri': 'り', 'ru': 'る', 're': 'れ', 'ro': 'ろ',
        'wa': 'わ', 'wi': 'ゐ', 'we': 'ゑ', 'wo': 'を', 'n': 'ん',
    }
    
    romaji = romaji_str.lower().strip()
    hiragana = ""
    i = 0
    
    while i < len(romaji):
        if romaji[i] == ' ':
            hiragana += ' '
            i += 1
            continue
        
        matched = False
        if i <= len(romaji) - 3:
            three_char = romaji[i:i+3]
            if three_char in romaji_map:
                hiragana += romaji_map[three_char]
                i += 3
                matched = True
        
        if not matched and i <= len(romaji) - 2:
            two_char = romaji[i:i+2]
            if two_char in romaji_map:
                hiragana += romaji_map[two_char]
                i += 2
                matched = True
        
        if not matched:
            if romaji[i] in romaji_map:
                hiragana += romaji_map[romaji[i]]
            elif romaji[i] in 'āáã':
                hiragana += 'あ'
            elif romaji[i] in 'īí':
                hiragana += 'い'
            elif romaji[i] in 'ūú':
                hiragana += 'う'
            elif romaji[i] in 'ēé':
                hiragana += 'え'
            elif romaji[i] in 'ōó':
                hiragana += 'お'
            i += 1
    
    return normalize_text(hiragana)

# チーム名マッピング
TEAM_MAPPING = {
    "Tokushima Vortis": "徳島",
    "Ehime FC": "愛媛",
    "Nara Club": "奈良",
    "Gainare Tottori": "鳥取",
    "Giravanz Kitakyushu": "北九州",
    "AC Parceiro Nagano": "長野",
    "Kataller Toyama": "富山",
    "Albirex Niigata": "新潟",
    "Matsumoto Yamaga FC": "松本",
    "Shonan Bellmare": "湘南",
    "FC Imabari": "今治",
    "Ishikawa FC Zweigen Kanazawa": "金沢",
    "Jubilo Iwata": "磐田",
    "Sagan Tosu": "鳥栖",
    "FC Azul Claro Numazu": "沼津",
    "FC Tokyo": "FC東京",
    "FC Gifu": "岐阜",
    "Fagiano Okayama": "岡山",
    "Fujieda MYFC": "藤枝",
    "Fukushima United FC": "福島",
    "Hokkaido Consadole Sapporo": "札幌",
    "Iwaki SC": "岩手",
    "JEF United Ichihara Chiba": "千葉",
    "Kagoshima United FC": "鹿児島",
    "Kamatamare Sanuki": "讃岐",
    "Kashima Antlers": "鹿島",
    "Kashiwa Reysol": "柏",
    "Kawasaki Frontale": "川崎F",
    "Kochi United SC": "高知",
    "Kyoto Sanga FC": "京都",
    "MIO Biwako Shiga": "滋賀",
    "Mito Hollyhock": "水戸",
    "Montedio Yamagata": "山形",
    "Nagoya Grampus": "名古屋",
    "Oita Trinita": "大分",
    "Omiya Ardija": "大宮",
    "Reilac Shiga FC": "滋賀",
    "Renofa Yamaguchi": "山口",
    "Roasso Kumamoto": "熊本",
    "SC Sagamihara": "相模原",
    "Sanfrecce Hiroshima": "広島",
    "Shimizu S-Pulse": "清水",
    "Tegevajaro Miyazaki FC": "宮崎",
    "ThespaKusatsu Gunma": "群馬",
    "Tochigi City": "栃木C",
    "Tochigi SC": "栃木SC",
    "Tokyo Verdy": "東京V",
    "Urawa Red Diamonds": "浦和",
    "V-Varen Nagasaki": "長崎",
    "Vanraure Hachinohe": "八戸",
    "Vegalta Sendai": "仙台",
    "Ventforet Kofu": "甲府",
    "Vissel Kobe": "神戸",
    "Yokohama F. Marinos": "横浜FM",
    "Yokohama FC": "横浜FC",
    "Cerezo Osaka": "C大阪",
    "Gamba Osaka": "G大阪",
    "FC Machida Zelvia": "町田",
    "FC Osaka": "FC大阪",
    "FC Ryūkyū": "琉球",
    "Avispa Fukuoka": "福岡",
}

def main():
    print("=== 改良型マッピング開始 ===")
    
    # 既存のマッピングを読み込み
    mapping_df = pd.read_csv('cf_name_mapping.csv')
    print(f"現在のマッピング数: {len(mapping_df)}")
    print(f"既にマッチ済み: {mapping_df['FB_Name'].notna().sum()}")
    print(f"未マッチ: {mapping_df['FB_Name'].isna().sum()}")
    
    # FB側の選手全て をひらがなに変換
    print("\n=== FB側の選手名をひらがなに変換中... ===")
    fb_df = pd.read_csv('fb_unique_players.csv')
    kakasi = pykakasi.kakasi()
    fb_names_hiragana = {}
    
    for idx, fb_name in enumerate(fb_df['FB_Name']):
        if pd.notna(fb_name):
            result = kakasi.convert(str(fb_name))
            hiragana = ''.join([r['hira'] for r in result])
            fb_names_hiragana[str(fb_name)] = normalize_text(hiragana)
        
        if (idx + 1) % 100 == 0:
            print(f"  処理済み: {idx+1}/{len(fb_df)}")
    
    print(f"ひらがな変換完了: {len(fb_names_hiragana)}")
    
    # チーム情報を追加
    print("\n=== SC側にチーム情報を追加中... ===")
    sc_dir = Path('生データ/skill corner')
    sc_team_map = {}
    
    for csv_file in sc_dir.rglob('*.csv'):
        try:
            df_temp = pd.read_csv(csv_file, usecols=['Player', 'Team'])
            for _, row in df_temp.iterrows():
                player = str(row['Player']).strip() if pd.notna(row['Player']) else ""
                team = str(row['Team']).strip() if pd.notna(row['Team']) else ""
                if player and player not in sc_team_map:
                    sc_team_map[player] = team
        except:
            pass
    
    mapping_df['SC_Team'] = mapping_df['SC_Name'].map(sc_team_map)
    
    print(f"チーム情報付与: {mapping_df['SC_Team'].notna().sum()}/{len(mapping_df)}")
    
    # FB側にチーム情報を追加
    print("=== FB側にチーム情報を追加中... ===")
    fb_dir = Path('生データ/football box')
    fb_team_map = {}
    
    for excel_file in fb_dir.rglob('*.xlsx'):
        try:
            df_temp = pd.read_excel(excel_file, sheet_name=0, usecols=['選手名', 'チーム名'])
            for _, row in df_temp.iterrows():
                player = str(row['選手名']).strip() if pd.notna(row['選手名']) else ""
                team = str(row['チーム名']).strip() if pd.notna(row['チーム名']) else ""
                if player and player not in fb_team_map:
                    fb_team_map[player] = team
        except:
            pass
    
    fb_df['チーム名'] = fb_df['FB_Name'].map(fb_team_map)
    
    print(f"チーム情報付与: {fb_df['チーム名'].notna().sum()}/{len(fb_df)}")
    
    # マッチング改善
    print("\n=== マッピング改善中（チーム重視）... ===")
    improved_count = 0
    
    for idx, row in mapping_df.iterrows():
        if pd.notna(row['FB_Name']):
            # 既にマッチング済み
            continue
        
        sc_name = row['SC_Name']
        sc_team = row['SC_Team']
        
        if pd.isna(sc_team):
            # チーム情報がない場合はスキップ
            continue
        
        sc_team_jp = TEAM_MAPPING.get(str(sc_team).strip())
        if not sc_team_jp:
            continue
        
        # SC側の名前をひらがなに変換
        sc_hiragana = romaji_to_hiragana(str(sc_name))
        
        # 同じチームのFB側選手を検索
        candidates = fb_df[(fb_df['チーム名'] == sc_team_jp) & (fb_df['FB_Name'].notna())]
        
        best_match = None
        best_ratio = 0
        threshold = 0.80  # 80%以上の類似度で確定
        
        for fb_idx, fb_row in candidates.iterrows():
            fb_name = fb_row['FB_Name']
            fb_hiragana = fb_names_hiragana.get(str(fb_name), "")
            
            similarity = SequenceMatcher(None, sc_hiragana, fb_hiragana).ratio()
            
            if similarity > threshold and similarity > best_ratio:
                best_ratio = similarity
                best_match = str(fb_name)
        
        if best_match:
            mapping_df.at[idx, 'FB_Name'] = best_match
            improved_count += 1
            
            if improved_count <= 10:
                print(f"  ✓ {sc_name:20} ({sc_team_jp:6}) → {best_match:20} ({best_ratio:.0%})")
        
        if (idx + 1) % 100 == 0:
            print(f"  処理済み: {idx+1}/{len(mapping_df)} (改善数: {improved_count})")
    
    # 結果を保存
    print(f"\n=== 結果を保存中... ===")
    mapping_df[['SC_Name', 'FB_Name']].to_csv('cf_name_mapping.csv', index=False, encoding='utf-8-sig')
    
    total_matched = mapping_df['FB_Name'].notna().sum()
    print(f"\n✅ マッピング完了！")
    print(f"総数: {len(mapping_df)}")
    print(f"マッチ数: {total_matched}")
    print(f"マッチ率: {total_matched/len(mapping_df)*100:.1f}%")
    print(f"この実行での改善数: {improved_count}")

if __name__ == '__main__':
    main()
