from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

BASE_DIR = Path(__file__).parent

DB_DIR = BASE_DIR / "db"
DB_DIR.mkdir(exist_ok=True)

DATABASE_PATH = DB_DIR / "bot_database.db"

BOT_TOKEN = os.getenv('BOT_TOKEN')