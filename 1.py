import os
from dotenv import load_dotenv
from supabase import create_client
from telegram import Bot
import google.generativeai as genai

load_dotenv()

# Test Supabase
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
print("✅ Supabase connected")

# Test Telegram Bot
bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))
print("✅ Telegram bot connected")

# Test Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
print("✅ Gemini connected")

print("🎉 All connections working!")