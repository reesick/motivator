# Use Python 3.11 (has prebuilt asyncpg wheels)
FROM python:3.11-slim

# Optional: reduce pip noise and speed up
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies first (better cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your code
COPY . .

# Expose nothing (Telegram bot + scheduler don’t need an HTTP port)
# EXPOSE 8000   # only if you run a web server

# Start your app
CMD ["python", "main.py"]