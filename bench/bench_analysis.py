import asyncio
import time
import httpx
import os

API_URL = os.getenv("BENCH_API", "http://localhost:8000")

SYMBOL = "AAPL"
PEERS = "MSFT,GOOGL,AMZN,TSLA,NVDA"

async def run_once(client: httpx.AsyncClient):
    await client.get(f"{API_URL}/api/v1/analysis/{SYMBOL}", params={"peers": PEERS, "analysis_type": "quick"})

async def bench(concurrency: int = 50, requests: int = 200):
    client = httpx.AsyncClient(timeout=30)
    tasks = []
    t0 = time.perf_counter()
    for _ in range(requests):
        tasks.append(run_once(client))
        if len(tasks) == concurrency:
            await asyncio.gather(*tasks)
            tasks.clear()
    if tasks:
        await asyncio.gather(*tasks)
    dt = time.perf_counter() - t0
    await client.aclose()
    print(f"{requests} requests in {dt:.2f}s → {requests/dt:.1f} req/s")

if __name__ == "__main__":
    asyncio.run(bench())