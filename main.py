# coding: utf-8

from fastapi import FastAPI, WebSocket

from models.session import get_session

from v1.auth import router as auth_router
from v1.events import router as events_router


app = FastAPI(root_path="/api")

app.include_router(auth_router)
app.include_router(events_router)


@app.get("/")
async def root() -> dict:
    async with get_session() as s:
        return {"response": "Heil"}


@app.websocket("/ws/{id}")
async def notify(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_json()

        await websocket.send_text(f"New Event: {data.get('id')}")
