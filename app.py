import datetime

import streamlit as st
from httpx import Client
from loguru import logger
from streamlit_cookies_controller import CookieController

from model import Message
from settings import Settings

settings = Settings()
cookies = CookieController()


def get_messages(channel, start_date, end_date, limit):
    client = Client(timeout=60 * 4)
    response = client.get(
        "http://localhost:8000/messages",
        params={
            "channel": channel,
            "start_date": start_date,
            "end_date": end_date,
            "limit": limit,
        },
    )
    return [Message(**i) for i in response.json()]


def make_feed(messages):

    client = Client(timeout=60 * 4)
    response = client.post(
        "http://localhost:8000/make_feed", json={"messages": messages}
    )
    return response.text


st.title("News Feed")

channels = st.multiselect(
    "Select channel", settings.channels_supported, settings.top_supported_channels
)
cookies.set("channels_selected", channels)

col1, col2 = st.columns(2)

with col1:
    # 0:00:00 today
    start_date = st.date_input(
        "Start date",
        value=datetime.datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0
        ),
    )

with col2:
    end_date = st.date_input(
        "End date",
        value=(datetime.datetime.now() + datetime.timedelta(days=1)).replace(
            hour=0, minute=0, second=0, microsecond=0
        ),
    )

st.write(" ".join([f"[{channel}](https://t.me/{channel})" for channel in channels]))


def get_feed(start_date, end_date, channels):
    messages = []

    for channel in channels:
        try:
            messages_ = get_messages(channel, start_date, end_date, 10)
            for message in messages_:

                messages.append(
                    {
                        "message": message.message,
                        "date": str(message.date),
                        "link": f"https://t.me/{channel}/{message.id}",
                        "source": channel,
                    }
                )
        except:
            logger.exception(f"Failed to get messages from channel {channel}")

    messages = sorted(messages, key=lambda x: x["date"])

    feed = make_feed(messages).replace("\\n", "\n")
    feed = feed.strip('"')
    feed = feed.strip()

    feed = feed.replace("# ", "# 🌟 ")
    feed = feed.replace("- ", "- 📰 ")

    with open("feed.md", "w") as f:
        f.write(feed)
    st.session_state["feed"] = feed


st.button(
    "Get feed",
    on_click=get_feed,
    kwargs={"start_date": start_date, "end_date": end_date, "channels": channels},
)


st.markdown(st.session_state.get("feed", ""))
