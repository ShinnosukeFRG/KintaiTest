import streamlit as st
import requests
import datetime

# 🔒 個別設定（APIキーやDBページIDを入れてください）
NOTION_API_KEY = "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"
DATABASE_ID = "1ffe3c1a837a81dab7c2f2f0ee932fc5"

# Notion API共通設定
headers = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

# 日付フォーマット
today = datetime.date.today().isoformat()

# タイトル表示
st.title("🕒 勤怠打刻アプリ")
st.subheader(f"日付：{today}")

# --- ユーザー入力 ---
start_time = st.time_input("始業時刻（例：09:00）", value=datetime.time(9, 0))
end_time = st.time_input("終業時刻（例：18:00）", value=datetime.time(18, 0))
break_time = st.number_input("休憩時間（分）", min_value=0, max_value=240, value=60, step=5)
internal_hours =st.number_input("⏱ 自社勤務時間（時間）", min_value=0.0, max_value=24.0, value=0.0, step=0.5)
transport = st.number_input("交通費（円）", min_value=0, step=100)
note = st.selectbox("特記事項", ["なし", "有給", "特別休暇", "遅刻", "早退"])

# 🔘 ボタンで打刻
if st.button("✅ 打刻する"):
    # NotionのDBへPOST/UPDATE
    def search_page_for_today():
        url = f"https://api.notion.com/v1/databases/%7BDATABASE_ID%7D/query"
        payload = {
        "filter": {
            "property": "日付",
            "title": {
                "equals": today
            }
        }
    }
        res = requests.post(url, headers=headers, json=payload)
        data = res.json()
        if "results" in data and len(data["results"]) > 0:
            return data["results"][0]["id"]
        else:
            return None


    def create_or_update_record(page_id=None):
        data = {
    "日付": {
        "title": [
            {
                "text": {
                    "content": today  # タイトルとして日付文字列を送信
                }
            }
        ]
    },
    "始業時刻": {"rich_text": [{"type": "text", "text": {"content": start_time.strftime("%H:%M")}}]},
    "終業時刻": {"rich_text": [{"type": "text", "text": {"content": end_time.strftime("%H:%M")}}]},
    "休憩時間": {"number": break_time},
    "自社勤務": {"number": internal_hours},
    "交通費": {"number": transport},
    "特記事項": {"select": {"name": note}}
}

        if page_id:
            url = f"https://api.notion.com/v1/pages/{page_id}"
            res = requests.patch(url, headers=headers, json={"properties": data})
        else:
            url = "https://api.notion.com/v1/pages"
            res = requests.post(url, headers=headers, json={
                "parent": {"database_id": DATABASE_ID},
                "properties": data
            })

        if res.status_code in [200, 201]:
            st.success("✅ 打刻が完了しました！")
        else:
            st.error(f"❌ エラー発生: {res.text}")

    page_id = search_page_for_today()
    create_or_update_record()
    