from elasticsearch import AsyncElasticsearch
import os

_es_client = None

async def get_es_client():
    """Get Elasticsearch client singleton"""
    global _es_client

    if _es_client is None:
        es_host = os.getenv("ELASTICSEARCH_HOST", "localhost")
        es_port = int(os.getenv("ELASTICSEARCH_PORT", "9200"))

        _es_client = AsyncElasticsearch(
            hosts=[f"http://{es_host}:{es_port}"],
            verify_certs=False
        )

        await _ensure_index_template(_es_client)

    return _es_client

async def _ensure_index_template(es):
    template = {
        "index_patterns": ["logs-*"]
        ,
        "template": {
            "settings": {
                "number_of_shards": 2,
                "number_of_replicas": 1
            },
            "mappings": {
                "properties": {
                    "timestamp": {"type": "date"},
                    "level": {"type": "keyword"},
                    "service": {"type": "keyword"},
                    "message": {"type": "text"},
                    "metadata": {"type": "object"}
                }
            }
        }
    }

    try:
        await es.indices.put_index_template(name="logs-template", body=template)
        print("✅ Elasticsearch index template created")
    except Exception as e:
        print(f"⚠️  Index template error: {e}")
