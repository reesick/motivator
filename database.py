import os
import asyncio
import asyncpg
from dotenv import load_dotenv
from datetime import datetime
from urllib.parse import urlparse

load_dotenv()

async def get_connection():
    """Create async database connection"""
    url = os.getenv("SUPABASE_URL")
    return await asyncpg.connect(url)

async def get_thought_base():
    """Get the latest thought base content"""
    conn = await get_connection()
    try:
        result = await conn.fetchrow("SELECT content FROM thought_base ORDER BY updated_at DESC LIMIT 1")
        return result['content'] if result else "You are motivated by personal growth."
    finally:
        await conn.close()

async def update_thought_base(new_content):
    """Update the thought base content"""
    conn = await get_connection()
    try:
        base_id = await get_thought_base_id()
        await conn.execute(
            "UPDATE thought_base SET content = $1, updated_at = $2 WHERE id = $3",
            new_content, datetime.now(), base_id
        )
    finally:
        await conn.close()

async def get_thought_base_id():
    """Get the ID of the current thought base"""
    conn = await get_connection()
    try:
        result = await conn.fetchrow("SELECT id FROM thought_base ORDER BY updated_at DESC LIMIT 1")
        return result['id'] if result else None
    finally:
        await conn.close()

async def save_thought_history(thought_text, source_snapshot):
    """Save a new thought to history"""
    conn = await get_connection()
    try:
        result = await conn.fetchrow(
            "INSERT INTO thought_history (thought_text, source_snapshot, date_sent) VALUES ($1, $2, $3) RETURNING id",
            thought_text, source_snapshot, datetime.now()
        )
        return result['id']
    finally:
        await conn.close()

async def get_all_thoughts():
    """Get all previous thoughts for duplicate checking"""
    conn = await get_connection()
    try:
        results = await conn.fetch("SELECT thought_text FROM thought_history")
        return [row['thought_text'] for row in results]
    finally:
        await conn.close()

async def update_rating(thought_id, rating):
    """Update rating for a specific thought"""
    conn = await get_connection()
    try:
        await conn.execute(
            "UPDATE thought_history SET rating = $1 WHERE id = $2",
            rating, thought_id
        )
    finally:
        await conn.close()

async def get_today_thought_id():
    """Get today's thought ID"""
    conn = await get_connection()
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        result = await conn.fetchrow(
            "SELECT id FROM thought_history WHERE date_sent::date = $1 ORDER BY date_sent DESC LIMIT 1",
            today
        )
        return result['id'] if result else None
    finally:
        await conn.close()

async def get_thought_by_id(thought_id):
    """Get thought text by ID"""
    conn = await get_connection()
    try:
        result = await conn.fetchrow("SELECT thought_text FROM thought_history WHERE id = $1", thought_id)
        return result['thought_text'] if result else ""
    finally:
        await conn.close()

# Sync wrappers for non-async code
def get_thought_base_sync():
    return asyncio.run(get_thought_base())

def update_thought_base_sync(new_content):
    return asyncio.run(update_thought_base(new_content))

def save_thought_history_sync(thought_text, source_snapshot):
    return asyncio.run(save_thought_history(thought_text, source_snapshot))

def get_all_thoughts_sync():
    return asyncio.run(get_all_thoughts())

def update_rating_sync(thought_id, rating):
    return asyncio.run(update_rating(thought_id, rating))

def get_today_thought_id_sync():
    return asyncio.run(get_today_thought_id())

def get_thought_by_id_sync(thought_id):
    return asyncio.run(get_thought_by_id(thought_id))