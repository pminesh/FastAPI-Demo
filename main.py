from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine
from app.core import core_models, roles, auth
from app.file_upload import file_models, files
from fastapi.staticfiles import StaticFiles
from app.ws import ws

# create tables
core_models.Base.metadata.create_all(bind=engine)
file_models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(roles.router, tags=['Roles'], prefix='/api/role')
app.include_router(auth.router, tags=['Auth'], prefix='/api/auth')
app.include_router(files.router, tags=['Files'], prefix='/api/auth')

connected_clients = set() # Keep track of connected clients

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.add(websocket)  # Add the connected client to the set
    try:
        while True:
            data = await websocket.receive_text()
            ws.device_operations(data)
            
            # Send message to all connected clients
            await broadcast_message(data)

    except Exception as e:
        connected_clients.remove(websocket)  # Remove from the set
        print('connected_clients: ', connected_clients)

async def broadcast_message(message: str):
    for client in connected_clients:
        await client.send_text(message)