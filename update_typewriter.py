from notion_client import Client
from dotenv import load_dotenv
import os
from datetime import datetime
import re
from zoneinfo import ZoneInfo

today = datetime.now(ZoneInfo("Asia/Jakarta")).strftime("%A")

def format_time(time_str):
    if not time_str:
        return ""

    # Ubah : menjadi .
    time_str = time_str.replace(":", ".")

    # Tambahkan nol di depan jika perlu
    time_str = re.sub(r"\b(\d)\.", r"0\1.", time_str)

    return time_str

load_dotenv()

TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("DATABASE_ID")

if TOKEN is None or DATABASE_ID is None:
    raise ValueError("Environment variables belum diatur.")

notion = Client(auth=TOKEN)

today = datetime.now(ZoneInfo("Asia/Jakarta")).strftime("%A")

TYPE_MAP = {
    "Activity": ("work", "event-work", "todo-work"),
    "Event": ("work", "event-work", "todo-work"),
    "Workout": ("personal", "event-personal", "todo-personal"),
    "Mood": ("personal", "event-personal", "todo-personal"),
}

print("=" * 40)
print("Hari ini :", today)
print("=" * 40)

response = notion.databases.query(
    database_id=DATABASE_ID
)

print("Jumlah data:", len(response["results"]))

events = []
todos = []

for page in response["results"]:

    props = page["properties"]

    try:
        days = [item["name"] for item in props["Day"]["multi_select"]]
    except:
        continue

    if today not in days:
        continue

    try:
        name = props["Name"]["title"][0]["plain_text"]
    except:
        name = ""

    try:
        category = props["Category"]["select"]["name"]
    except:
        category = ""

    try:
        activity = props["Type"]["select"]["name"]
    except:
        activity = ""

    try:
        time = "".join(
            t["plain_text"]
            for t in props["Time"]["rich_text"]
        )
    except:
        time = ""

    try:
        note = "".join(
            t["plain_text"]
            for t in props["Keterangan"]["rich_text"]
        )
    except:
        note = ""
    if category == "":
        continue

    label, event_class, todo_class = TYPE_MAP.get(
        activity,
        ("personal", "event-personal", "todo-personal")
    )

    item = {
        "name": name,
        "time": time,
        "label": label,
        "event_class": event_class,
        "todo_class": todo_class
    }

    if category == "Event":
        events.append(item)

    elif category == "Todo":
        todos.append(item)

print(events)
print(todos)

from bs4 import BeautifulSoup

with open("index.html", "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f, "lxml")

events_ul = soup.find("ul", class_="events")

events_ul.clear()

if len(events) == 0:

    li = soup.new_tag("li")

    icon = soup.new_tag("span")
    icon["class"] = "event-icon event-personal"
    icon.string = "personal"

    label = soup.new_tag("span")
    label["class"] = "label"
    label.string = "No event YAYY"

    waktu = soup.new_tag("span")
    waktu["class"] = "time"

    li.append(icon)
    li.append(label)
    li.append(waktu)

    events_ul.append(li)

else:

    for event in events:

        li = soup.new_tag("li")

        icon = soup.new_tag("span")
        icon["class"] = f"event-icon {event['event_class']}"
        icon.string = event["label"]

        label = soup.new_tag("span")
        label["class"] = "label"
        label.string = event["name"]

        waktu = soup.new_tag("span")
        waktu["class"] = "time"
        waktu.string = event["time"]

        li.append(icon)
        li.append(label)
        li.append(waktu)

        events_ul.append(li)

todos_ul = soup.find("ul", class_="todos")
todos_ul.clear()

if len(todos) == 0:

    li = soup.new_tag("li")
    li["class"] = "todo"

    icon = soup.new_tag("span")
    icon["class"] = "todo-icon todo-personal"
    icon.string = "personal"

    label = soup.new_tag("span")
    label["class"] = "label"
    label.string = "Nothing to do YAYYY"

    li.append(icon)
    li.append(label)

    todos_ul.append(li)

else:

    for todo in todos:

        li = soup.new_tag("li")
        li["class"] = "todo"

        icon = soup.new_tag("span")
        icon["class"] = f"todo-icon {todo['todo_class']}"
        icon.string = todo["label"]

        label = soup.new_tag("span")
        label["class"] = "label"
        label.string = todo["name"]

        time = soup.new_tag("span")
        time["class"] = "time"
        time.string = todo["time"]

        li.append(icon)
        li.append(label)
        li.append(time)


        todos_ul.append(li)

# BARU DISIMPAN
with open("index.html", "w", encoding="utf-8") as f:
    f.write(str(soup))

print("Berhasil!")
