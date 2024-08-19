from fastapi import WebSocket
async def sync_media(websocket: WebSocket, data: str):
    # Logic to sync play/pause actions and seek events
    await websocket.send_text(f"Sync data: {data}")
