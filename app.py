import datetime
import hashlib
import shelve

import streamlit as st
from httpx import Client
from loguru import logger
from streamlit_cookies_controller import CookieController

from gpt import Feed
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


def make_feed(messages) -> Feed:

    client = Client(timeout=60 * 4)
    response = client.post(
        "http://localhost:8000/make_feed", json={"messages": messages}
    )
    return Feed(**response.json())


st.title("News Feed")

user = cookies.get("CF_Authorization")
if user is None:
    user = cookies.get("_streamlit_xsrf")
user_hash = hashlib.sha256(user.encode()).hexdigest()


with shelve.open("data/storage") as db:
    if user_hash in db:
        channels_saved = db[user_hash]
    else:
        channels_saved = settings.top_supported_channels


channels = st.multiselect("Select channel", settings.channels_supported, channels_saved)

with shelve.open("data/storage") as db:
    db[user_hash] = channels

col1, col2 = st.columns(2)

with col1:
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
            messages_ = get_messages(
                channel, start_date, end_date, settings.number_of_messages_per_channel
            )
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

    feed = make_feed(messages)

    feed_md = ""

    for topic in feed.topics:
        topic_name = topic.topic
        feed_md += f"### 🌟{topic_name}\n"
        for news in topic.news:
            feed_md += f"- 📰 {news.summary}"
            for idx, link in enumerate(news.telegram_urls):
                channel_ = link.split("/")[-2]
                feed_md += f" [{channel_}]({link}),"
            feed_md = feed_md[:-1]
            feed_md += "\n"

    with open("feed.md", "w") as f:
        f.write(feed_md)
    st.session_state["feed"] = feed_md


st.button(
    "Get feed",
    on_click=get_feed,
    kwargs={"start_date": start_date, "end_date": end_date, "channels": channels},
)


st.markdown(st.session_state.get("feed", ""))
