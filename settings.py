import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Flask Configuration
SECRET_KEY = os.getenv("SECRET", "default-secret-key")
SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///app/data/db.sqlite3")
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Admin Credentials
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "password")

# Bot Webhook Configuration
BOT_WEBHOOK_URL = os.getenv("BOT_WEBHOOK_URL", "")
BOT_WEBHOOK_SECRET = os.getenv("BOT_WEBHOOK_SECRET", "")
