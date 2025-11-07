#!/usr/bin/env python3
"""
Unified YouTube Advisor Test Suite

A comprehensive testing framework that combines basic diagnostics, 
detailed analysis, and full evaluation into a single tool.

Usage:
    python tests/test_suite.py --mode basic        # Quick health check
    python tests/test_suite.py --mode detailed     # In-depth analysis  
    python tests/test_suite.py --mode evaluation   # Full evaluation
    python tests/test_suite.py --mode all          # Run all modes
"""

import os
import sys
import re
import argparse
from typing import List, Dict, Any
from dotenv import load_dotenv

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.advisor import YouTubeAdvisor


class YouTubeAdvisorTestSuite:
    """Unified test suite for YouTube Advisor with multiple testing modes."""
    
    def __init__(self):
        self.test_questions = [
            {
                "question": "How can I improve my video introductions to get better retention?",
                "expected_topics": ["intro", "retention", "hook"],
                "expected_video": "aprilynne",
                "category": "video_introductions"
            },
            {
                "question": "What are the best practices for creating effective thumbnails?",
                "expected_topics": ["thumbnail", "contrast", "focal point"],
                "expected_video": "aprilynne",
                "category": "thumbnails"
            },
            {
                "question": "How should I structure my YouTube videos for better storytelling?",
                "expected_topics": ["structure", "act", "story"],
                "expected_video": "hayden",
                "category": "storytelling"
            },
            {
                "question": "How do I keep viewers engaged throughout my videos?",
                "expected_topics": ["engagement", "retention", "cliffhanger"],
                "expected_video": "hayden",
                "category": "retention"
            },
            {
                "question": "What pacing should I use for my target audience?",
                "expected_topics": ["pacing", "audience"],
                "expected_video": "hayden",
                "category": "pacing"
            },
            {
                "question": "How do I optimize my YouTube ad spend for better ROI?",
                "expected_topics": [],  # Should trigger fallback
                "expected_video": None,
                "category": "out_of_scope"
            }
        ]
        self.results = []
    
    def check_environment(self) -> bool:
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
    
    def test_basic_functionality(self, advisor: YouTubeAdvisor) -> bool:
        """Test basic YouTube Advisor functionality."""
        print("\n🧪 Testing Basic Functionality...")
        
        try:
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
            citation_pattern = r'\[source: "[^"]+" t=\d{2}:\d{2}:\d{2}\]'
            citations = re.findall(citation_pattern, response)
            print(f"🔗 Citations found: {len(citations)}")
            
            return True
        except Exception as e:
            print(f"❌ Question processing error: {e}")
            return False
    
    def test_out_of_scope_handling(self, advisor: YouTubeAdvisor) -> bool:
        """Test out-of-scope question handling."""
        print("\n🚫 Testing Out-of-Scope Handling...")
        
        try:
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
    
    def check_citation_format(self, response: str) -> Dict[str, Any]:
        """Check if the response has properly formatted citations."""
        citation_pattern = r'\[source: "[^"]+" t=\d{2}:\d{2}:\d{2}\]'
        citations = re.findall(citation_pattern, response)
        
        return {
            "has_citations": len(citations) > 0,
            "citation_count": len(citations),
            "citations": citations
        }
    
    def check_grounding(self, response: str, expected_video: str, expected_topics: List[str]) -> Dict[str, Any]:
        """Check if the response is properly grounded in the expected content."""
        response_lower = response.lower()
        
        # Check if expected video is referenced
        video_referenced = expected_video and expected_video in response_lower
        
        # Check if expected topics are covered
        topics_covered = []
        for topic in expected_topics:
            if topic.lower() in response_lower:
                topics_covered.append(topic)
        
        return {
            "video_referenced": video_referenced,
            "topics_covered": topics_covered,
            "topic_coverage_ratio": len(topics_covered) / len(expected_topics) if expected_topics else 0
        }
    
    def check_fallback(self, response: str) -> bool:
        """Check if the response properly handles out-of-scope questions."""
        fallback_indicators = [
            "don't have enough information",
            "not covered",
            "outside the scope",
            "can't answer",
            "not in the transcripts"
        ]
        
        return any(indicator in response.lower() for indicator in fallback_indicators)
    
    def evaluate_response(self, question_data: Dict[str, Any], response: str) -> Dict[str, Any]:
        """Evaluate a single response against expected criteria."""
        result = {
            "question": question_data["question"],
            "category": question_data["category"],
            "response": response,
            "response_length": len(response)
        }
        
        # Check citation format
        citation_check = self.check_citation_format(response)
        result.update(citation_check)
        
        # Check grounding (unless out of scope)
        if question_data["category"] != "out_of_scope":
            grounding_check = self.check_grounding(
                response, 
                question_data["expected_video"], 
                question_data["expected_topics"]
            )
            result.update(grounding_check)
            
            # Score the response
            citation_score = 1 if citation_check["has_citations"] else 0
            grounding_score = grounding_check["topic_coverage_ratio"]
            video_score = 1 if grounding_check["video_referenced"] else 0
            
            result["score"] = (citation_score + grounding_score + video_score) / 3
        else:
            # For out-of-scope questions, check fallback behavior
            fallback_handled = self.check_fallback(response)
            result["fallback_handled"] = fallback_handled
            result["score"] = 1 if fallback_handled else 0
        
        return result
    
    def run_basic_mode(self) -> bool:
        """Run basic diagnostic tests."""
        print("🏥 YouTube Advisor - Basic Diagnostic Mode")
        print("=" * 50)
        
        # Test environment
        env_ok = self.check_environment()
        if not env_ok:
            print("\n❌ Environment setup failed! Fix the issues above first.")
            return False
        
        # Initialize advisor
        try:
            print("\n🚀 Initializing YouTube Advisor...")
            advisor = YouTubeAdvisor()
        except Exception as e:
            print(f"❌ Failed to initialize advisor: {e}")
            return False
        
        # Test basic functionality
        basic_ok = self.test_basic_functionality(advisor)
        if not basic_ok:
            print("\n❌ Basic functionality failed!")
            return False
        
        # Test out-of-scope handling
        scope_ok = self.test_out_of_scope_handling(advisor)
        
        # Summary
        print("\n📊 Basic Diagnostic Summary")
        print("=" * 30)
        print(f"Environment Setup: {'✅ PASS' if env_ok else '❌ FAIL'}")
        print(f"Basic Functionality: {'✅ PASS' if basic_ok else '❌ FAIL'}")
        print(f"Out-of-Scope Handling: {'✅ PASS' if scope_ok else '❌ FAIL'}")
        
        if env_ok and basic_ok and scope_ok:
            print("\n🎉 All basic tests passed! Your YouTube Advisor should work correctly.")
            return True
        else:
            print("\n⚠️ Some issues detected. Check the specific errors above.")
            return False
    
    def run_detailed_mode(self) -> bool:
        """Run detailed individual test analysis."""
        print("🔍 YouTube Advisor - Detailed Analysis Mode")
        print("=" * 50)
        
        # Load environment and initialize
        load_dotenv()
        
        try:
            print("🚀 Initializing advisor...")
            advisor = YouTubeAdvisor()
            print(f"✅ Loaded {len(advisor.segments)} segments\n")
        except Exception as e:
            print(f"❌ Failed to initialize advisor: {e}")
            return False
        
        # Test sample cases for detailed analysis
        sample_cases = self.test_questions[:3]  # First 3 test cases
        
        for i, test_case in enumerate(sample_cases, 1):
            print(f"Detailed Test {i}: {test_case['category']}")
            print(f"Q: {test_case['question']}")
            
            try:
                response = advisor.ask(test_case['question'])
                print(f"✅ Got response ({len(response)} chars)")
                print(f"📝 Response: {response[:200]}...")
                
                # Check citations
                citation_check = self.check_citation_format(response)
                print(f"🔗 Citations found: {citation_check['citation_count']}")
                if citation_check['citations']:
                    print(f"   Example: {citation_check['citations'][0]}")
                
                # Check topics
                if test_case['expected_topics']:
                    grounding_check = self.check_grounding(
                        response, test_case['expected_video'], test_case['expected_topics']
                    )
                    print(f"📋 Topics covered: {grounding_check['topics_covered']} / {test_case['expected_topics']}")
                    print(f"🎥 Video referenced: {grounding_check['video_referenced']}")
                
                # Check fallback for out-of-scope
                if test_case['category'] == "out_of_scope":
                    has_fallback = self.check_fallback(response)
                    print(f"🚫 Fallback detected: {has_fallback}")
                
            except Exception as e:
                print(f"❌ Error: {e}")
            
            print("-" * 60)
        
        return True
    
    def run_evaluation_mode(self) -> bool:
        """Run full evaluation suite."""
        print("🧪 YouTube Advisor - Full Evaluation Mode")
        print("=" * 50)
        
        # Load environment and initialize
        load_dotenv()
        
        # Check for API key
        if not os.getenv('OPENAI_API_KEY'):
            print("❌ Error: OPENAI_API_KEY environment variable not set!")
            return False
        
        try:
            print("🚀 Initializing YouTube Advisor...")
            advisor = YouTubeAdvisor()
        except Exception as e:
            print(f"❌ Failed to initialize advisor: {e}")
            return False
        
        # Run evaluation
        print("\n🔄 Running evaluation harness...\n")
        
        for i, question_data in enumerate(self.test_questions, 1):
            print(f"Test {i}/{len(self.test_questions)}: {question_data['category']}")
            print(f"Q: {question_data['question']}")
            
            try:
                response = advisor.ask(question_data["question"])
                result = self.evaluate_response(question_data, response)
                self.results.append(result)
                
                print(f"Score: {result['score']:.2f}")
                print(f"Citations: {result['citation_count']}")
                print("-" * 80)
                
            except Exception as e:
                print(f"❌ Error: {e}")
                result = {
                    "question": question_data["question"],
                    "category": question_data["category"],
                    "error": str(e),
                    "score": 0
                }
                self.results.append(result)
                print("-" * 80)
        
        # Print summary
        self.print_evaluation_summary()
        
        # Determine pass/fail
        average_score = sum(r.get('score', 0) for r in self.results) / len(self.results)
        if average_score >= 0.8:
            print("\n🎉 Evaluation PASSED! The system is performing well.")
            return True
        elif average_score >= 0.6:
            print("\n⚠️ Evaluation PARTIAL. Some improvements needed.")
            return False
        else:
            print("\n❌ Evaluation FAILED. Significant issues detected.")
            return False
    
    def print_evaluation_summary(self):
        """Print detailed evaluation summary."""
        if not self.results:
            print("No results to summarize.")
            return
        
        print("\n📊 Evaluation Summary")
        print("=" * 50)
        
        # Overall statistics
        total_tests = len(self.results)
        successful_tests = sum(1 for r in self.results if r.get('score', 0) > 0)
        average_score = sum(r.get('score', 0) for r in self.results) / total_tests
        
        print(f"Total tests: {total_tests}")
        print(f"Successful tests: {successful_tests}")
        print(f"Success rate: {successful_tests/total_tests:.1%}")
        print(f"Average score: {average_score:.2f}")
        
        # Category breakdown
        print(f"\n📋 Results by Category:")
        categories = {}
        for result in self.results:
            cat = result["category"]
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(result)
        
        for category, results in categories.items():
            avg_score = sum(r.get('score', 0) for r in results) / len(results)
            print(f"  {category}: {avg_score:.2f} ({len(results)} tests)")
        
        # Citation analysis
        citation_counts = [r.get('citation_count', 0) for r in self.results if 'citation_count' in r]
        if citation_counts:
            avg_citations = sum(citation_counts) / len(citation_counts)
            print(f"\n📝 Citation Analysis:")
            print(f"  Average citations per response: {avg_citations:.1f}")
            print(f"  Responses with citations: {sum(1 for c in citation_counts if c > 0)}/{len(citation_counts)}")


def main():
    """Main entry point with command-line argument parsing."""
    parser = argparse.ArgumentParser(
        description="YouTube Advisor Unified Test Suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Test Modes:
  basic      - Quick environment and functionality check
  detailed   - In-depth analysis of individual test cases  
  evaluation - Full evaluation with scoring and pass/fail
  all        - Run all modes sequentially

Examples:
  python tests/test_suite.py --mode basic
  python tests/test_suite.py --mode evaluation
  python tests/test_suite.py --mode all
        """
    )
    
    parser.add_argument(
        '--mode', 
        choices=['basic', 'detailed', 'evaluation', 'all'],
        default='basic',
        help='Test mode to run (default: basic)'
    )
    
    args = parser.parse_args()
    
    # Initialize test suite
    test_suite = YouTubeAdvisorTestSuite()
    
    # Run requested mode(s)
    success = True
    
    if args.mode == 'all':
        print("🚀 Running All Test Modes\n")
        success &= test_suite.run_basic_mode()
        print("\n" + "="*80 + "\n")
        success &= test_suite.run_detailed_mode()
        print("\n" + "="*80 + "\n")
        success &= test_suite.run_evaluation_mode()
    elif args.mode == 'basic':
        success = test_suite.run_basic_mode()
    elif args.mode == 'detailed':
        success = test_suite.run_detailed_mode()
    elif args.mode == 'evaluation':
        success = test_suite.run_evaluation_mode()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()