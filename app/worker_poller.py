# app/worker_poller.py
import asyncio
import os
from datetime import datetime
import asyncpg
import time

DSN = os.getenv(
    "SYNC_DATABASE_URL"
)  # example: postgresql://postgres:postgres@db:5432/oneeye

QUERY = """
SELECT id, patient_id, red_flag, next_rescreen_on FROM recommendation_state
WHERE status='active' AND next_rescreen_on <= now()
"""


def handle_due(row):
    # implement: send notification, update next_rescreen_on or mark resolved
    print("Handling due", row)


async def loop():
    conn = await asyncpg.connect(DSN)
    try:
        while True:
            rows = await conn.fetch(QUERY)
            for r in rows:
                handle_due(r)
            await asyncio.sleep(60)  # configurable
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(loop())
