import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

def get_thought_base():
    result = supabase.table("thought_base").select("content").order("updated_at", desc=True).limit(1).execute()
    return result.data[0]["content"] if result.data else "You are motivated by personal growth."

def update_thought_base(new_content):
    supabase.table("thought_base").update({"content": new_content}).eq("id", get_thought_base_id()).execute()

def get_thought_base_id():
    result = supabase.table("thought_base").select("id").order("updated_at", desc=True).limit(1).execute()
    return result.data[0]["id"] if result.data else None

def save_thought_history(thought_text, source_snapshot):
    result = supabase.table("thought_history").insert({
        "thought_text": thought_text,
        "source_snapshot": source_snapshot
    }).execute()
    return result.data[0]["id"]

def get_all_thoughts():
    result = supabase.table("thought_history").select("thought_text").execute()
    return [row["thought_text"] for row in result.data]

def update_rating(thought_id, rating):
    supabase.table("thought_history").update({"rating": rating}).eq("id", thought_id).execute()

def get_today_thought_id():
    from datetime import datetime
    today = datetime.now().strftime("%Y-%m-%d")
    result = supabase.table("thought_history").select("id").gte("date_sent", today).execute()
    return result.data[0]["id"] if result.data else None