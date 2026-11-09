import asyncio
import os
import time

import httpx
import numpy as np
from dotenv import load_dotenv


async def petition(client: httpx.AsyncClient, url: str, request: dict, token):
    begin = time.perf_counter()
    try:
        response = await client.post(url=url, json=request, headers=token)
        response.raise_for_status()
        return time.perf_counter() - begin
    except httpx.HTTPError as e:
        print(f"Error found: {e}")
        return None


async def calculate_p50_p95(n_requests: int):
    url = "/predict"
    predict = {"station": 2, "hour": 5, "day_of_week": 6}
    load_dotenv()
    key = os.getenv("API_TOKEN", "")
    headers = {"Token": key}
    times = []

    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        for _ in range(n_requests):
            events = await petition(client, url, predict, headers)
            times.append(events)

    aux = [t for t in times if t is not None]
    validtime = np.array(aux) * 1000
    print(f"P50: {np.percentile(validtime, 50)} ms")
    print(f"P95: {np.percentile(validtime, 95)} ms")
    nones = [t for t in times if t is None]
    print(f"Failures: {len(nones)}")


asyncio.run(calculate_p50_p95(200))
