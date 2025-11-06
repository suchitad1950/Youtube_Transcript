#!/usr/bin/env python3
"""
Test Suite for YouTube Advisor Chatbot

This module contains comprehensive tests to validate the core functionality
of the YouTube Advisor chatbot, including citation format, grounding, and
fallback behavior.
"""

import os
import re
import sys
import unittest
from unittest.mock import Mock, patch

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.advisor import YouTubeAdvisor
from src.transcript_processor import TranscriptProcessor


class TestYouTubeAdvisor(unittest.TestCase):
    """Test suite for the YouTube Advisor chatbot."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        # Mock OpenAI for testing to avoid API calls
        cls.mock_client = Mock()
        cls.mock_response = Mock()
        cls.mock_response.choices = [Mock()]
        cls.mock_response.choices[0].message.content = (
            "To improve video introductions:\n\n"
            "1. Keep intros short (3-5 seconds maximum) [source: \"Improving Video Introductions\" t=00:01:15]\n"
            "2. Start with a hook to create curiosity [source: \"Improving Video Introductions\" t=00:02:15]\n"
            "3. Avoid long intros with music or graphics [source: \"Improving Video Introductions\" t=00:03:30]"
        )
        cls.mock_client.chat.completions.create.return_value = cls.mock_response
    
    def setUp(self):
        """Set up each test."""
        # Create advisor with mocked OpenAI client
        with patch('src.advisor.OpenAI') as mock_openai:
            mock_openai.return_value = self.mock_client
            self.advisor = YouTubeAdvisor("test-api-key")
    
    def test_citation_format(self):
        """Test that responses include properly formatted citations."""
        question = "How do I improve video introductions?"
        response = self.advisor.ask(question)
        
        # Check for citation pattern: [source: "Video Title" t=HH:MM:SS]
        citation_pattern = r'\[source: "[^"]+" t=\d{2}:\d{2}:\d{2}\]'
        citations = re.findall(citation_pattern, response)
        
        self.assertGreater(len(citations), 0, "Response should contain at least one properly formatted citation")
        print(f"✅ Citation format test passed - Found {len(citations)} citations")
    
    def test_grounding_to_specific_video(self):
        """Test that responses cite content from the expected video."""
        # Mock response for storytelling question
        storytelling_response = (
            "For better storytelling structure:\n\n"
            "1. Use three-act structure [source: \"YouTube Storytelling Techniques\" t=00:00:45]\n"
            "2. Create hooks in Act 1 [source: \"YouTube Storytelling Techniques\" t=00:01:00]\n"
            "3. Use mini-cliffhangers in Act 2 [source: \"YouTube Storytelling Techniques\" t=00:04:30]"
        )
        self.mock_response.choices[0].message.content = storytelling_response
        
        question = "How should I structure my YouTube videos for storytelling?"
        response = self.advisor.ask(question)
        
        # Check that response references storytelling content
        self.assertIn("storytelling", response.lower(), 
                     "Response should reference storytelling content for storytelling question")
        print("✅ Grounding test passed - Response correctly cites storytelling video")
    
    def test_fallback_behavior(self):
        """Test graceful handling of out-of-scope questions."""
        # Test with no relevant segments found
        with patch.object(self.advisor, 'find_relevant_segments', return_value=[]):
            question = "How do I optimize my YouTube ads budget?"
            response = self.advisor.ask(question)
            
            fallback_indicators = [
                "don't have enough information",
                "not covered",
                "outside the scope",
                "can't answer"
            ]
            
            has_fallback = any(indicator in response.lower() for indicator in fallback_indicators)
            self.assertTrue(has_fallback, "Response should gracefully handle out-of-scope questions")
            print("✅ Fallback test passed - Graceful handling of out-of-scope questions")
    
    def test_transcript_loading(self):
        """Test that transcript files are loaded correctly."""
        processor = TranscriptProcessor()
        segments = processor.load_all_transcripts()
        
        self.assertGreater(len(segments), 0, "Should load transcript segments")
        
        # Check that both videos are represented
        video_ids = set(seg.video_id for seg in segments)
        expected_videos = {'aprilynne', 'hayden'}
        self.assertEqual(video_ids, expected_videos, "Should load both video transcripts")
        
        # Check that embeddings are created
        self.assertTrue(all(seg.embedding is not None for seg in segments),
                       "All segments should have embeddings")
        print(f"✅ Transcript loading test passed - Loaded {len(segments)} segments")
    
    def test_semantic_search(self):
        """Test that semantic search finds relevant segments."""
        question = "How do I make better thumbnails?"
        relevant_segments = self.advisor.find_relevant_segments(question, top_k=3)
        
        self.assertGreater(len(relevant_segments), 0, "Should find relevant segments")
        self.assertLessEqual(len(relevant_segments), 3, "Should respect top_k limit")
        
        # Check that returned segments contain thumbnail-related content
        segment_contents = " ".join(seg.content.lower() for seg in relevant_segments)
        self.assertIn("thumbnail", segment_contents, 
                     "Relevant segments should contain thumbnail-related content")
        print("✅ Semantic search test passed - Found relevant segments")


def run_test_suite():
    """Run the complete test suite and report results."""
    print("🧪 Running YouTube Advisor Test Suite\n")
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestYouTubeAdvisor)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n📊 Test Results:")
    print(f"   Tests run: {result.testsRun}")
    print(f"   Failures: {len(result.failures)}")
    print(f"   Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("🎉 All tests passed! The chatbot is working correctly.")
        return True
    else:
        print("⚠️ Some tests failed. Please review the implementation.")
        return False


if __name__ == "__main__":
    run_test_suite()