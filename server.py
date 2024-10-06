from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, Request

from client import TelegramClient, TelegramSettings, fetch_messages
from gpt import make_feed as make_feed_gpt
from model import Message

telegram_settings = TelegramSettings()

api_id = telegram_settings.api_id
api_hash = telegram_settings.api_hash
session_name = telegram_settings.session_name

telegram_client = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global telegram_client
    telegram_client = TelegramClient(session_name, api_id, api_hash)
    yield
    await telegram_client.disconnect()


app = FastAPI(lifespan=lifespan)


@app.get("/messages")
async def get_messages(
    channel: str,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    limit: int | None = 10,
) -> list[Message]:
    if limit > 1000:
        raise ValueError(
            "Limit should be less than 1000, currently it is set to {limit}"
        )

    async with telegram_client:
        messages = await fetch_messages(
            telegram_client, channel, start_date, end_date, limit
        )

    return messages


@app.post("/make_feed")
async def make_feed(
    request: Request,
) -> str:
    r = await request.json()
    r = r["messages"]
    feed = await make_feed_gpt(r)
    return feed
