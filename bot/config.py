import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS", "").split(","))) if os.getenv("ADMIN_IDS") else []
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///zasol.db")

WHITEPAGES_API_KEY = os.getenv("WHITEPAGES_API_KEY", "")
NUMVERIFY_API_KEY = os.getenv("NUMVERIFY_API_KEY", "")
USE_SCRAPING = os.getenv("USE_SCRAPING", "true").lower() == "true"
REDIS_URL = os.getenv("REDIS_URL", "")
