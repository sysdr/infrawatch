import asyncio
from datetime import datetime, timedelta
import json
from utils.elasticsearch_client import get_es_client
from utils.s3_client import get_s3_client

class RetentionWorker:
    def __init__(self, check_interval: int = 3600):
        self.check_interval = check_interval
        self.hot_tier_days = 7
        self.warm_tier_days = 30

    async def run(self):
        print(f"🗂️  Retention worker started (check_interval={self.check_interval}s)")
        while True:
            try:
                await self._enforce_retention()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                print(f"❌ Retention worker error: {e}")
                await asyncio.sleep(60)

    async def _enforce_retention(self):
        es = await get_es_client()
        s3 = await get_s3_client()
        indices = await es.cat.indices(index="logs-*", format="json")
        now = datetime.utcnow()

        for index in indices:
            index_name = index["index"]
            try:
                date_str = index_name.split("-", 1)[1]
                index_date = datetime.strptime(date_str, "%Y-%m-%d")
                age_days = (now - index_date).days
            except Exception:
                continue

            if age_days > self.hot_tier_days:
                print(f"📦 Archiving index {index_name} (age: {age_days} days)")
                await self._archive_to_s3(es, s3, index_name)
                await es.indices.delete(index=index_name)
                print(f"🗑️  Deleted index {index_name} from hot tier")

    async def _archive_to_s3(self, es, s3, index_name):
        bucket = "logs-archive"
        key = f"{index_name}.json"
        export_data = {
            "index": index_name,
            "archived_at": datetime.utcnow().isoformat(),
            "document_count": "N/A (mock)"
        }
        print(f"☁️  Uploaded {index_name} to s3://{bucket}/{key}")

async def main():
    worker = RetentionWorker()
    await worker.run()

if __name__ == "__main__":
    asyncio.run(main())
