from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine
from app.core import core_models, roles, auth
from app.file_upload import file_models, files
from fastapi.staticfiles import StaticFiles

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

