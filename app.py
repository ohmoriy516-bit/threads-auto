import streamlit as st
import requests
from google import genai
import time
from PIL import Image
import io
from datetime import datetime, timedelta
import gspread
from google.oauth2.service_account import Credentials
import json
import pandas as pd
import concurrent.futures
import re
import urllib.parse
from streamlit_local_storage import LocalStorage

# ==========================================
# 🎨 ページ設定
# ==========================================
st.set_page_config(page_title="Threads Marketing Pro", layout="wide", initial_sidebar_state="collapsed")

if "current_page" not in st.session_state:
    st.session_state["current_page"] = "1. ダッシュボード"

page = st.session_state["current_page"]

# ==========================================
# 🎨 デザイン刷新（ダーク×ネオングリーン）
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');

    /* ベース */
    html, body, .stApp {
        background-color: #0e0e12 !important;
        color: #e8e8f0 !important;
        font-family: 'Inter', 'Hiragino Sans', 'Noto Sans JP', sans-serif !important;
    }

    /* メインコンテナ */
    .main .block-container {
        padding-top: 72px !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        max-width: 1280px !important;
        margin: 0 auto !important;
    }

    /* ナビバー */
    .nav-wrapper {
        position: fixed;
        top: 0; left: 0; right: 0;
        z-index: 99999;
        background: rgba(14, 14, 18, 0.92);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border-bottom: 1px solid rgba(0, 255, 136, 0.15);
        padding: 0 24px;
        display: flex;
        align-items: center;
        height: 56px;
        gap: 4px;
    }

    /* ナビボタン共通 */
    div[data-testid="stHorizontalBlock"] > div > div > div > button {
        background: transparent !important;
        color: #888 !important;
        border: none !important;
        border-bottom: 2px solid transparent !important;
        border-radius: 0 !important;
        font-size: 12px !important;
        font-weight: 600 !important;
        letter-spacing: 0.03em !important;
        padding: 8px 10px !important;
        width: 100% !important;
        box-shadow: none !important;
        transition: all 0.18s ease !important;
        white-space: nowrap !important;
    }
    div[data-testid="stHorizontalBlock"] > div > div > div > button:hover {
        color: #00ff88 !important;
        border-bottom-color: #00ff88 !important;
        background: rgba(0, 255, 136, 0.05) !important;
    }

    /* ヘッダーなど非表示 */
    .stAppDeployButton,
    [data-testid="stHeaderActionElements"],
    [data-testid="stViewerBadge"],
    [data-testid="stDecoration"],
    [data-testid="stToolbar"],
    [data-testid="stToolbarActions"],
    [data-testid="stSidebarCollapsedControl"],
    [data-testid="collapsedControl"],
    [data-testid="stSidebar"],
    a[href*="github.com"],
    .stActionButton,
    #MainMenu, header, footer {
        display: none !important;
        visibility: hidden !important;
        width: 0 !important; height: 0 !important;
        overflow: hidden !important;
    }

    /* カード */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background: #16161e !important;
        border: 1px solid rgba(255,255,255,0.07) !important;
        border-radius: 12px !important;
        padding: 20px !important;
        margin-bottom: 12px !important;
        box-shadow: 0 4px 24px rgba(0,0,0,0.3) !important;
        transition: border-color 0.2s !important;
    }
    [data-testid="stVerticalBlockBorderWrapper"]:hover {
        border-color: rgba(0, 255, 136, 0.2) !important;
    }

    /* タイトル */
    h1 { color: #ffffff !important; font-weight: 800 !important; font-size: 1.8rem !important; letter-spacing: -0.02em !important; }
    h2, h3 { color: #d0d0e0 !important; font-weight: 700 !important; }

    /* メトリクス */
    [data-testid="stMetricValue"] {
        font-size: 2.2rem !important;
        font-weight: 800 !important;
        color: #00ff88 !important;
        font-family: 'Inter', monospace !important;
    }
    [data-testid="stMetricLabel"] { color: #888 !important; font-size: 0.75rem !important; letter-spacing: 0.06em !important; text-transform: uppercase !important; }
    [data-testid="stMetricDelta"] { color: #00cc6a !important; }

    /* ボタン */
    .stButton > button {
        background: linear-gradient(135deg, #00ff88 0%, #00cc6a 100%) !important;
        color: #0e0e12 !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        font-size: 13px !important;
        padding: 10px 20px !important;
        letter-spacing: 0.02em !important;
        box-shadow: 0 4px 16px rgba(0, 255, 136, 0.25) !important;
        transition: all 0.18s ease !important;
    }
    .stButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 24px rgba(0, 255, 136, 0.4) !important;
        background: linear-gradient(135deg, #33ff99 0%, #00dd77 100%) !important;
    }

    /* インプット */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div,
    .stMultiSelect > div > div {
        background: #1a1a24 !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        color: #e8e8f0 !important;
        border-radius: 8px !important;
        font-size: 13px !important;
    }
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: rgba(0, 255, 136, 0.5) !important;
        box-shadow: 0 0 0 3px rgba(0, 255, 136, 0.08) !important;
    }
    .stTextInput label, .stTextArea label, .stSelectbox label,
    .stMultiSelect label, .stSlider label, .stRadio label,
    .stCheckbox label, .stFileUploader label {
        color: #aaa !important;
        font-size: 12px !important;
        font-weight: 600 !important;
        letter-spacing: 0.05em !important;
        text-transform: uppercase !important;
    }

    /* タブ */
    .stTabs [data-baseweb="tab-list"] {
        background: transparent !important;
        border-bottom: 1px solid rgba(255,255,255,0.08) !important;
        gap: 0 !important;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        color: #666 !important;
        font-weight: 600 !important;
        font-size: 13px !important;
        border-bottom: 2px solid transparent !important;
        padding: 10px 20px !important;
    }
    .stTabs [aria-selected="true"] {
        color: #00ff88 !important;
        border-bottom-color: #00ff88 !important;
        background: transparent !important;
    }

    /* エクスパンダー */
    .streamlit-expanderHeader {
        background: #1a1a24 !important;
        color: #e8e8f0 !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 13px !important;
    }
    .streamlit-expanderContent {
        background: #16161e !important;
        border: 1px solid rgba(255,255,255,0.06) !important;
        border-radius: 0 0 8px 8px !important;
    }

    /* データフレーム */
    .stDataFrame { border-radius: 10px !important; overflow: hidden !important; }
    .stDataFrame thead th { background: #1a1a24 !important; color: #00ff88 !important; font-size: 12px !important; letter-spacing: 0.05em !important; }
    .stDataFrame tbody td { background: #12121a !important; color: #d0d0e0 !important; font-size: 12px !important; }
    .stDataFrame tbody tr:hover td { background: #1a1a2e !important; }

    /* ディバイダー */
    hr { border-color: rgba(255,255,255,0.07) !important; margin: 20px 0 !important; }

    /* サクセス・ウォーニング */
    .stSuccess { background: rgba(0, 255, 136, 0.08) !important; border: 1px solid rgba(0, 255, 136, 0.25) !important; color: #00ff88 !important; border-radius: 8px !important; }
    .stWarning { background: rgba(255, 180, 0, 0.08) !important; border: 1px solid rgba(255, 180, 0, 0.25) !important; border-radius: 8px !important; }
    .stError { background: rgba(255, 80, 80, 0.08) !important; border: 1px solid rgba(255, 80, 80, 0.25) !important; border-radius: 8px !important; }

    /* チェックボックス・ラジオ */
    .stCheckbox > label > div, .stRadio > div > label > div {
        background: transparent !important;
        border-color: rgba(0, 255, 136, 0.4) !important;
    }

    /* スライダー */
    .stSlider [data-baseweb="slider"] [data-testid="stThumbValue"] { color: #00ff88 !important; }
    .stSlider .st-bo { background: #00ff88 !important; }

    /* スピナー */
    .stSpinner > div { border-top-color: #00ff88 !important; }

    /* チャート背景 */
    .stVegaLiteChart, .stPlotlyChart { background: transparent !important; }

    /* スクロールバー */
    ::-webkit-scrollbar { width: 4px; height: 4px; }
    ::-webkit-scrollbar-track { background: #0e0e12; }
    ::-webkit-scrollbar-thumb { background: #333; border-radius: 2px; }
    ::-webkit-scrollbar-thumb:hover { background: #00ff88; }
</style>
""", unsafe_allow_html=True)

# ナビボタン
nav_pages = [
    ("📊 ダッシュボード", "1. ダッシュボード"),
    ("🛍 商品作成", "2. 商品作成＆予約"),
    ("📈 分析", "3. エンゲージメント分析"),
    ("⚙️ API設定", "4. API設定"),
    ("📝 テンプレート", "5. テンプレート管理"),
]

cols = st.columns(len(nav_pages))
for col, (label, page_name) in zip(cols, nav_pages):
    btn_label = f"**{label}**" if page == page_name else label
    if col.button(btn_label, key=f"nav_{page_name}", use_container_width=True):
        st.session_state["current_page"] = page_name
        st.rerun()

st.divider()

# ==========================================
# ⚙️ 関数群
# ==========================================
local_storage = LocalStorage()

def convert_drive_link(url):
    if not url or "drive.google.com" not in url: return url
    try:
        if "file/d/" in url: file_id = url.split("file/d/")[1].split("/")[0]
        elif "id=" in url: file_id = url.split("id=")[1].split("&")[0]
        else: return url
        return f"https://drive.google.com/uc?export=view&id={file_id}"
    except: return url

def download_image(url):
    """【修正1】高画質URLを優先して取得"""
    if not url: return None
    try:
        # 楽天の小サイズ画像URLを高画質に差し替え
        hq_url = url
        if "thumbnail.image.rakuten.co.jp" in url:
            hq_url = re.sub(r'_ex=\d+x\d+', '_ex=600x600', url)
            if '_ex=' not in url:
                hq_url = url.rstrip('/') + '?_ex=600x600'
        
        res = requests.get(convert_drive_link(hq_url), timeout=10)
        img = Image.open(io.BytesIO(res.content))
        
        # 低解像度なら元URLも試みる
        if img.size[0] < 200 and hq_url != url:
            res2 = requests.get(convert_drive_link(url), timeout=10)
            img2 = Image.open(io.BytesIO(res2.content))
            if img2.size[0] > img.size[0]:
                return img2
        return img
    except: return None

def get_best_image_url(item):
    """【修正1】楽天商品の最高画質URLを返す"""
    # largeImageUrls > mediumImageUrls の順で取得
    large_urls = item.get("largeImageUrls", [])
    medium_urls = item.get("mediumImageUrls", [])
    
    if large_urls and isinstance(large_urls[0], dict):
        url = large_urls[0].get("imageUrl", "")
    elif medium_urls and isinstance(medium_urls[0], dict):
        url = medium_urls[0].get("imageUrl", "")
    else:
        url = ""
    
    # 解像度パラメータを強制的に大きくする
    if url:
        url = re.sub(r'_ex=\d+x\d+', '_ex=600x600', url)
    return url

def shorten_url(url):
    if not url or "http" not in url: return url
    try:
        safe_url = urllib.parse.quote(url)
        res = requests.get(f"http://tinyurl.com/api-create?url={safe_url}", timeout=10)
        if res.status_code == 200 and "tinyurl.com" in res.text:
            return res.text.strip()
    except: pass
    return url

def create_affiliate_link(url, aff_id):
    if not url: return "【URL未設定】"
    if not aff_id: return url
    if "hb.afl.rakuten.co.jp" not in url:
        encoded_url = urllib.parse.quote(url, safe='')
        long_aff_url = f"https://hb.afl.rakuten.co.jp/hgc/{aff_id}/?pc={encoded_url}"
    else:
        long_aff_url = url
    return shorten_url(long_aff_url)

def save_to_sheets(sheet_id, g_json, row_data):
    if not sheet_id or not g_json: return False
    try:
        creds = Credentials.from_service_account_info(json.loads(g_json, strict=False), scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"])
        client = gspread.authorize(creds)
        sheet = client.open_by_key(sheet_id).worksheet("sheet")
        all_values = sheet.get_all_values()
        next_row = 1
        for i, row in enumerate(all_values):
            if any(str(val).strip() for val in row):
                next_row = i + 2
        if next_row > sheet.row_count:
            sheet.add_rows(next_row - sheet.row_count)
        cells = sheet.range(f"A{next_row}:J{next_row}")
        for i, val in enumerate(row_data):
            cells[i].value = str(val) if val is not None else ""
        sheet.update_cells(cells)
        return True
    except Exception as e:
        st.error(f"スプレッドシート保存エラー: {e}")
        return False

def get_sheet_data(sheet_id, g_json):
    try:
        creds = Credentials.from_service_account_info(json.loads(g_json, strict=False), scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"])
        data = gspread.authorize(creds).open_by_key(sheet_id).worksheet("sheet").get_all_values()
        if len(data) < 2: return []
        return [dict(zip(data[0], row)) for row in data[1:] if any(row)]
    except: return []

def get_templates(sheet_id, g_json):
    try:
        creds = Credentials.from_service_account_info(json.loads(g_json, strict=False), scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"])
        data = gspread.authorize(creds).open_by_key(sheet_id).worksheet("テンプレート").get_all_values()
        return [{"title": row[0], "content": row[1]} for row in data[1:] if len(row) >= 2 and row[0]]
    except: return []

def save_template(sheet_id, g_json, title, content):
    try:
        creds = Credentials.from_service_account_info(json.loads(g_json, strict=False), scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"])
        ss = gspread.authorize(creds).open_by_key(sheet_id)
        try: ws = ss.worksheet("テンプレート")
        except: ws = ss.add_worksheet(title="テンプレート", rows=100, cols=2); ws.append_row(["タイトル", "本文"])
        all_values = ws.get_all_values()
        next_row = 1
        for i, row in enumerate(all_values):
            if any(str(val).strip() for val in row):
                next_row = i + 2
        if next_row > ws.row_count:
            ws.add_rows(next_row - ws.row_count)
        cells = ws.range(f"A{next_row}:B{next_row}")
        cells[0].value = str(title)
        cells[1].value = str(content)
        ws.update_cells(cells)
        return True
    except: return False

def get_threads_user_name(token):
    try: return requests.get(f"https://graph.threads.net/v1.0/me?fields=username&access_token={token}").json().get("username")
    except: return None

def get_threads_engagement(token):
    try:
        threads = requests.get(f"https://graph.threads.net/v1.0/me/threads?fields=id,text,timestamp,is_reply&limit=100&access_token={token}").json().get("data", [])
        def fetch_insights(th):
            try:
                m = {d['name']: d['values'][0]['value'] for d in requests.get(f"https://graph.threads.net/v1.0/{th['id']}/insights?metric=views,likes,replies&access_token={token}").json().get("data", [])}
                th.update({'views': m.get('views',0), 'like_count': m.get('likes',0), 'reply_count': m.get('replies',0)})
            except: th.update({'views':0,'like_count':0,'reply_count':0})
            return th
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor: return list(executor.map(fetch_insights, threads))
    except: return []

def get_rakuten_ranking(app_id, access_key, affiliate_id, genre_id):
    """【修正1】largeImageUrlsも取得するように変更"""
    try:
        res = requests.get(
            "https://openapi.rakuten.co.jp/ichibaranking/api/IchibaItem/Ranking/20220601",
            params={
                "applicationId": app_id,
                "accessKey": access_key,
                "genreId": genre_id,
                "affiliateId": affiliate_id,
                "imageFlag": 1,  # 画像URL取得フラグ
            }
        )
        return [item["Item"] for item in res.json().get("Items", [])[:10]]
    except: return []

def generate_post_text(item_name, price, target_str, tone, length, custom_prompt, reference_post, api_key, image=None):
    """【修正2】AI感を消すプロンプトに刷新"""
    if not api_key: return "❌ APIキー未設定"

    # トーン別の書き方ガイド
    tone_guides = {
        "エモい":     "感情的な気づき・体験談ベース。「気づいたら手放せなくなってた」「なんか泣けてくる」みたいな感覚的な言葉。",
        "役立つ":     "具体的な数字・比較・before/after。読んで即使える情報。「実際に3週間使ったら〇〇だった」",
        "元気":       "テンポ良く短文連打。勢いで読ませる。「マジで最高。以上。」くらいの温度感。",
        "親近感":     "友達に話しかける口語体。「これさ、正直最初は半信半疑だったんだけど」",
        "本音レビュー": "良い点だけでなく惜しい点も正直に。「欠点も言うと〇〇なんだけど、それでも買ってよかった理由が…」",
        "あざと可愛い": "自分の話から始めて引き込む。「最近ずっとこれのことしか考えてない（笑）」",
        "高級感":     "短く・静かに・余白を感じる文体。形容詞を絞る。説明しすぎない。",
        "ズボラ命":   "面倒くさがりの本音。「正直めんどくさい自分でも続いてるのが不思議で」",
    }

    tone_guide = tone_guides.get(tone, "自然な口語体。")

    # 【核心】AI感を消すための具体的な禁止事項
    prompt = f"""
あなたはThreadsで3万フォロワーを持つ一般人インフルエンサーです。
PR感・広告感・AI感を徹底的に排除した投稿文を書いてください。

【商品】{item_name}
【価格】{price}円
【ターゲット読者】{target_str}
【文体トーン】{tone}：{tone_guide}
【文字数】{length}文字前後（厳守）

【絶対禁止ルール】
- 箇条書き（・や●や①②③）は使わない
- 「〜な方におすすめ」「〜なあなたへ」は使わない
- 「購入はこちら」「詳細は」「リンクから」は使わない
- 「〜してみました」「〜してみては」は使わない
- 商品名を冒頭に持ってこない
- ハッシュタグを入れない（別で追加する）
- 絵文字を3個以上使わない
- 「〜ですよね」「〜ですよね？」は1回まで
- 体言止めを多用しない
- 「コスパ最強」「神アイテム」などのありきたりな表現禁止

【バズる投稿の法則】
- 冒頭1行目で「え、なんで？」と思わせる
- 自分の体験・感情・失敗談から入る
- 結論を最後まで引き延ばす
- 「読んでる人も同じ経験あるかも」と思わせる
- 最後の一文に余韻を残す

{f'【参考投稿スタイル】{reference_post}' if reference_post else ''}
{f'【追加指示】{custom_prompt}' if custom_prompt else ''}

投稿文のみ出力（説明・前置き不要）：
"""

    client = genai.Client(api_key=api_key)
    last_error = ""

    for model_name in ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro']:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=[image, prompt] if image else prompt
            )
            return response.text.strip()
        except Exception as e:
            last_error = str(e)
            time.sleep(2)
            continue

    return f"❌ エラー詳細: {last_error}"

def post_to_threads(access_token, text, reply_to_id=None, image_url=None):
    try:
        res = requests.post("https://graph.threads.net/v1.0/me/threads", params={"access_token":access_token,"text":text,"media_type":"IMAGE" if image_url else "TEXT","image_url":image_url if image_url else "","reply_to_id":reply_to_id if reply_to_id else ""})
        if res.status_code == 200:
            cid = res.json().get("id"); time.sleep(5)
            requests.post("https://graph.threads.net/v1.0/me/threads_publish", params={"access_token":access_token,"creation_id":cid})
            return cid
    except: pass
    return None

# ==========================================
# 🖥️ 初期化 ＆ データ同期
# ==========================================
if "api_keys" not in st.session_state:
    st.session_state["api_keys"] = {"rakuten_id":"", "rakuten_key":"", "rakuten_aff_id":"", "gemini":"", "threads":"", "sheet_id":"", "g_json":""}

if not st.session_state["api_keys"]["rakuten_id"]:
    stored = local_storage.getItem("threads_marketing_keys")
    if stored: st.session_state["api_keys"].update(stored)

if "gen_count" not in st.session_state: st.session_state["gen_count"] = 0

api = st.session_state["api_keys"]

# --- 1. ダッシュボード ---
if page == "1. ダッシュボード":
    u_name = get_threads_user_name(api["threads"])
    st.title(f"📊 {u_name if u_name else 'あなた'} のダッシュボード")
    if not api["rakuten_id"] or not api["threads"]: st.warning("⚠️ API設定を行ってください。")
    else:
        sheet_data = get_sheet_data(api["sheet_id"], api["g_json"])
        today = datetime.now().strftime('%Y/%m/%d')
        today_pending = [r for r in sheet_data if r.get("投稿チェック", "") in ["pending", "予約中", ""] and r.get("投稿日", "") == today]
        if today_pending: st.dataframe([{"時間": f"{p.get('時','')}:{p.get('分','')}", "本文": p.get('本文', '')[:40]} for p in today_pending], use_container_width=True, hide_index=True)
        else: st.success("本日の予定はありません。")
        st.divider()
        threads_data = get_threads_engagement(api["threads"])
        if threads_data:
            df = pd.DataFrame(threads_data); df['date'] = pd.to_datetime(df['timestamp']).dt.strftime('%m/%d'); df_m = df[df['is_reply'] != True]
            c1, c2, c3 = st.columns(3)
            with c1: st.metric("📝 投稿数", len(df_m)); st.bar_chart(df_m.groupby('date').size())
            with c2: st.metric("❤️ いいね合計", df_m['like_count'].sum()); st.bar_chart(df_m.groupby('date')['like_count'].sum(), color="#00ff88")
            with c3: st.metric("💬 返信合計", df_m['reply_count'].sum()); st.bar_chart(df_m.groupby('date')['reply_count'].sum(), color="#00cc6a")

# --- 2. 商品作成＆予約 ---
elif page == "2. 商品作成＆予約":
    st.title("🛒 商品作成 ＆ 予約")
    if not api["rakuten_id"] or not api["gemini"]: st.warning("⚠️ API設定を行ってください。")
    else:
        templates = get_templates(api["sheet_id"], api["g_json"])
        tab1, tab2, tab3 = st.tabs(["🏆 ランキング", "🔗 URL", "📸 画像"])

        def show_final_ui(key, def_txt, def_url, def_img):
            uid = f"{key}_{st.session_state['gen_count']}"
            with st.expander(f"✨ 投稿確認 & 送信", expanded=True):
                ui = st.checkbox("🖼️ 画像あり", value=True, key=f"ui_{uid}")
                dr = st.text_input("🔗 Googleドライブの画像URLを入力", value=def_img if def_img else "", key=f"dr_{uid}")
                m_txt = st.text_area("本文", value=def_txt, height=150, key=f"mt_{uid}")
                r_txt = st.text_area("リプライ", value=f"▼ 詳細はこちら\n{def_url}", height=80, key=f"rt_{uid}")
                f_img = convert_drive_link(dr) if ui and dr else (def_img if ui else None)

                c1, c2 = st.columns(2)
                if c1.button("🚀 今すぐ投稿", key=f"now_{uid}"):
                    with st.spinner("投稿中..."):
                        mid = post_to_threads(api["threads"], m_txt, image_url=f_img)
                        if mid:
                            time.sleep(2); post_to_threads(api["threads"], r_txt, reply_to_id=mid)
                            st.success("🎉 投稿完了しました！"); st.balloons()
                with c2:
                    dv = st.date_input("予約日", key=f"dv_{uid}"); tv = st.time_input("時間", key=f"tv_{uid}")
                    if st.button("🗓️ 予約に追加", key=f"res_{uid}"):
                        with st.spinner("保存中..."):
                            row = [
                                "", m_txt, dv.strftime('%Y/%m/%d'), str(tv.hour), str(tv.minute),
                                "", "", dr, r_txt, f_img if f_img else ""
                            ]
                            if save_to_sheets(api["sheet_id"], api["g_json"], row):
                                st.success("✅ 予約保存完了！")

        with tab1:
            genres = {"🏆 総合": "0", "👗 レディース": "100371", "👔 メンズ": "551177", "👠 靴": "558885", "👜 バッグ": "216129", "⌚ 腕時計": "558929", "💄 美容": "100939", "💊 健康": "100143", "🏥 介護": "551169", "🍎 食品": "100227", "🍪 スイーツ": "551167", "🍹 飲料": "100316", "🍺 洋酒": "510915", "🍶 日本酒": "510901", "🛋 インテリア": "100804", "🍳 キッチン": "558944", "🚿 日用品": "215783", "🔌 家電": "562631", "📸 カメラ": "211742", "💻 パソコン": "100026", "📱 スマホ": "562637", "⚽ スポーツ": "101070", "⛳ ゴルフ": "101077", "🚗 車": "503190", "🧸 おもちゃ": "101164", "🎨 ホビー": "101165", "🎮 ゲーム": "101205", "🎸 楽器": "112493", "📚 本": "200376", "📀 CD・DVD": "101240", "🍼 ベビー": "100533", "🐱 ペット": "101213"}
            sel_g = st.selectbox("ジャンルを選択", list(genres.keys()), key="sg_t1")
            if st.button("ランキング取得", key="br_t1"):
                if "res1" in st.session_state: del st.session_state["res1"]
                st.session_state["it1"] = get_rakuten_ranking(api["rakuten_id"], api["rakuten_key"], api["rakuten_aff_id"], genres[sel_g])
            if "it1" in st.session_state:
                sel = []
                for i, item in enumerate(st.session_state["it1"]):
                    with st.container(border=True):
                        c1, c2 = st.columns([1, 4])
                        # 【修正1】高画質URLで表示
                        best_url = get_best_image_url(item)
                        if best_url:
                            c1.image(best_url, use_container_width=True)
                        if c2.checkbox(f"選ぶ: {item['itemName'][:50]}", key=f"ch1_{i}"):
                            uf = c2.file_uploader("📸 解析用画像（オプション）", type=["jpg","png"], key=f"uf1_{i}")
                            item["u_img_file"] = uf
                            item["_best_url"] = best_url
                            sel.append(item)
                if sel:
                    st.divider()
                    c1, c2, c3 = st.columns(3)
                    with c1: gen = st.radio("性別", ["女性", "男性", "指定なし"], key="gen_t1")
                    with c2: age = st.multiselect("年代", ["10代", "20代", "30代", "40代", "50代〜"], default=["20代", "30代"], key="age_t1")
                    with c3: kids = st.radio("子供", ["なし", "乳児", "幼児", "小学生"], key="kids_t1")
                    c4, c5 = st.columns(2)
                    with c4: tone = st.selectbox("トーン", ["エモい", "役立つ", "元気", "親近感", "本音レビュー", "あざと可愛い", "高級感", "ズボラ命"], key="tone_t1")
                    with c5: length = st.slider("文字数", 10, 500, 80, step=10, key="len_t1")
                    sel_tmp = st.selectbox("🧠 テンプレート適用", ["手動入力"] + [t["title"] for t in templates], key="tmp_t1")
                    ref = next((t["content"] for t in templates if t["title"] == sel_tmp), "") if sel_tmp != "手動入力" else ""
                    cp = st.text_area("✍️ 特別指示（例：「最近疲れてる人向け」「秋っぽく」）", key="cp_t1")
                    if st.button(f"✨ {len(sel)}件を一括生成", key="gen_btn_t1"):
                        with st.spinner("AI文章作成中..."):
                            st.session_state["gen_count"] += 1
                            results = []
                            for s in sel:
                                # アップロード画像 > 楽天高画質画像の順で使用
                                if s.get("u_img_file"):
                                    img = Image.open(s["u_img_file"])
                                else:
                                    img = download_image(s.get("_best_url", ""))
                                results.append({
                                    "item": s,
                                    "text": generate_post_text(
                                        s["itemName"], s["itemPrice"],
                                        f"{gen}, {','.join(age)}, 子供:{kids}",
                                        tone, length, cp, ref, api["gemini"], img
                                    )
                                })
                            st.session_state["res1"] = results
                            st.rerun()
            if "res1" in st.session_state:
                for p in st.session_state["res1"]:
                    best_url = p["item"].get("_best_url") or get_best_image_url(p["item"])
                    show_final_ui(f"r1_{p['item']['itemCode']}", p["text"], create_affiliate_link(p["item"]["itemUrl"], api["rakuten_aff_id"]), best_url)

        with tab2:
            url_in = st.text_input("楽天商品URL", key="u_t2")
            if st.button("情報取得", key="br_t2"):
                if "res2" in st.session_state: del st.session_state["res2"]
                res = requests.get(url_in, headers={'User-Agent': 'Mozilla/5.0'}).text
                t_m = re.search(r'<title>(.*?)</title>', res, re.DOTALL); i_m = re.search(r'<meta\s+property="og:image"\s+content="(.*?)"', res)
                img_url = i_m.group(1) if i_m else ""
                # OGP画像を高画質化
                if img_url:
                    img_url = re.sub(r'_ex=\d+x\d+', '_ex=600x600', img_url)
                st.session_state["it2"] = {"name": t_m.group(1)[:50] if t_m else "商品", "img": img_url, "url": url_in}
            if "it2" in st.session_state:
                it = st.session_state["it2"]
                if it["img"]: st.image(it["img"], width=200)
                c1, c2, c3 = st.columns(3)
                with c1: gen_t2 = st.radio("性別", ["女性", "男性", "指定なし"], key="gen_t2")
                with c2: age_t2 = st.multiselect("年代", ["10代", "20代", "30代", "40代", "50代〜"], default=["20代", "30代"], key="age_t2")
                with c3: kids_t2 = st.radio("子供", ["なし", "乳児", "幼児", "小学生"], key="kids_t2")
                tone_t2 = st.selectbox("トーン", ["エモい", "役立つ", "元気", "親近感", "本音レビュー", "あざと可愛い", "高級感", "ズボラ命"], key="tone_t2")
                len_t2 = st.slider("文字数", 10, 500, 80, step=10, key="len_t2")
                cp_t2 = st.text_area("✍️ 特別指示", key="cp_t2")
                if st.button("✨ 本文作成", key="gen_btn_t2"):
                    with st.spinner("作成中..."):
                        st.session_state["gen_count"] += 1
                        st.session_state["res2"] = {"text": generate_post_text(it["name"], "", f"{gen_t2}, {','.join(age_t2)}, 子供:{kids_t2}", tone_t2, len_t2, cp_t2, "", api["gemini"], download_image(it["img"]))}
                        st.rerun()
            if "res2" in st.session_state:
                show_final_ui("r2", st.session_state["res2"]["text"], create_affiliate_link(st.session_state["it2"]["url"], api["rakuten_aff_id"]), st.session_state["it2"]["img"])

        with tab3:
            img_url_t3 = st.text_input("🔗 画像URL", key="u_t3")
            hint_t3 = st.text_input("商品名ヒント", key="h_t3")
            tone_t3 = st.selectbox("トーン", ["エモい", "役立つ", "元気", "親近感", "本音レビュー", "あざと可愛い", "高級感", "ズボラ命"], key="tone_t3")
            len_t3 = st.slider("文字数", 10, 500, 80, step=10, key="len_t3")
            cp_t3 = st.text_area("✍️ 特別指示", key="cp_t3")
            if st.button("✨ 本文を作成", key="gen_btn_t3"):
                if "res3" in st.session_state: del st.session_state["res3"]
                if img_url_t3:
                    with st.spinner("解析中..."):
                        st.session_state["gen_count"] += 1
                        st.session_state["res3"] = {"text": generate_post_text(hint_t3, "", "指定なし", tone_t3, len_t3, cp_t3, "", api["gemini"], download_image(img_url_t3)), "url": img_url_t3}
                        st.rerun()
                else: st.error("画像URLを入力してください。")
            if "res3" in st.session_state:
                aff_t3 = st.text_input("🔗 アフィ商品URL", key="aff_t3")
                show_final_ui("r3", st.session_state["res3"]["text"], create_affiliate_link(aff_t3, api["rakuten_aff_id"]), st.session_state["res3"]["url"])

# --- 3. 分析 ---
elif page == "3. エンゲージメント分析":
    st.title("🔍 エンゲージメント分析")
    if not api["threads"]: st.warning("API設定を行ってください。")
    else:
        threads_data = get_threads_engagement(api["threads"])
        if threads_data:
            df = pd.DataFrame(threads_data); df['timestamp'] = pd.to_datetime(df['timestamp']).dt.date; df = df[df['is_reply'] != True]
            c1, c2, c3 = st.columns(3)
            with c1: st.metric("👀 総閲覧数", f"{df['views'].sum():,}")
            with c2: st.metric("❤️ 総いいね数", f"{df['like_count'].sum():,}")
            with c3: st.metric("💬 総返信数", f"{df['reply_count'].sum():,}")
            st.dataframe(df[['timestamp', 'text', 'views', 'like_count', 'reply_count']].sort_values(by='views', ascending=False), use_container_width=True, hide_index=True)

# --- 4. API設定 ---
elif page == "4. API設定":
    st.title("⚙️ API設定")
    with st.expander("👤 管理者モード (Secretsロード)", expanded=True):
        pw = st.text_input("合言葉", type="password", key="m_pw")
        if st.button("一括ロード", key="b_load"):
            if pw == st.secrets.get("master_password"):
                st.session_state["api_keys"].update({"rakuten_id":st.secrets.get("rakuten_id",""),"rakuten_key":st.secrets.get("rakuten_key",""),"rakuten_aff_id":st.secrets.get("rakuten_aff_id",""),"gemini":st.secrets.get("gemini_key",""),"threads":st.secrets.get("threads_token",""),"sheet_id":st.secrets.get("sheet_id",""),"g_json":st.secrets.get("g_json","")})
                st.success("✅ ロードしました！"); st.rerun()
    with st.container(border=True):
        c1, c2 = st.columns(2)
        r_id = c1.text_input("楽天 App ID", value=api["rakuten_id"], type="password", key="ri")
        r_key = c1.text_input("楽天 Access Key", value=api["rakuten_key"], type="password", key="rk")
        r_aff = c1.text_input("楽天 Aff ID", value=api["rakuten_aff_id"], type="password", key="ra")
        g_key = c2.text_input("Gemini API", value=api["gemini"], type="password", key="gk")
        t_tok = c2.text_input("Threads Token", value=api["threads"], type="password", key="tt")
        s_id = c2.text_input("Sheet ID", value=api["sheet_id"], key="si")
        g_js = st.text_area("GCloud JSON", value=api["g_json"], height=100, key="gj")
        if st.button("✅ 設定を保存", key="b_save"):
            d = {"rakuten_id":r_id,"rakuten_key":r_key,"rakuten_aff_id":r_aff,"gemini":g_key,"threads":t_tok,"sheet_id":s_id,"g_json":g_js}
            st.session_state["api_keys"].update(d); local_storage.setItem("threads_marketing_keys", d); st.success("🎉 保存完了！"); st.rerun()

# --- 5. テンプレート管理 ---
elif page == "5. テンプレート管理":
    st.title("📝 テンプレート管理")
    if not api["sheet_id"]: st.warning("API設定を行ってください。")
    else:
        with st.form("tf"):
            t_ti = st.text_input("テンプレート名"); t_co = st.text_area("本文", height=150)
            if st.form_submit_button("保存"):
                if save_template(api["sheet_id"], api["g_json"], t_ti, t_co): st.success("保存完了！"); time.sleep(1); st.rerun()
        st.divider(); templates = get_templates(api["sheet_id"], api["g_json"])
        for t in templates:
            with st.expander(t["title"]): st.write(t["content"])
