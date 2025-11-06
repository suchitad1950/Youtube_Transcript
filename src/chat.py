#!/usr/bin/env python3
"""
YouTube Advisor CLI Interface

A command-line interface for the YouTube Advisor chatbot.
Provides both single-question and interactive modes.
"""

import argparse
import os
import sys
from dotenv import load_dotenv

# Add the src directory to the path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.advisor import YouTubeAdvisor


def setup_environment():
    """Load environment variables and validate API key."""
    load_dotenv()
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ Error: OPENAI_API_KEY not found!")
        print("Please create a .env file in the project root with:")
        print("OPENAI_API_KEY=your-api-key-here")
        print("\nOr set the environment variable directly:")
        print("export OPENAI_API_KEY=your-api-key-here")
        sys.exit(1)
    
    return api_key


def ask_single_question(advisor, question):
    """Ask a single question and print the response."""
    print(f"❓ Question: {question}\n")
    
    answer = advisor.ask(question)
    print(f"🤖 Answer:\n{answer}\n")


def interactive_mode(advisor):
    """Run in interactive mode where users can ask multiple questions."""
    print("💬 YouTube Advisor - Interactive Mode")
    print("📋 I can help with: video introductions, thumbnails, storytelling, and retention")
    print("❌ Type 'quit', 'exit', or 'stop' to exit\n")
    
    while True:
        try:
            question = input("❓ Your question: ").strip()
            
            if question.lower() in ['quit', 'exit', 'stop']:
                print("👋 Thanks for using YouTube Advisor!")
                break
            
            if not question:
                print("Please enter a question.")
                continue
            
            print(f"\n🤖 Thinking...")
            answer = advisor.ask(question)
            print(f"\n💡 Answer:\n{answer}\n")
            print("-" * 80)
            
        except KeyboardInterrupt:
            print("\n👋 Thanks for using YouTube Advisor!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


def main():
    """Main entry point for the CLI application."""
    parser = argparse.ArgumentParser(
        description="YouTube Advisor - Get grounded advice for YouTube creators",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python src/chat.py --q "How can I improve my video introductions?"
  python src/chat.py  # Interactive mode
        """
    )
    
    parser.add_argument(
        '--q', '--question',
        type=str,
        help='Ask a single question and exit'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='YouTube Advisor 1.0.0'
    )
    
    args = parser.parse_args()
    
    # Setup environment and API key
    try:
        api_key = setup_environment()
    except Exception as e:
        print(f"❌ Setup error: {e}")
        sys.exit(1)
    
    # Initialize the advisor
    try:
        print("🚀 Starting YouTube Advisor...")
        advisor = YouTubeAdvisor(api_key)
        print()
    except Exception as e:
        print(f"❌ Failed to initialize advisor: {e}")
        print("Please check your API key and internet connection.")
        sys.exit(1)
    
    # Run in single question or interactive mode
    if args.q:
        ask_single_question(advisor, args.q)
    else:
        interactive_mode(advisor)


if __name__ == "__main__":
    main()