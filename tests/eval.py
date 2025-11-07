#!/usr/bin/env python3
"""
Evaluation Harness for YouTube Advisor

This script runs a series of predefined test questions to evaluate
the chatbot's performance on various scenarios.
"""

import os
import sys
import re
from typing import List, Dict, Any
from dotenv import load_dotenv

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.advisor import YouTubeAdvisor


class EvaluationHarness:
    """Evaluation harness for testing the YouTube Advisor with predefined questions."""
    
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
    
    def run_evaluation(self, advisor: YouTubeAdvisor) -> List[Dict[str, Any]]:
        """Run the complete evaluation suite."""
        print("🔄 Running evaluation harness...\n")
        
        for i, question_data in enumerate(self.test_questions, 1):
            print(f"Test {i}/{len(self.test_questions)}: {question_data['category']}")
            print(f"Q: {question_data['question']}")
            
            # Get response from advisor
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
        
        return self.results
    
    def print_summary(self):
        """Print a summary of the evaluation results."""
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
    """Main entry point for the evaluation harness."""
    print("🧪 YouTube Advisor Evaluation Harness")
    print("=" * 50)
    
    # Load environment variables from .env file
    load_dotenv()
    
    # Check for API key
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ Error: OPENAI_API_KEY environment variable not set!")
        print("Please create a .env file in the project root with:")
        print("OPENAI_API_KEY=your-api-key-here")
        print("\nOr set the environment variable directly:")
        print("export OPENAI_API_KEY=your-api-key-here")
        sys.exit(1)
    
    try:
        # Initialize advisor
        print("🚀 Initializing YouTube Advisor...")
        advisor = YouTubeAdvisor()
        
        # Run evaluation
        harness = EvaluationHarness()
        results = harness.run_evaluation(advisor)
        
        # Print summary
        harness.print_summary()
        
        # Overall result
        average_score = sum(r.get('score', 0) for r in results) / len(results)
        if average_score >= 0.8:
            print("\n🎉 Evaluation PASSED! The system is performing well.")
        elif average_score >= 0.6:
            print("\n⚠️ Evaluation PARTIAL. Some improvements needed.")
        else:
            print("\n❌ Evaluation FAILED. Significant issues detected.")
        
    except Exception as e:
        print(f"❌ Evaluation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()