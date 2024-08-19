from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn
import json
import uuid
from pydantic import BaseModel

app = FastAPI()

# Serve static files
app.mount("/media", StaticFiles(directory="media"), name="media")
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/templates", StaticFiles(directory="templates"), name="templates")

# In-memory store for user connections
connected_users = {}  # Stores WebSocket connections
user_connections = {}  # Maps user ID to the connected user ID

class ConnectRequest(BaseModel):
    user_id: str
    target_id: str

@app.get("/")
async def get():
    return HTMLResponse(open("templates/index.html").read())

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await websocket.accept()
    connected_users[user_id] = websocket

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            action = message.get("action")
            time = message.get("time")
            target_id = user_connections.get(user_id)

            if target_id and target_id in connected_users:
                target_client = connected_users[target_id]
                await target_client.send_text(json.dumps({
                    "action": action,
                    "time": time,
                    "source_id": user_id
                }))

    except WebSocketDisconnect:
        if user_id in connected_users:
            del connected_users[user_id]
        if user_id in user_connections:
            target_id = user_connections[user_id]
            if target_id in connected_users:
                target_client = connected_users[target_id]
                await target_client.send_text(json.dumps({
                    "action": "disconnected",
                    "source_id": user_id
                }))
            del user_connections[user_id]

@app.post("/create_id")
async def create_id():
    user_id = str(uuid.uuid4())
    return {"user_id": user_id}

@app.post("/connect")
async def connect(request: ConnectRequest):
    user_id = request.user_id
    target_id = request.target_id

    if not user_id or not target_id:
        raise HTTPException(status_code=400, detail="User ID and Target ID are required")

    if target_id not in connected_users:
        raise HTTPException(status_code=404, detail="Target user not found")

    user_connections[user_id] = target_id
    user_connections[target_id] = user_id

    # Notify both users about the connection
    for id in [user_id, target_id]:
        if id in connected_users:
            await connected_users[id].send_text(json.dumps({
                "action": "connected",
                "partner_id": user_id if id == target_id else target_id
            }))

    return {"status": f"Connected to {target_id}"}

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)