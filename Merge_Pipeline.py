import pandas as pd

def merge_soccer_data(fb_filepath, sc_filepath, name_mapping, match_date_filter=None):
    """
    Football BoxとSkill Cornerのデータを統合する前処理パイプライン
    
    Parameters:
        fb_filepath (str): Football BoxのExcelファイル(.xlsx)またはCSVのパス
        sc_filepath (str): Skill CornerのCSVファイルのパス
        name_mapping (dict): {'英語名': '日本語名'} の変換マスタ
        match_date_filter (str, optional): 特定の試合日('YYYY-MM-DD')で絞り込む場合
    
    Returns:
        pd.DataFrame: 結合・前処理済みのデータフレーム
    """
    
    # 1. データの読み込み
    print(f"Loading data...\n FB: {fb_filepath}\n SC: {sc_filepath}")
    # 今回はテスト用にCSV化されたExcelデータを想定
    try:
        df_fb = pd.read_csv(fb_filepath, encoding='utf-8')
    except UnicodeDecodeError:
        df_fb = pd.read_csv(fb_filepath, encoding='shift_jis')
        
    df_sc = pd.read_csv(sc_filepath)

    # 2. 試合日のフォーマット統一 (20260207 -> 2026-02-07)
    df_fb['試合日'] = pd.to_datetime(df_fb['試合日'].astype(str), format='%Y%m%d').dt.strftime('%Y-%m-%d')
    
    # フィルタリング指定があれば実行
    if match_date_filter:
        df_fb = df_fb[df_fb['試合日'] == match_date_filter]
        df_sc = df_sc[df_sc['Date'] == match_date_filter]

    # 3. MVP対応: CF（ストライカー）の抽出
    # ※SC側のPositionが'Center Forward'のものに絞る
    df_sc_cf = df_sc[df_sc['Position'] == 'Center Forward'].copy()

    # 4. 選手名の言語統一（マッピング）
    df_sc_cf['Player_JA'] = df_sc_cf['Player'].map(name_mapping)

    # 5. データの結合 (Inner Merge)
    df_merged = pd.merge(
        df_fb,
        df_sc_cf,
        left_on=['試合日', '選手名'],
        right_on=['Date', 'Player_JA'],
        how='inner'
    )
    
    return df_merged

# ==========================================
# 実行テスト用ブロック (ここから下はSkill化する際に消すか別ファイルに分ける)
# ==========================================
if __name__ == "__main__":
    # 手元のファイルパス（ご自身の環境に合わせて微調整してください）
    TEST_FB_FILE = '選手データ_エリア進入プレー_試合別.xlsx - sheet1.csv'
    TEST_SC_FILE = '2026-02-07_-_Giravanz_Kitakyushu_v_Gainare_Tottori_physical_data.csv'
    
    # 2/7 北九州vs鳥取のCF名寄せ辞書
    test_mapping = {
        'Naoto Miki': '三木　直土',
        'Hideatsu Ozawa': '小澤　秀充',
        'Ryo Nagai': '永井　龍',
        'Seung-Jin Koh': '高　昇辰'
    }

    # 関数の実行
    result_df = merge_soccer_data(TEST_FB_FILE, TEST_SC_FILE, test_mapping, match_date_filter='2026-02-07')

    # 結果の確認
    print("\n=== Merge Successful! ===")
    cols_to_check = ['試合日', 'チーム名', 'Player_JA', 'PA進入', 'Sprint Count TIP']
    print(result_df[cols_to_check])