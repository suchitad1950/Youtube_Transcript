#!/usr/bin/env python3
"""
Simple diagnostic script to check YouTube Advisor functionality
"""

import os
import sys
from dotenv import load_dotenv

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def check_environment():
    """Check if environment is set up correctly."""
    print("🔍 Checking Environment Setup...")
    
    # Load .env file
    load_dotenv()
    
    # Check API key
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key:
        print(f"✅ API Key found: {api_key[:10]}...{api_key[-4:]}")
    else:
        print("❌ API Key not found!")
        return False
    
    # Check transcript files
    transcript_files = ['transcripts/aprilynne.txt', 'transcripts/hayden.txt']
    for file_path in transcript_files:
        if os.path.exists(file_path):
            print(f"✅ Found: {file_path}")
        else:
            print(f"❌ Missing: {file_path}")
            return False
    
    return True

def test_basic_functionality():
    """Test basic YouTube Advisor functionality."""
    print("\n🧪 Testing Basic Functionality...")
    
    try:
        from src.advisor import YouTubeAdvisor
        print("✅ Successfully imported YouTubeAdvisor")
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False
    
    try:
        print("🔄 Initializing YouTube Advisor...")
        advisor = YouTubeAdvisor()
        print(f"✅ Advisor initialized with {len(advisor.segments)} segments")
    except Exception as e:
        print(f"❌ Initialization error: {e}")
        return False
    
    try:
        print("🔄 Testing simple question...")
        response = advisor.ask("How can I improve my video introductions?")
        print(f"✅ Got response ({len(response)} characters)")
        print(f"📝 Response preview: {response[:100]}...")
        
        # Check for citations
        import re
        citation_pattern = r'\[source: "[^"]+" t=\d{2}:\d{2}:\d{2}\]'
        citations = re.findall(citation_pattern, response)
        print(f"🔗 Citations found: {len(citations)}")
        
        return True
    except Exception as e:
        print(f"❌ Question processing error: {e}")
        return False

def test_out_of_scope():
    """Test out-of-scope question handling."""
    print("\n🚫 Testing Out-of-Scope Handling...")
    
    try:
        from src.advisor import YouTubeAdvisor
        advisor = YouTubeAdvisor()
        
        response = advisor.ask("How do I optimize my YouTube ad spend?")
        print(f"📝 Out-of-scope response: {response[:100]}...")
        
        # Check for fallback indicators
        fallback_indicators = [
            "don't have enough information",
            "not covered",
            "outside the scope",
            "can't answer",
            "not in the transcripts"
        ]
        
        has_fallback = any(indicator in response.lower() for indicator in fallback_indicators)
        if has_fallback:
            print("✅ Proper fallback detected")
        else:
            print("❌ No fallback detected - may be making up answers!")
        
        return has_fallback
    except Exception as e:
        print(f"❌ Out-of-scope test error: {e}")
        return False

def main():
    """Run all diagnostic tests."""
    print("🏥 YouTube Advisor Diagnostic Tool")
    print("=" * 50)
    
    # Test environment
    env_ok = check_environment()
    if not env_ok:
        print("\n❌ Environment setup failed! Fix the issues above first.")
        return
    
    # Test basic functionality
    basic_ok = test_basic_functionality()
    if not basic_ok:
        print("\n❌ Basic functionality failed!")
        return
    
    # Test out-of-scope handling
    scope_ok = test_out_of_scope()
    
    # Summary
    print("\n📊 Diagnostic Summary")
    print("=" * 30)
    print(f"Environment Setup: {'✅ PASS' if env_ok else '❌ FAIL'}")
    print(f"Basic Functionality: {'✅ PASS' if basic_ok else '❌ FAIL'}")
    print(f"Out-of-Scope Handling: {'✅ PASS' if scope_ok else '❌ FAIL'}")
    
    if env_ok and basic_ok and scope_ok:
        print("\n🎉 All tests passed! Your YouTube Advisor should work correctly.")
    else:
        print("\n⚠️ Some issues detected. Check the specific errors above.")

if __name__ == "__main__":
    main()