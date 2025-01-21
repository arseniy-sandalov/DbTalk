# app.py
import sys
sys.path.append("..")

from fastapi import FastAPI
from llm.llm_api import router as llm_router
from authentication.auth_api import router as auth_router
from chats.chat_db import router as conversation_router
from fastapi.middleware.cors import CORSMiddleware
from mys_db.create_db import create_db
from config_parser import read_config

config_path = "shared/config.ini"
config_values = read_config(config_path)

if (config_values['MysDB']['db_autoupdate']):
    create_db('shared/MysFinal_db.db')

app = FastAPI()


# Include all routers
app.include_router(auth_router)
app.include_router(llm_router)
app.include_router(conversation_router)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

''' Add console-based resource monitor...'''