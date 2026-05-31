import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

import mysql.connector
from app.config import DB_CONFIG

def connect_db():
    return mysql.connector.connect(**DB_CONFIG)