import asyncio
import datetime

from telethon import TelegramClient, functions

from model import Channel, Message
from settings import TelegramSettings

telegram_settings = TelegramSettings()

api_id = telegram_settings.api_id
api_hash = telegram_settings.api_hash
session_name = telegram_settings.session_name


async def channels(client: str | int, channel_url) -> list[Channel]:
    entity = await client.get_entity(channel_url)
    result = await client(
        functions.channels.GetChannelRecommendationsRequest(channel=entity)
    )
    channels = [Channel(**i.to_dict()) for i in result.chats]
    return channels


def get_channel_info(client: TelegramClient, channel_id):
    channel = client.get_entity(channel_id)
    return channel


async def fetch_messages(
    client: TelegramClient,
    channel_url: str,
    start_date: datetime.datetime,
    end_date: datetime.datetime,
    limit=None,
) -> list[Message]:

    channel = await client.get_entity(channel_url)

    messages = []
    async for message in client.iter_messages(
        channel,
        offset_date=start_date,
        reverse=True,
        limit=limit,
    ):
        msg_dict = Message(**message.to_dict())

        if msg_dict.date.replace(tzinfo=None) > end_date:
            break
        if msg_dict.message != "":
            messages.append(msg_dict)
    return messages


def sync_fetch_and_save_messages(
    client,
    channel_url: str,
    start_date: datetime.datetime,
    end_date: datetime.datetime,
    limit: int,
) -> list[Message]:
    messages = asyncio.run(
        fetch_messages(client, channel_url, start_date, end_date, limit)
    )
    return messages


async def test():
    async with TelegramClient(session_name, api_id, api_hash) as client:
        print(
            await fetch_messages(
                client, "telegram", datetime.datetime.now(), datetime.datetime.now(), 10
            )
        )


if __name__ == "__main__":
    asyncio.run(test())
