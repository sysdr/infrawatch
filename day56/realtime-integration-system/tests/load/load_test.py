import asyncio
import websockets
import json
import time
from datetime import datetime

async def simulate_client(client_id, duration=60):
    """Simulate a single client"""
    uri = f"ws://localhost:8000/ws/{client_id}"
    message_count = 0
    
    try:
        async with websockets.connect(uri) as websocket:
            # Wait for connection
            await websocket.recv()
            
            start_time = time.time()
            
            while time.time() - start_time < duration:
                # Send ping
                await websocket.send(json.dumps({"type": "ping"}))
                
                # Wait for pong
                response = await websocket.recv()
                message_count += 1
                
                await asyncio.sleep(1)
    
    except Exception as e:
        print(f"Client {client_id} error: {e}")
    
    return message_count

async def load_test(num_clients=100, duration=60):
    """Run load test with multiple clients"""
    print(f"Starting load test: {num_clients} clients for {duration}s")
    
    start_time = datetime.now()
    
    # Create clients
    tasks = [
        simulate_client(f"load_client_{i}", duration)
        for i in range(num_clients)
    ]
    
    # Run all clients
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    end_time = datetime.now()
    duration_actual = (end_time - start_time).total_seconds()
    
    # Calculate stats
    successful_clients = sum(1 for r in results if isinstance(r, int))
    total_messages = sum(r for r in results if isinstance(r, int))
    
    print(f"\nLoad Test Results:")
    print(f"Duration: {duration_actual:.2f}s")
    print(f"Successful clients: {successful_clients}/{num_clients}")
    print(f"Total messages: {total_messages}")
    print(f"Messages/sec: {total_messages/duration_actual:.2f}")
    print(f"Avg messages/client: {total_messages/successful_clients:.2f}")

if __name__ == "__main__":
    asyncio.run(load_test(num_clients=100, duration=30))
