from fastapi import FastAPI, WebSocket, Request
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine
from app.core import core_models, roles, auth
from app.file_upload import file_models, files
from fastapi.staticfiles import StaticFiles
from app.ws import ws, device_models
from fastapi.templating import Jinja2Templates
import json

# create tables
core_models.Base.metadata.create_all(bind=engine)
file_models.Base.metadata.create_all(bind=engine)
device_models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def get(request: Request):
    context = {"request": request, "message": "Devices"}
    return templates.TemplateResponse("index.html", context)

app.include_router(roles.router, tags=['Roles'], prefix='/api/role')
app.include_router(auth.router, tags=['Auth'], prefix='/api/auth')
app.include_router(files.router, tags=['Files'], prefix='/api/auth')

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/user/{client_id}/ws")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    send_data = ws.device_operations({})
    await manager.broadcast(json.dumps(send_data))
    try:
        while True:
            data = await websocket.receive_text()
            send_data = ws.device_operations(data)
            await manager.broadcast(json.dumps(send_data))
    except Exception as e:
        manager.disconnect(websocket)
        await manager.broadcast(json.dumps({"status":404,"message":"web socket disconnected"}))