import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

def get_connection():
    """Create database connection"""
    return psycopg2.connect(
        os.getenv("SUPABASE_URL"),
        cursor_factory=RealDictCursor
    )

def get_thought_base():
    """Get the latest thought base content"""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT content FROM thought_base ORDER BY updated_at DESC LIMIT 1")
        result = cur.fetchone()
        return result['content'] if result else "You are motivated by personal growth."
    finally:
        conn.close()

def update_thought_base(new_content):
    """Update the thought base content"""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "UPDATE thought_base SET content = %s, updated_at = %s WHERE id = %s",
            (new_content, datetime.now(), get_thought_base_id())
        )
        conn.commit()
    finally:
        conn.close()

def get_thought_base_id():
    """Get the ID of the current thought base"""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT id FROM thought_base ORDER BY updated_at DESC LIMIT 1")
        result = cur.fetchone()
        return result['id'] if result else None
    finally:
        conn.close()

def save_thought_history(thought_text, source_snapshot):
    """Save a new thought to history"""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO thought_history (thought_text, source_snapshot, date_sent) VALUES (%s, %s, %s) RETURNING id",
            (thought_text, source_snapshot, datetime.now())
        )
        result = cur.fetchone()
        conn.commit()
        return result['id']
    finally:
        conn.close()

def get_all_thoughts():
    """Get all previous thoughts for duplicate checking"""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT thought_text FROM thought_history")
        results = cur.fetchall()
        return [row['thought_text'] for row in results]
    finally:
        conn.close()

def update_rating(thought_id, rating):
    """Update rating for a specific thought"""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "UPDATE thought_history SET rating = %s WHERE id = %s",
            (rating, thought_id)
        )
        conn.commit()
    finally:
        conn.close()

def get_today_thought_id():
    """Get today's thought ID"""
    conn = get_connection()
    try:
        cur = conn.cursor()
        today = datetime.now().strftime("%Y-%m-%d")
        cur.execute(
            "SELECT id FROM thought_history WHERE date_sent::date = %s ORDER BY date_sent DESC LIMIT 1",
            (today,)
        )
        result = cur.fetchone()
        return result['id'] if result else None
    finally:
        conn.close()

def get_thought_by_id(thought_id):
    """Get thought text by ID"""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT thought_text FROM thought_history WHERE id = %s", (thought_id,))
        result = cur.fetchone()
        return result['thought_text'] if result else ""
    finally:
        conn.close()