import asyncio
import json

from openai import AsyncOpenAI

from settings import OpenaiSettings

openai_settings = OpenaiSettings()

client = AsyncOpenAI(api_key=openai_settings.api_key)


async def make_feed(messages, model=openai_settings.model, limit=256):

    messages = [{**i, "message": i["message"][:limit]} for i in messages]

    sources = set([i["source"] for i in messages])
    with open("news.json", "w") as f:
        json.dump(messages, f, indent=4, ensure_ascii=False)

    system_messages = (
        "You are a journalist and your task to make daily review of the news.\n"
        "You have to write a short summary and different opinions on the news for the last 24 hours.\n"
        "Group the news by topic from different sources and add links to the sources.\n"
        "Sort the news by importance. Most important news should be at the top.\n"
        "Link shoud be named as the source field in json. Do not hallucinate.\n"
        "Use all the sources you have not one.\n"
        "Be pluralistic.\n"
        "You have to write at least 5 news.\n"
        "Render as a markdown.\n"
        "Use only the information from the news.\n"
        "News given as list of json objects.\n"
        "Use english language.\n"
        "Example of proper topics: War in Ukraine, Covid-19, War in Israel, etc.\n"
        "Do not use genral topics like 'World news', 'Politics', 'International Relations', 'Domestic Incidents', Natural Disasters'.\n"
        "Topics should be coincise and describe events.\n"
        "Format:\n"
        "# News Topic 1\n"
        "- News 1 and summary. [SourceName1](link1), [SourceName2](link2)\n"
        "- News 2 and summary. [SourceName5](link5), [SourceName2](link2)\n"
        "# News Topic 2\n"
        "- News 1 and summary. [SourceName1](link1), [SourceName3](link3)\n"
        "- News 2 and summary. [SourceName5](link5)"
    )

    messages = [
        {"role": "system", "content": system_messages},
        {
            "role": "user",
            "content": f"Sources: {', '.join(sources)}\n News: {json.dumps(messages, indent=4, ensure_ascii=False)}",
        },
    ]

    response = await client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0,
    )
    response = response.choices[0].message.content
    response = response.replace("`", "")
    response = response.replace("markdown", "")
    return response


if __name__ == "__main__":
    with open("news.json", "r") as f:
        messages = json.load(f)

    feed = asyncio.run(make_feed(messages))

    with open("feed.md", "w") as f:
        f.write(feed)
