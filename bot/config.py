import os
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
if not BOT_TOKEN:
    logger.warning("BOT_TOKEN not set! Bot will not start.")

ADMIN_IDS = []
_admin_ids_str = os.getenv("ADMIN_IDS", "")
if _admin_ids_str:
    ADMIN_IDS = [int(x.strip()) for x in _admin_ids_str.split(",") if x.strip().isdigit()]

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///zasol.db")

WHITEPAGES_API_KEY = os.getenv("WHITEPAGES_API_KEY", "")
NUMVERIFY_API_KEY = os.getenv("NUMVERIFY_API_KEY", "")
USE_SCRAPING = os.getenv("USE_SCRAPING", "true").lower() in ("true", "1", "yes")

# ScraperAPI — обходит Cloudflare (5000 free credits, 7-day trial)
# Регистрация: https://www.scraperapi.com/signup
SCRAPERAPI_KEY = os.getenv("SCRAPERAPI_KEY", "8ddcaf1d2ac711a88569c17db597b4ed")

REDIS_URL = os.getenv("REDIS_URL", "")
