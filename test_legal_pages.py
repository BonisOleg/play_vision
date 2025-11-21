#!/usr/bin/env python
"""
Test script to verify legal pages are working
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, '/Users/olegbonislavskyi/Play_Vision')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'playvision.settings')
django.setup()

from django.test import Client
from django.urls import reverse

def test_legal_pages():
    client = Client()
    pages = ['privacy', 'terms', 'copyright']
    
    print("Testing legal pages...")
    for slug in pages:
        url = reverse('core:legal', kwargs={'slug': slug})
        print(f"\nTesting: {url}")
        
        try:
            response = client.get(url)
            if response.status_code == 200:
                print(f"  ✓ {slug}: OK (200)")
            else:
                print(f"  ✗ {slug}: {response.status_code}")
        except Exception as e:
            print(f"  ✗ {slug}: Error - {e}")
    
    print("\n" + "="*50)
    print("All tests completed!")

if __name__ == '__main__':
    test_legal_pages()

