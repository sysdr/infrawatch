import pytest, asyncio
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend'))

def test_run_created():
    from app.services import runner
    import asyncio
    run_id = asyncio.get_event_loop().run_until_complete(
        runner.start_test_run({
            "name": "Unit Test Run",
            "test_type": "load",
            "target_url": "http://localhost:8117",
            "users": 2,
            "duration_seconds": 5,
        })
    )
    assert run_id is not None
    run = runner.get_run(run_id)
    assert run is not None
    assert run["name"] == "Unit Test Run"

def test_get_all_runs_returns_list():
    from app.services import runner
    runs = runner.get_all_runs()
    assert isinstance(runs, list)
