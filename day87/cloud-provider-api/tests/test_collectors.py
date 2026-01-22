import pytest
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
from app.collectors.ec2_collector import EC2Collector
from app.collectors.rds_collector import RDSCollector
from app.collectors.s3_collector import S3Collector

@pytest.mark.asyncio
async def test_ec2_collector():
    """Test EC2 collector"""
    collector = EC2Collector()
    instances = await collector.collect_all_instances()
    
    assert isinstance(instances, list)
    print(f"✓ Collected {len(instances)} EC2 instances")

@pytest.mark.asyncio
async def test_rds_collector():
    """Test RDS collector"""
    collector = RDSCollector()
    databases = await collector.collect_all_databases()
    
    assert isinstance(databases, list)
    print(f"✓ Collected {len(databases)} RDS databases")

@pytest.mark.asyncio
async def test_s3_collector():
    """Test S3 collector"""
    collector = S3Collector()
    buckets = await collector.collect_all_buckets()
    
    assert isinstance(buckets, list)
    print(f"✓ Collected {len(buckets)} S3 buckets")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
