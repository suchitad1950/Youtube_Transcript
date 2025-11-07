#!/usr/bin/env python3
"""
Quick evaluation test to identify the specific issues
"""

import os
import sys
import re
from dotenv import load_dotenv

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.advisor import YouTubeAdvisor

def main():
    load_dotenv()
    
    print("🔬 Quick Evaluation Test")
    print("=" * 40)
    
    advisor = YouTubeAdvisor()
    
    # Test 1: Basic question
    print("\n1. Testing video introductions question:")
    response1 = advisor.ask("How can I improve my video introductions?")
    print(f"Response length: {len(response1)} chars")
    print(f"First 100 chars: {response1[:100]}...")
    
    # Check citations
    citations = re.findall(r'\[source: "[^"]+" t=\d{2}:\d{2}:\d{2}\]', response1)
    print(f"Citations found: {len(citations)}")
    
    # Check topics
    intro_topics = ["intro", "retention", "hook"]
    found_topics = [topic for topic in intro_topics if topic.lower() in response1.lower()]
    print(f"Topics found: {found_topics}")
    
    # Test 2: Out-of-scope question
    print("\n2. Testing out-of-scope question:")
    response2 = advisor.ask("How do I optimize my YouTube ad spend?")
    print(f"Response: {response2}")
    
    # Check fallback
    fallback_phrases = ["don't have enough information", "not covered", "outside the scope", "can't answer", "not in the transcripts"]
    has_fallback = any(phrase in response2.lower() for phrase in fallback_phrases)
    print(f"Fallback detected: {has_fallback}")
    
    print("\n" + "="*40)

if __name__ == "__main__":
    main()