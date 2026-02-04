import asyncio
import json
from datetime import datetime, timedelta
from collections import defaultdict
from utils.elasticsearch_client import get_es_client
from utils.redis_client import get_redis_client

class SecurityCorrelation:
    def __init__(self, check_interval: int = 60, window_minutes: int = 10):
        self.check_interval = check_interval
        self.window_minutes = window_minutes

    async def run(self):
        print(f"🔒 Security correlation started (check_interval={self.check_interval}s, window={self.window_minutes}m)")
        while True:
            try:
                await self._detect_patterns()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                print(f"❌ Security correlation error: {e}")
                await asyncio.sleep(10)

    async def _detect_patterns(self):
        es = await get_es_client()
        redis = await get_redis_client()
        await self._detect_brute_force(es, redis)
        await self._detect_rate_anomalies(es, redis)

    async def _detect_brute_force(self, es, redis):
        now = datetime.utcnow()
        window_start = now - timedelta(minutes=self.window_minutes)
        result = await es.search(
            index="logs-*",
            body={
                "query": {
                    "bool": {
                        "must": [
                            {"term": {"level": "ERROR"}},
                            {"match": {"message": "authentication failed"}},
                            {"range": {"timestamp": {"gte": window_start.isoformat()}}}
                        ]
                    }
                },
                "aggs": {
                    "by_user": {
                        "terms": {"field": "metadata.user_id.keyword"},
                        "aggs": {
                            "unique_ips": {
                                "cardinality": {"field": "metadata.ip.keyword"}
                            }
                        }
                    }
                },
                "size": 0
            }
        )

        for bucket in result.get("aggregations", {}).get("by_user", {}).get("buckets", []):
            user_id = bucket["key"]
            attempt_count = bucket["doc_count"]
            unique_ips = bucket["unique_ips"]["value"]

            if attempt_count >= 5 and unique_ips >= 3:
                await self._trigger_alert(
                    redis,
                    alert_type="credential_stuffing",
                    context={
                        "user_id": user_id,
                        "attempt_count": attempt_count,
                        "unique_ips": unique_ips,
                        "window_minutes": self.window_minutes
                    }
                )

    async def _detect_rate_anomalies(self, es, redis):
        now = datetime.utcnow()
        window_start = now - timedelta(minutes=1)
        result = await es.search(
            index="logs-*",
            body={
                "query": {
                    "range": {"timestamp": {"gte": window_start.isoformat()}}
                },
                "aggs": {
                    "by_endpoint": {
                        "terms": {"field": "metadata.endpoint.keyword", "size": 100},
                        "aggs": {
                            "top_ips": {
                                "terms": {"field": "metadata.ip.keyword", "size": 5}
                            }
                        }
                    }
                },
                "size": 0
            }
        )

        for bucket in result.get("aggregations", {}).get("by_endpoint", {}).get("buckets", []):
            endpoint = bucket["key"]
            request_count = bucket["doc_count"]

            if request_count > 1000:
                top_ips = [ip["key"] for ip in bucket["top_ips"]["buckets"]]
                await self._trigger_alert(
                    redis,
                    alert_type="rate_anomaly",
                    context={
                        "endpoint": endpoint,
                        "request_count": request_count,
                        "top_ips": top_ips,
                        "window_minutes": 1
                    }
                )

    async def _trigger_alert(self, redis, alert_type: str, context: dict):
        dedup_key = f"alert:{alert_type}:{context.get('user_id') or context.get('endpoint')}"

        if await redis.exists(dedup_key):
            existing = json.loads(await redis.get(dedup_key))
            existing["last_seen"] = datetime.utcnow().isoformat()
            existing["occurrence_count"] = existing.get("occurrence_count", 1) + 1
            await redis.setex(dedup_key, 300, json.dumps(existing))
            return

        alert = {
            "id": f"alert-{datetime.utcnow().timestamp()}",
            "alert_type": alert_type,
            "severity": "HIGH",
            "title": self._get_alert_title(alert_type),
            "description": self._get_alert_description(alert_type, context),
            "context": context,
            "triggered_at": datetime.utcnow().isoformat(),
            "resolved": False,
            "occurrence_count": 1
        }

        await redis.setex(dedup_key, 300, json.dumps(alert))
        await redis.incr("metrics:alerts:triggered")
        print(f"🚨 ALERT: {alert['title']} - {alert['description']}")

    def _get_alert_title(self, alert_type: str) -> str:
        titles = {
            "credential_stuffing": "Credential Stuffing Attack Detected",
            "rate_anomaly": "Abnormal Request Rate Detected"
        }
        return titles.get(alert_type, f"Security Alert: {alert_type}")

    def _get_alert_description(self, alert_type: str, context: dict) -> str:
        if alert_type == "credential_stuffing":
            return f"User {context['user_id']} had {context['attempt_count']} failed login attempts from {context['unique_ips']} different IPs"
        elif alert_type == "rate_anomaly":
            return f"Endpoint {context['endpoint']} received {context['request_count']} requests in 1 minute"
        return f"Security pattern detected: {context}"

async def main():
    worker = SecurityCorrelation()
    await worker.run()

if __name__ == "__main__":
    asyncio.run(main())
