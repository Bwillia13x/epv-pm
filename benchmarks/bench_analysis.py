#!/usr/bin/env python3
"""Simple async benchmark for /api/v1/analysis

Usage::

    python benchmarks/bench_analysis.py --url http://localhost:8000 \
        --requests 50 --concurrency 10

The script sends *requests* POST calls to
{url}/api/v1/analysis/AAPL with 5 peer symbols and prints latency
statistics (mean, median, p95, p99) as CSV to stdout so CI can parse.
"""
from __future__ import annotations

import argparse
import asyncio
import statistics
import sys
import time
from typing import List

import httpx  # type: ignore

PEERS: List[str] = ["MSFT", "GOOGL", "AMZN", "META", "TSLA"]


async def _single_request(client: httpx.AsyncClient, url: str) -> float:
    """Send one POST request, return elapsed seconds."""
    payload = {
        "symbol": "AAPL",
        "years": 5,
        "peers": PEERS,
        "analysis_type": "quick",
    }
    start = time.perf_counter()
    resp = await client.post(url, json=payload, timeout=60.0)
    resp.raise_for_status()
    return time.perf_counter() - start


async def run_benchmark(base_url: str, total: int, concurrency: int) -> List[float]:
    """Run *total* requests with *concurrency* level and collect latencies."""

    endpoint = f"{base_url.rstrip('/')}/api/v1/analysis/AAPL"
    latencies: List[float] = []
    sem = asyncio.Semaphore(concurrency)

    async with httpx.AsyncClient(http2=True) as client:
        async def worker() -> None:
            nonlocal latencies
            async with sem:
                lat = await _single_request(client, endpoint)
                latencies.append(lat)

        await asyncio.gather(*[worker() for _ in range(total)])

    return latencies


def print_stats(samples: List[float]) -> None:
    if not samples:
        print("no-samples")
        return
    mean = statistics.mean(samples)
    p50 = statistics.median(samples)
    p95 = statistics.quantiles(samples, n=100)[94]
    p99 = statistics.quantiles(samples, n=100)[98]

    print("metric,value")
    print(f"mean,{mean:.4f}")
    print(f"p50,{p50:.4f}")
    print(f"p95,{p95:.4f}")
    print(f"p99,{p99:.4f}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Benchmark /analysis latency")
    parser.add_argument("--url", default="http://localhost:8000", help="Base API URL")
    parser.add_argument("--requests", type=int, default=20, help="Total number of requests")
    parser.add_argument("--concurrency", type=int, default=5, help="Concurrent requests")

    args = parser.parse_args()

    try:
        samples = asyncio.run(run_benchmark(args.url, args.requests, args.concurrency))
        print_stats(samples)
    except Exception as exc:
        print(f"benchmark-error,{exc}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())