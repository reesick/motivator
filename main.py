# main.py - Combined runner
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from generator import send_daily_thought
from rating_handler import main as rating_main
from input_handler import main as input_main
import threading

def run_rating_handler():
    rating_main()

def run_input_handler():
    input_main()

async def main():
    # Start background handlers
    rating_thread = threading.Thread(target=run_rating_handler)
    rating_thread.daemon = True
    rating_thread.start()
    
    input_thread = threading.Thread(target=run_input_handler)  
    input_thread.daemon = True
    input_thread.start()
    
    # Setup scheduler for daily thoughts
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        send_daily_thought,
        CronTrigger(hour=7, minute=0),  # 7:00 AM daily
        id='daily_thought'
    )
    scheduler.start()
    
    print("🚀 Daily Thought Motivator started!")
    print("📅 Daily thoughts at 7:00 AM")
    print("🤖 Rating & story handlers running...")
    
    # Keep running
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        scheduler.shutdown()

if __name__ == "__main__":
    asyncio.run(main())