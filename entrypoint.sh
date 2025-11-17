#!/bin/bash
set -e

echo "Starting Telegram Bot Backend..."

# Initialize database
echo "Initializing database..."
python init_db.py

# Start the application
echo "Starting Gunicorn..."
exec gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 120 app:app
