#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test personality prompt import
"""

import sys
import os

# Add path to GopiAI-App
sys.path.append(os.path.join(os.path.dirname(__file__), 'GopiAI-App'))

try:
    from gopiai.app.prompt.personality import PERSONALITY_SYSTEM_PROMPT
    print("SUCCESS: Personality prompt imported")
    print("First 200 characters:")
    print(PERSONALITY_SYSTEM_PROMPT[:200] + "...")
except ImportError as e:
    print(f"ERROR importing prompt: {e}")
    print("Checking file existence...")
    
    personality_path = os.path.join(os.path.dirname(__file__), 'GopiAI-App', 'gopiai', 'app', 'prompt', 'personality.py')
    if os.path.exists(personality_path):
        print(f"File found: {personality_path}")
    else:
        print(f"File not found: {personality_path}")
        
    # Check alternative paths
    alt_paths = [
        os.path.join(os.path.dirname(__file__), '..', 'GopiAI-App', 'gopiai', 'app', 'prompt', 'personality.py'),
        os.path.join(os.path.dirname(__file__), '..', '..', 'GopiAI-App', 'gopiai', 'app', 'prompt', 'personality.py'),
    ]
    
    for alt_path in alt_paths:
        if os.path.exists(alt_path):
            print(f"✅ Альтернативный путь найден: {alt_path}")
            break
    else:
        print("❌ Файл personality.py не найден ни по одному из путей")
