import asyncio
import json

import websockets


async def test_ws():
    uri = "ws://localhost:8001/api/simulate?config=colony_v4.json"
    try:
        async with websockets.connect(uri) as ws:
            print("Connected.")
            while True:
                msg = await ws.recv()
                data = json.loads(msg)
                tick = data.get("tick", "init")
                print(f"raw event: {data.get('type')} at tick: {tick}")
                if data.get("type") == "end":
                    print(f"END event data: {data}")
                    break
                if data.get("type") == "error":
                    print(f"ERROR event from server: {data}")
                    break
    except websockets.exceptions.ConnectionClosed as e:
        print(f"Connection closed. Code: {e.code}, Reason: {e.reason}")
    except Exception as e:
        print(f"Exception: {e}")

asyncio.run(test_ws())
