import streamlit as st
import datetime
import requests
import pytz
import pandas as pd
import calendar

# Notion API 情報
NOTION_API_KEY = "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"
DATABASE_ID = "1ffe3c1a837a8116935efa71d54c36da"
headers = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

# 日本時間取得
jst = pytz.timezone('Asia/Tokyo')
today = datetime.datetime.now(jst).date()
now_time = datetime.datetime.now(jst).time().strftime("%H:%M")

# --- 打刻ページ ---
st.title("勤怠打刻ページ")

name = st.text_input("名前を入力してください")
selected_date = st.date_input("打刻日", value=today)
day_of_week = selected_date.strftime('%a')
begin_time = st.time_input("始業時刻", value=datetime.time(9, 0))
end_time = st.time_input("終業時刻", value=datetime.time(18, 0))
break_time = st.number_input("休憩時間（時間）", min_value=0.0, step=0.25)
company_time = st.number_input("自社勤務時間（時間）", min_value=0.0, step=0.25)
transport_fee = st.number_input("交通費（円）", min_value=0)
special_note = st.selectbox("特記事項", ["なし", "有給", "特別休暇", "遅刻", "早退"])

# 稼働・残業時間計算
start_dt = datetime.datetime.combine(selected_date, begin_time)
end_dt = datetime.datetime.combine(selected_date, end_time)
worked_hours = max((end_dt - start_dt).total_seconds() / 3600 - break_time, 0)
overtime_hours = max(worked_hours - 8, 0)

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
                "稼働時間": {"rich_text": [{"text": {"content": f"{worked_hours:.2f}"}}]},
                "残業時間": {"rich_text": [{"text": {"content": f"{overtime_hours:.2f}"}}]}
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


# --- 月次集計ページ ---
st.header("📊 月次集計")

query_name = st.text_input("集計対象の名前を入力")
query_month = st.text_input("集計対象の月 (例: 2025-05)")

if st.button("月次を集計する") and query_name and query_month:
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    start_date = f"{query_month}-01"
    end_date = f"{query_month}-32"

    query_payload = {
        "filter": {
            "and": [
                {"property": "打刻者", "title": {"equals": query_name}},
                {"property": "日付", "date": {"on_or_after": start_date}},
                {"property": "日付", "date": {"before": end_date}},
            ]
        }
    }

    response = requests.post(url, headers=headers, json=query_payload)

    if response.status_code == 200:
        results = response.json().get("results", [])
        total_work = 0
        total_company = 0
        total_paid = 0
        total_special = 0
        workdays = 0

        for res in results:
            props = res["properties"]
            try:
                work_hours = float(props["稼働時間"]["rich_text"][0]["text"]["content"])
            except:
                work_hours = 0
            try:
                company_hours = float(props["自社勤務時間"]["number"])
            except:
                company_hours = 0

            note = props["特記事項"]["select"]["name"]
            date_str = props["日付"]["date"]["start"]
            day = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()

            total_work += work_hours
            total_company += company_hours
            if note == "有給":
                total_paid += 1
            elif note == "特別休暇":
                total_special += 1
            if note == "なし":
                workdays += 1

        total_genba = total_work - total_company

        # 祝日考慮（簡略対応：5月のみ）
        year, month = map(int, query_month.split("-"))
        holidays_may = [datetime.date(year, month, d) for d in [3, 4, 5]]
        first_day = datetime.date(year, month, 1)
        last_day = datetime.date(year, month, calendar.monthrange(year, month)[1])
        date_range = pd.date_range(start=first_day, end=last_day)
        standard_workdays = sum(1 for date in date_range if date.weekday() < 5 and date.date() not in holidays_may)

        st.subheader(f"{query_name} さんの {query_month} 月次集計結果")
        st.markdown(f"""
        - 🕒 総稼働時間: `{total_work:.2f} 時間`
        - 🏢 自社勤務時間: `{total_company:.2f} 時間`
        - 🏭 現場稼働時間: `{total_genba:.2f} 時間`
        - 🛌 有給取得日数: `{total_paid} 日`
        - 🎌 特別休暇日数: `{total_special} 日`
        - 📅 標準出勤日数: `{standard_workdays} 日`
        - ✅ 実際の出勤日数: `{workdays} 日`
        """)
    else:
        st.error(f"集計に失敗しました: {response.text}")
