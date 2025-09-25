#!/usr/bin/env bash
# Simplified build script for Render deployment
# Use this if main build.sh fails

set -o errexit

echo "Step 1: Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Step 2: Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "Step 3: Running migrations..."
python manage.py migrate

echo "Step 4: Creating initial data..."
python manage.py setup_initial_data || echo "Initial data setup failed, continuing..."

echo "Step 5: Loading AI knowledge base..."
python manage.py load_knowledge_base || echo "AI knowledge base loading failed, continuing..."

echo "Build completed successfully!"
