import os
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from generator import send_daily_thought
from bot_handler import main as bot_main
import threading

def run_bot_handler():
    bot_main()

async def main():
    # Start bot handler in background
    bot_thread = threading.Thread(target=run_bot_handler)
    bot_thread.daemon = True
    bot_thread.start()
    
    # Setup scheduler for daily thoughts at 7 AM
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        send_daily_thought,
        CronTrigger(hour=7, minute=0),
        id='daily_thought'
    )
    scheduler.start()
    
    print("🚀 Daily Thought Motivator deployed!")
    print("📅 Daily thoughts at 7:00 AM")
    print("🤖 Bot handler running 24/7")
    
    # Keep running forever
    try:
        while True:
            await asyncio.sleep(60)
    except KeyboardInterrupt:
        scheduler.shutdown()

if __name__ == "__main__":
    asyncio.run(main())