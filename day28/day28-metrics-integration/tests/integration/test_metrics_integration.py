import pytest
import asyncio
import httpx
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000/api/v1"

class TestMetricsIntegration:
    
    @pytest.fixture(autouse=True)
    async def setup(self):
        """Setup for each test"""
        self.client = httpx.AsyncClient(base_url=BASE_URL, timeout=30.0)
        yield
        await self.client.aclose()
    
    async def test_health_check(self):
        """Test system health check"""
        response = await self.client.get("/health")
        assert response.status_code == 200
        
        health = response.json()
        assert "status" in health
        assert "database" in health
        assert "redis" in health
        assert health["database"] is True
        assert health["redis"] is True
    
    async def test_create_single_metric(self):
        """Test creating a single metric"""
        metric = {
            "name": "test_metric",
            "value": 42.5,
            "source": "test_source",
            "tags": {"test": "value"}
        }
        
        response = await self.client.post("/metrics", json=metric)
        assert response.status_code == 200
        
        result = response.json()
        assert result["name"] == metric["name"]
        assert result["value"] == metric["value"]
        assert result["source"] == metric["source"]
        assert "id" in result
        assert "timestamp" in result
    
    async def test_create_batch_metrics(self):
        """Test creating metrics in batch"""
        metrics = [
            {
                "name": f"batch_metric_{i}",
                "value": float(i * 10),
                "source": "batch_test",
                "tags": {"batch": "test", "index": str(i)}
            }
            for i in range(5)
        ]
        
        response = await self.client.post("/metrics/batch", json={"metrics": metrics})
        assert response.status_code == 200
        
        result = response.json()
        assert result["created"] == 5
        assert result["status"] == "success"
    
    async def test_query_metrics(self):
        """Test querying metrics with filters"""
        # First create some test metrics
        await self.test_create_batch_metrics()
        
        # Query all metrics
        response = await self.client.get("/metrics")
        assert response.status_code == 200
        
        metrics = response.json()
        assert isinstance(metrics, list)
        assert len(metrics) > 0
        
        # Query with filters
        response = await self.client.get("/metrics", params={"source": "batch_test"})
        assert response.status_code == 200
        
        filtered_metrics = response.json()
        assert len(filtered_metrics) >= 5  # At least our batch
        
        for metric in filtered_metrics:
            assert metric["source"] == "batch_test"
    
    async def test_realtime_metrics(self):
        """Test realtime metrics from Redis"""
        # Create a metric first
        metric = {
            "name": "realtime_test",
            "value": 99.9,
            "source": "realtime_source"
        }
        
        await self.client.post("/metrics", json=metric)
        
        # Check realtime endpoint
        response = await self.client.get("/metrics/realtime")
        assert response.status_code == 200
        
        result = response.json()
        assert "metrics" in result
        assert "timestamp" in result
        
        # Should have our metric in Redis
        metrics = result["metrics"]
        assert isinstance(metrics, dict)
    
    async def test_metric_summary(self):
        """Test metric summary statistics"""
        # Create multiple metrics with same name
        base_metric = {
            "name": "summary_test",
            "source": "summary_source"
        }
        
        values = [10.0, 20.0, 30.0, 40.0, 50.0]
        for value in values:
            metric = {**base_metric, "value": value}
            await self.client.post("/metrics", json=metric)
        
        # Get summary
        response = await self.client.get("/metrics/summary_test/summary")
        assert response.status_code == 200
        
        summary = response.json()
        assert summary["name"] == "summary_test"
        assert summary["count"] >= 5
        assert summary["min_value"] <= 10.0
        assert summary["max_value"] >= 50.0
        assert 10.0 <= summary["avg_value"] <= 50.0
    
    async def test_error_handling(self):
        """Test error handling for invalid requests"""
        # Invalid metric (missing required fields)
        invalid_metric = {"name": "test"}
        response = await self.client.post("/metrics", json=invalid_metric)
        assert response.status_code == 422  # Validation error
        
        # Invalid metric name
        invalid_name_metric = {
            "name": "invalid name with spaces!",
            "value": 10.0,
            "source": "test"
        }
        response = await self.client.post("/metrics", json=invalid_name_metric)
        assert response.status_code == 422
        
        # Query non-existent metric summary
        response = await self.client.get("/metrics/nonexistent_metric/summary")
        assert response.status_code == 200  # Should return empty summary
        
        summary = response.json()
        assert summary["count"] == 0
    
    async def test_performance_under_load(self):
        """Test system performance with concurrent requests"""
        # Create 50 concurrent metric creation requests
        async def create_metric(i):
            metric = {
                "name": f"perf_test_{i % 10}",  # 10 different metric names
                "value": float(i),
                "source": f"perf_source_{i % 5}",  # 5 different sources
                "tags": {"test": "performance", "batch": str(i // 10)}
            }
            response = await self.client.post("/metrics", json=metric)
            return response.status_code == 200
        
        # Run concurrent requests
        start_time = datetime.now()
        tasks = [create_metric(i) for i in range(50)]
        results = await asyncio.gather(*tasks)
        end_time = datetime.now()
        
        # Check results
        success_count = sum(results)
        total_time = (end_time - start_time).total_seconds()
        
        print(f"Created {success_count}/50 metrics in {total_time:.2f}s")
        print(f"Rate: {success_count/total_time:.2f} metrics/second")
        
        # Should have > 90% success rate and reasonable performance
        assert success_count >= 45  # 90% success rate
        assert total_time < 10.0  # Should complete within 10 seconds
    
    async def test_data_consistency(self):
        """Test data consistency between database and Redis"""
        metric = {
            "name": "consistency_test",
            "value": 123.45,
            "source": "consistency_source",
            "tags": {"test": "consistency"}
        }
        
        # Create metric
        response = await self.client.post("/metrics", json=metric)
        assert response.status_code == 200
        
        created_metric = response.json()
        
        # Check in database (via query)
        response = await self.client.get("/metrics", params={
            "name": "consistency_test",
            "source": "consistency_source"
        })
        assert response.status_code == 200
        
        db_metrics = response.json()
        assert len(db_metrics) >= 1
        
        # Find our metric
        our_metric = next(m for m in db_metrics if m["id"] == created_metric["id"])
        assert our_metric["name"] == metric["name"]
        assert our_metric["value"] == metric["value"]
        assert our_metric["source"] == metric["source"]
        
        # Check in Redis (via realtime endpoint)
        response = await self.client.get("/metrics/realtime")
        assert response.status_code == 200
        
        realtime_data = response.json()
        redis_metrics = realtime_data["metrics"]
        
        # Should find a matching metric in Redis
        found_in_redis = False
        for key, redis_metric in redis_metrics.items():
            if (redis_metric.get("name") == metric["name"] and 
                redis_metric.get("value") == metric["value"] and
                redis_metric.get("source") == metric["source"]):
                found_in_redis = True
                break
        
        assert found_in_redis, "Metric not found in Redis cache"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
