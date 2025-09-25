#!/usr/bin/env bash
# Build script for Render deployment

set -o errexit

echo "🔧 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "📦 Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "🗄️ Running migrations..."
python manage.py migrate

echo "🤖 Loading AI knowledge base..."
python manage.py load_knowledge_base || echo "⚠️ AI knowledge base loading failed, continuing..."

echo "👤 Creating initial data..."
python manage.py setup_initial_data || echo "⚠️ Initial data setup failed, continuing..."

echo "🎉 Build completed successfully!"
