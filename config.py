# config.py
import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Settings
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
YOUR_TELEGRAM_CHAT_ID = os.getenv("YOUR_TELEGRAM_CHAT_ID")

# AI Settings  
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Database Settings
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Scheduler Settings
DAILY_SEND_TIME = "07:00"  # 7 AM
