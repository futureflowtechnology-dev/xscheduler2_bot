import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# =========================
# REQUIRED SETTINGS
# =========================

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN is missing in .env file")

# =========================
# OPTIONAL SETTINGS
# =========================

ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

DEFAULT_SEND_DELAY = int(os.getenv("DEFAULT_SEND_DELAY", "5"))

MAX_QUEUE_SIZE = int(os.getenv("MAX_QUEUE_SIZE", "1000"))

SCHEDULE_TIMEZONE = os.getenv("SCHEDULE_TIMEZONE", "Asia/Kolkata")