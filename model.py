import datetime

from pydantic import BaseModel, RootModel


class Channel(BaseModel):
    id: int
    title: str
    date: datetime.datetime
    participants_count: int | None = None
    username: str | None = None


class ChannelList(RootModel):
    root: list[Channel]


class Peer(BaseModel):
    channel_id: int | None = None
    user_id: int | None = None


class Message(BaseModel):
    id: int
    date: datetime.datetime
    message: str | None = None
    views: int | None = None
    forwards: int | None = None
    from_id: int | None = None
    post: bool | None = None
    peer_id: Peer | None = None


class MessageList(RootModel):
    root: list[Message]
