import os
from typing import List
from sklearn.metrics.pairwise import cosine_similarity
from openai import OpenAI

from .transcript_processor import TranscriptProcessor, TranscriptSegment


class YouTubeAdvisor:
    """Main chatbot class for providing YouTube advice."""
    
    def __init__(self, openai_api_key: str = None):
        # Initialize OpenAI client
        if openai_api_key:
            self.client = OpenAI(api_key=openai_api_key)
        else:
            self.client = OpenAI()  # Will use OPENAI_API_KEY env var
        
        self.processor = TranscriptProcessor()
        self.segments = []
        
        # Load transcripts
        print("🔄 Initializing YouTube Advisor...")
        self.segments = self.processor.load_all_transcripts()
        
        if not self.segments:
            print("❌ No transcript segments loaded!")
        else:
            print(f"✅ Loaded {len(self.segments)} total segments")
    
    def find_relevant_segments(self, question: str, top_k: int = 5) -> List[TranscriptSegment]:
        """Find the most relevant transcript segments for a question."""
        if not self.segments:
            return []
        
        # Create embedding for the question
        question_embedding = self.processor.embedder.encode([question])
        
        # Calculate similarities
        similarities = []
        for segment in self.segments:
            if segment.embedding is not None:
                similarity = cosine_similarity(
                    question_embedding.reshape(1, -1),
                    segment.embedding.reshape(1, -1)
                )[0][0]
                similarities.append((similarity, segment))
        
        # Sort by similarity and return top k
        similarities.sort(key=lambda x: x[0], reverse=True)
        relevant_segments = [seg for _, seg in similarities[:top_k]]
        
        return relevant_segments
    
    def create_context_prompt(self, question: str, relevant_segments: List[TranscriptSegment]) -> str:
        """Create a prompt with context from relevant segments."""
        context = "TRANSCRIPT CONTEXT:\n\n"
        
        for segment in relevant_segments:
            context += f"Video: {segment.video_title}\n"
            context += f"Timestamp: {segment.timestamp}\n"
            context += f"Content: {segment.content}\n\n"
        
        prompt = f"""
You are a YouTube growth advisor. Answer the user's question based ONLY on the provided transcript context.

{context}

USER QUESTION: {question}

INSTRUCTIONS:
1. Provide actionable recommendations based only on the transcript content
2. Include citations for each recommendation using this format: [source: "Video Title" t=HH:MM:SS]
3. If the transcripts don't contain enough information, say so clearly
4. Be specific and practical - avoid generic advice
5. Group related recommendations together

ANSWER:
"""
        
        return prompt
    
    def ask(self, question: str) -> str:
        """Main method to ask a question and get grounded advice."""
        print(f"🤔 Processing question: {question}")
        
        # Find relevant segments
        relevant_segments = self.find_relevant_segments(question)
        
        if not relevant_segments:
            return ("I don't have enough information in the provided transcripts to answer your question. "
                   "Please ask about video introductions or storytelling techniques, which are covered in the available content.")
        
        # Create prompt with context
        prompt = self.create_context_prompt(question, relevant_segments)
        
        try:
            # Get response from OpenAI
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful YouTube growth advisor that provides grounded advice with citations."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=800
            )
            
            answer = response.choices[0].message.content
            print("✅ Generated response with citations")
            return answer
            
        except Exception as e:
            print(f"❌ Error generating response: {e}")
            return f"Sorry, I encountered an error while processing your question: {e}"