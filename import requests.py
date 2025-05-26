import requests

# セキュリティのためここにだけAPIキーを貼ってください（共有しないよう注意）
NOTION_API_KEY = "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"
PARENT_PAGE_ID = "1ffe3c1a837a80828718ddfc1c5bb248"

headers = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

payload = {
    "parent": { "type": "page_id", "page_id": PARENT_PAGE_ID},
    "title": [
        {
            "type": "text",
            "text": {
                "content": "勤怠管理_2024年10月"
            }
        }
    ],
    "properties": {
        # ✅ 「日付」をタイトルプロパティに変更
        "日付": { "title": {} },
        
        "曜日": {
            "type": "select",
            "select": {
                "options": [{"name": d} for d in ["月", "火", "水", "木", "金", "土", "日"]]
            }
        },
        "始業時刻": { "type": "rich_text", "rich_text": {} },
        "終業時刻": { "type": "rich_text", "rich_text": {} },
        "休憩時間": { "type": "number", "number": { "format": "number" } },
        "自社勤務": { "type": "checkbox", "checkbox": {} },
        "交通費": { "type": "number", "number": { "format": "yen" } },
        "特記事項": {
            "type": "select",
            "select": {
                "options": [{"name": t} for t in ["有給", "特別休暇", "遅刻", "早退", "なし"]]
            }
        },
        # 計算式プロパティはNotion UIから設定
        "稼働時間": { "type": "rich_text", "rich_text": {} },
        "残業時間": { "type": "rich_text", "rich_text": {} }
    }
}

response = requests.post(
    "https://api.notion.com/v1/databases",
    headers=headers,
    json=payload
)

print("ステータスコード:", response.status_code)
print("レスポンス:", response.text)