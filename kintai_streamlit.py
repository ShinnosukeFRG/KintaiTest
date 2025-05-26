import streamlit as st
import datetime
import requests
import pytz

# Notion API 情報
NOTION_API_KEY = "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"
DATABASE_ID = "1ffe3c1a837a8116935efa71d54c36da"
headers = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

# 日本時間の現在日時
jst = pytz.timezone('Asia/Tokyo')
today = datetime.datetime.now(jst).date()
now_time = datetime.datetime.now(jst).time().strftime("%H:%M")

st.title("勤怠打刻ページ")

# 入力欄
name = st.text_input("名前を入力してください")
selected_date = st.date_input("打刻日", value=today)
day_of_week = selected_date.strftime('%a')
begin_time = st.time_input("始業時刻", value=datetime.time(9, 0))
end_time = st.time_input("終業時刻", value=datetime.time(18, 0))
break_time = st.number_input("休憩時間（時間）", min_value=0.0, step=0.25)
company_time = st.number_input("自社勤務時間（時間）", min_value=0.0, step=0.25)
transport_fee = st.number_input("交通費（円）", min_value=0)
special_note = st.selectbox("特記事項", ["なし", "有給", "特別休暇", "遅刻", "早退"])

# 稼働時間自動計算
start_dt = datetime.datetime.combine(selected_date, begin_time)
end_dt = datetime.datetime.combine(selected_date, end_time)
worked_hours = max((end_dt - start_dt).total_seconds() / 3600 - break_time, 0)

if st.button("打刻を送信"):
    if not name:
        st.warning("名前を入力してください。")
    else:
        payload = {
            "parent": {"database_id": DATABASE_ID},
            "properties": {
                "打刻者": {"title": [{"text": {"content": name}}]},
                "日付": {"date": {"start": str(selected_date)}},
                "曜日": {"select": {"name": day_of_week}},
                "始業時刻": {"rich_text": [{"text": {"content": begin_time.strftime('%H:%M')}}]},
                "終業時刻": {"rich_text": [{"text": {"content": end_time.strftime('%H:%M')}}]},
                "休憩時間": {"number": break_time},
                "自社勤務時間": {"number": company_time},
                "交通費": {"number": transport_fee},
                "特記事項": {"select": {"name": special_note}},
                "稼働時間": {"rich_text": [{"text": {"content": f"{worked_hours:.2f}"}}]}
            }
        }

        response = requests.post(
            "https://api.notion.com/v1/pages",
            headers=headers,
            json=payload
        )

        if response.status_code == 200:
            st.success("打刻が保存されました！")
        else:
            st.error(f"エラーが発生しました: {response.text}")
