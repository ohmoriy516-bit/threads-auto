import gspread
from google.oauth2.service_account import Credentials
import json
import requests
import time
from datetime import datetime
import os

THREADS_TOKEN = os.environ.get("THREADS_TOKEN")
SHEET_ID = os.environ.get("SHEET_ID")
G_JSON = os.environ.get("G_JSON")

def post_to_threads(access_token, text, reply_to_id=None, image_url=None):
    params = {"access_token": access_token, "text": text}
    if image_url and image_url.startswith("http"):
        params["media_type"] = "IMAGE"
        params["image_url"] = image_url
    else:
        params["media_type"] = "TEXT"
    if reply_to_id:
        params["reply_to_id"] = reply_to_id

    try:
        res = requests.post("https://graph.threads.net/v1.0/me/threads", params=params)
        if res.status_code == 200:
            creation_id = res.json().get("id")
            if params["media_type"] == "IMAGE":
                time.sleep(10)
            pub_res = requests.post(
                "https://graph.threads.net/v1.0/me/threads_publish",
                params={"access_token": access_token, "creation_id": creation_id}
            )
            return pub_res.json().get("id")
    except Exception as e:
        print(f"APIエラー: {e}")
    return None

def main():
    if not all([THREADS_TOKEN, SHEET_ID, G_JSON]):
        print("設定(Secrets)が不足しています。")
        return

    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(json.loads(G_JSON), scopes=scopes)
    sheet = gspread.authorize(creds).open_by_key(SHEET_ID).sheet1

    all_values = sheet.get_all_values()
    if not all_values:
        return

    headers = all_values[0]
    rows = all_values[1:]
    now = datetime.now()

    for i, row_values in enumerate(rows):
        row = dict(zip(headers, row_values))
        status = row.get('投稿チェック', '')

        if status in ['', 'pending', '予約中']:
            try:
                date_str = f"{row['投稿日']} {row['時']}:{row['分']}:00"
                scheduled_time = datetime.strptime(date_str, '%Y/%m/%d %H:%M:%S')

                if scheduled_time <= now:
                    print(f"実行中: {row.get('本文', '')[:20]}...")

                    # メイン投稿
                    main_id = post_to_threads(
                        THREADS_TOKEN,
                        row.get('本文', ''),
                        image_url=row.get('画像URL', '')
                    )

                    if main_id:
                        time.sleep(5)
                        # 返信：reply_to_id を渡してリプライとして投稿（修正点）
                        reply_text = row.get('返信コメント内容', '')
                        if reply_text:
                            post_to_threads(
                                THREADS_TOKEN,
                                reply_text,
                                reply_to_id=main_id  # ← ここが修正箇所
                            )

                        sheet.update_cell(i + 2, 6, "完了")
                        print("✅ 投稿成功！")
                    else:
                        print("❌ 投稿失敗")

            except Exception as e:
                print(f"行 {i+2} の処理でエラー: {e}")

if __name__ == "__main__":
    main()
