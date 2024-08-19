from fastapi import WebSocket
async def handle_sync(websocket: WebSocket):
    # Handle incoming data (e.g., play/pause events, sync timestamps)
    while True:
        data = await websocket.receive_text()
        # Process the data to sync playback
        await sync_media(websocket, data)
