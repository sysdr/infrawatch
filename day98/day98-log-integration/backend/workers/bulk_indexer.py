import asyncio
import json
from datetime import datetime
from typing import List
from utils.redis_client import get_redis_client
from utils.elasticsearch_client import get_es_client

class BulkIndexer:
    def __init__(self, batch_size: int = 500, flush_interval: float = 5.0):
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.batch: List[dict] = []
        self.last_flush = datetime.utcnow()

    async def run(self):
        print(f"🔄 Bulk indexer started (batch_size={self.batch_size}, flush_interval={self.flush_interval}s)")
        redis = await get_redis_client()
        es = await get_es_client()

        while True:
            try:
                log_data = await redis.brpop("index-queue", timeout=1)

                if log_data:
                    _, log_json = log_data
                    log = json.loads(log_json)
                    self.batch.append(log)

                should_flush = (
                    len(self.batch) >= self.batch_size or
                    (datetime.utcnow() - self.last_flush).total_seconds() >= self.flush_interval
                )

                if should_flush and self.batch:
                    await self._flush_batch(es, redis)
            except Exception as e:
                print(f"❌ Bulk indexer error: {e}")
                await asyncio.sleep(1)

    async def _flush_batch(self, es, redis):
        if not self.batch:
            return

        bulk_body = []
        for log in self.batch:
            date_str = log.get("timestamp", datetime.utcnow().isoformat())[:10]
            index_name = f"logs-{date_str}"
            bulk_body.append({
                "index": {
                    "_index": index_name,
                    "_id": log.get("id")
                }
            })
            bulk_body.append(log)

        try:
            result = await es.bulk(body=bulk_body)
            indexed_count = len(self.batch)
            await redis.incrby("metrics:logs:indexed", indexed_count)
            print(f"✅ Indexed {indexed_count} logs (errors: {result.get('errors', False)})")
            self.batch.clear()
            self.last_flush = datetime.utcnow()
        except Exception as e:
            print(f"❌ Bulk index failed: {e}")
            await asyncio.sleep(5)

async def main():
    indexer = BulkIndexer()
    await indexer.run()

if __name__ == "__main__":
    asyncio.run(main())
