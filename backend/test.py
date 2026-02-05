import asyncio

from openai import AsyncOpenAI


async def list_models() -> None:
    client = AsyncOpenAI()

    async for model in client.models.list():
        print(f"ID={model.id} owned={model.owned_by}")


asyncio.run(list_models())
