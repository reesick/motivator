# generator.py
import os
import asyncio
from datetime import datetime
from dotenv import load_dotenv
from telegram import Bot
import google.generativeai as genai
from database import get_thought_base, save_thought_history, get_all_thoughts

load_dotenv()

# Setup
bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')
YOUR_CHAT_ID = os.getenv("YOUR_TELEGRAM_CHAT_ID")  # Add this to .env

def generate_thought():
    thought_base = get_thought_base()
    prompt = f"""Based on this personality profile, create a short motivational thought (2-3 sentences):
    
    {thought_base}
    
    Make it inspiring, practical, and personal. No quotes from famous people."""
    
    response = model.generate_content(prompt)
    return response.text.strip()

def check_duplicate(new_thought):
    existing_thoughts = get_all_thoughts()
    new_words = set(new_thought.lower().split())
    
    for existing in existing_thoughts:
        existing_words = set(existing.lower().split())
        similarity = len(new_words.intersection(existing_words)) / len(new_words.union(existing_words))
        if similarity > 0.7:  # 70% similarity threshold
            return True
    return False

async def send_daily_thought():
    for attempt in range(3):
        thought = generate_thought()
        if not check_duplicate(thought):
            break
    
    # Save to database
    thought_base_snapshot = get_thought_base()
    thought_id = save_thought_history(thought, thought_base_snapshot)
    
    # Send via Telegram
    message = f"""🌟 *Daily Thought*

{thought}

Rate this thought (1-10):
Reply with just the number!"""
    
    await bot.send_message(chat_id=YOUR_CHAT_ID, text=message, parse_mode='Markdown')
    print(f"✅ Thought sent at {datetime.now()}")

if __name__ == "__main__":
    asyncio.run(send_daily_thought())