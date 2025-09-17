# rating_handler.py
import os
import asyncio
from datetime import datetime, timedelta
from dotenv import load_dotenv
from telegram import Bot
from telegram.ext import Application, MessageHandler, filters
import google.generativeai as genai
from database import get_today_thought_id, update_rating, get_thought_base, update_thought_base

load_dotenv()

# Setup
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-pro')
YOUR_CHAT_ID = os.getenv("YOUR_TELEGRAM_CHAT_ID")

def extract_rating(text):
    # Look for numbers 1-10 in the message
    import re
    numbers = re.findall(r'\b([1-9]|10)\b', text)
    return int(numbers[0]) if numbers else None

def update_thought_base_with_rating(rating, thought_text):
    current_base = get_thought_base()
    
    if rating >= 7:
        # High rating - add positive theme
        prompt = f"""Based on this highly rated thought: "{thought_text}"
        
        Extract the main theme in one short line starting with "User likes thoughts about"
        Example: "User likes thoughts about taking action and overcoming fear."
        """
    else:
        # Low rating - add avoidance
        prompt = f"""Based on this low-rated thought: "{thought_text}"
        
        Extract what to avoid in one short line starting with "User dislikes thoughts about"
        Example: "User dislikes thoughts about abstract concepts without practical steps."
        """
    
    response = model.generate_content(prompt)
    new_line = response.text.strip()
    
    updated_base = current_base + " " + new_line
    update_thought_base(updated_base)

async def handle_rating(update, context):
    if str(update.message.chat_id) != YOUR_CHAT_ID:
        return
    
    rating = extract_rating(update.message.text)
    if rating:
        thought_id = get_today_thought_id()
        if thought_id:
            update_rating(thought_id, rating)
            
            # Get today's thought text for updating base
            from database import supabase
            thought_result = supabase.table("thought_history").select("thought_text").eq("id", thought_id).execute()
            thought_text = thought_result.data[0]["thought_text"] if thought_result.data else ""
            
            # Update thought base
            update_thought_base_with_rating(rating, thought_text)
            
            await update.message.reply_text(f"✅ Rating {rating} saved! I'll learn from this.")
        else:
            await update.message.reply_text("No thought found for today to rate.")

def main():
    app = Application.builder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_rating))
    
    print("🤖 Rating handler started...")
    app.run_polling()

if __name__ == "__main__":
    main()

# input_handler.py
import os
import asyncio
from dotenv import load_dotenv
from telegram import Bot
from telegram.ext import Application, MessageHandler, filters
import google.generativeai as genai
from database import get_thought_base, update_thought_base

load_dotenv()

# Setup
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-pro')
YOUR_CHAT_ID = os.getenv("YOUR_TELEGRAM_CHAT_ID")

def extract_story_seed(story_text):
    prompt = f"""Extract a motivational seed from this personal story in one short line:

Story: {story_text}

Format: "User finds motivation in [specific theme/approach]"
Example: "User finds motivation in small daily wins and consistent progress"
"""
    
    response = model.generate_content(prompt)
    return response.text.strip()

async def handle_story_input(update, context):
    if str(update.message.chat_id) != YOUR_CHAT_ID:
        return
    
    # Check if message starts with "Story:" or is long enough to be a story
    message_text = update.message.text
    if message_text.lower().startswith("story:") or len(message_text) > 50:
        # Extract story seed
        story_seed = extract_story_seed(message_text)
        
        # Update thought base
        current_base = get_thought_base()
        updated_base = current_base + " " + story_seed
        update_thought_base(updated_base)
        
        await update.message.reply_text(f"✅ Story added to your profile!\n\nExtracted: {story_seed}")

def main():
    app = Application.builder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_story_input))
    
    print("📖 Story handler started...")
    app.run_polling()

if __name__ == "__main__":
    main()