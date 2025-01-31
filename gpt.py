import asyncio
import json

from openai import AsyncOpenAI
from pydantic import BaseModel

from settings import OpenaiSettings

openai_settings = OpenaiSettings()

client = AsyncOpenAI(api_key=openai_settings.api_key)


class News(BaseModel):
    telegram_urls: list[str]
    summary: str


class Topic(BaseModel):
    topic: str
    news: list[News]


class Feed(BaseModel):
    topics: list[Topic]


async def make_feed(messages, model=openai_settings.model, limit=256) -> Feed:

    messages = [{**i, "message": i["message"][:limit]} for i in messages]

    sources = set([i["source"] for i in messages])
    with open("news.json", "w") as f:
        json.dump(messages, f, indent=4, ensure_ascii=False)

    system_messages = (
        "You are a journalist and your task to make daily review of the news.\n"
        "You have to write a short summary and different opinions on the news for the last 24 hours.\n"
        "Group the news by topic from different sources and add links to the sources.\n"
        "Group sources. Do not repeat the same info in topics. Just add link to list.\n"
        "Sort the news by importance. Most important news should be at the top.\n"
        "Link shoud be named as the source field in json. Do not hallucinate.\n"
        "Use all the sources you have not one.\n"
        "Be pluralistic.\n"
        "You have to write at least 5 news.\n"
        "Use only the information from the news.\n"
        "News given as list of json objects.\n"
        "Use english language.\n"
        "Example of proper topics: War in Ukraine, Covid-19, War in Israel, etc.\n"
        "Do not use genral topics like 'World news', 'Politics', 'International Relations', 'Domestic Incidents', Natural Disasters'.\n"
        "Topics should be coincise and describe events.\n"
        "Topics consist of news, every news have multiple sources as a rule. News has coincise summary"
    )

    messages = [
        {"role": "system", "content": system_messages},
        {
            "role": "user",
            "content": f"Sources: {', '.join(sources)}\n News: {json.dumps(messages, indent=4, ensure_ascii=False)}",
        },
    ]

    response = await client.beta.chat.completions.parse(
        model=model, messages=messages, temperature=0, response_format=Feed
    )
    parsed = response.choices[0].message.parsed

    return parsed


if __name__ == "__main__":
    with open("news_3.json", "r") as f:
        messages = json.load(f)

    # for i in range(1_000_000):
    #     import time
    #     time.sleep(10)
    feed = asyncio.run(make_feed(messages))

    with open("feed.json", "w") as f:
        f.write(feed.model_dump_json(indent=4))
