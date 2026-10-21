import asyncio
import json

import httpx


async def main():
    async with httpx.AsyncClient(timeout=90) as client:
        for path in ("/health", "/matches"):
            response = await client.get("http://127.0.0.1:8000" + path)
            response.raise_for_status()
            data = response.json()
            print(path, json.dumps(data[:6] if isinstance(data, list) else data))


asyncio.run(main())
