#!/usr/bin/env python3
"""
Detailed evaluation diagnostic - runs each test individually to identify specific issues
"""

import os
import sys
import re
from dotenv import load_dotenv

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.advisor import YouTubeAdvisor

def test_individual_cases():
    """Test each evaluation case individually."""
    print("🔍 Detailed Individual Test Analysis")
    print("=" * 50)
    
    # Load environment
    load_dotenv()
    
    # Initialize advisor
    print("🚀 Initializing advisor...")
    advisor = YouTubeAdvisor()
    print(f"✅ Loaded {len(advisor.segments)} segments\n")
    
    # Test cases from eval.py
    test_cases = [
        {
            "name": "Video Introductions",
            "question": "How can I improve my video introductions to get better retention?",
            "expected_topics": ["intro", "retention", "hook"],
            "expected_video": "aprilynne"
        },
        {
            "name": "Thumbnails", 
            "question": "What are the best practices for creating effective thumbnails?",
            "expected_topics": ["thumbnail", "contrast", "focal point"],
            "expected_video": "aprilynne"
        },
        {
            "name": "Out-of-Scope",
            "question": "How do I optimize my YouTube ad spend for better ROI?",
            "expected_topics": [],
            "expected_video": None
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"Test {i}: {test_case['name']}")
        print(f"Q: {test_case['question']}")
        
        try:
            response = advisor.ask(test_case['question'])
            print(f"✅ Got response ({len(response)} chars)")
            print(f"📝 Response: {response[:200]}...")
            
            # Check citations
            citation_pattern = r'\[source: "[^"]+" t=\d{2}:\d{2}:\d{2}\]'
            citations = re.findall(citation_pattern, response)
            print(f"🔗 Citations found: {len(citations)}")
            if citations:
                print(f"   Example: {citations[0]}")
            
            # Check topics
            response_lower = response.lower()
            topics_found = []
            for topic in test_case['expected_topics']:
                if topic.lower() in response_lower:
                    topics_found.append(topic)
            print(f"📋 Topics covered: {topics_found} / {test_case['expected_topics']}")
            
            # Check video reference
            if test_case['expected_video']:
                video_mentioned = test_case['expected_video'] in response_lower
                print(f"🎥 Video referenced: {video_mentioned}")
            
            # Check fallback for out-of-scope
            if test_case['name'] == "Out-of-Scope":
                fallback_phrases = [
                    "don't have enough information",
                    "not covered", 
                    "outside the scope",
                    "can't answer",
                    "not in the transcripts"
                ]
                has_fallback = any(phrase in response_lower for phrase in fallback_phrases)
                print(f"🚫 Fallback detected: {has_fallback}")
                if has_fallback:
                    found_phrase = next(phrase for phrase in fallback_phrases if phrase in response_lower)
                    print(f"   Found phrase: '{found_phrase}'")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("-" * 60)

if __name__ == "__main__":
    test_individual_cases()