import os
import re
from dotenv import load_dotenv
from telegram.ext import Application, MessageHandler, filters
import google.generativeai as genai
from database import get_today_thought_id, update_rating, get_thought_base, update_thought_base, get_thought_by_id

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')
YOUR_CHAT_ID = os.getenv("YOUR_TELEGRAM_CHAT_ID")

async def handle_message(update, context):
    if str(update.message.chat_id) != YOUR_CHAT_ID:
        return
    
    text = update.message.text
    
    # Handle ratings (1-10)
    numbers = re.findall(r'\b([1-9]|10)\b', text)
    if len(numbers) == 1 and len(text.split()) <= 2:
        rating = int(numbers[0])
        thought_id = get_today_thought_id()
        if thought_id:
            update_rating(thought_id, rating)
            
            # Get today's thought text and update thought base
            thought_text = get_thought_by_id(thought_id)
            
            # Update thought base based on rating
            current_base = get_thought_base()
            if rating >= 7:
                prompt = f'Extract the main theme from this highly rated thought: "{thought_text}". Format: "User likes thoughts about [theme]"'
            else:
                prompt = f'Extract what to avoid from this low-rated thought: "{thought_text}". Format: "User dislikes thoughts about [theme]"'
            
            try:
                response = model.generate_content(prompt)
                new_line = response.text.strip()
                updated_base = current_base + " " + new_line
                update_thought_base(updated_base)
                await update.message.reply_text(f"Rating {rating} saved! I'll learn from this.")
            except Exception as e:
                await update.message.reply_text(f"Rating {rating} saved!")
                
        else:
            await update.message.reply_text("No thought found for today.")
    
    # Handle stories
    elif text.lower().startswith("story:") or len(text) > 50:
        try:
            # Summarize story properly
            prompt = f'Extract a motivational seed from this story in one line: "{text}". Format: "User finds motivation in [specific approach]"'
            response = model.generate_content(prompt)
            story_seed = response.text.strip()
            
            current_base = get_thought_base()
            updated_base = current_base + " " + story_seed
            update_thought_base(updated_base)
            
            await update.message.reply_text(f"Story added!\n\nExtracted: {story_seed}")
        except Exception as e:
            # Fallback if AI fails
            current_base = get_thought_base()
            updated_base = current_base + f" User shared: {text[:100]}"
            update_thought_base(updated_base)
            await update.message.reply_text("Story added to your profile!")

def main():
    app = Application.builder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Bot handler started...")
    app.run_polling()

if __name__ == "__main__":
    main()