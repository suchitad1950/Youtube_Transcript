import os
import re
import numpy as np
from typing import List, Optional
from dataclasses import dataclass
from sentence_transformers import SentenceTransformer


@dataclass
class TranscriptSegment:
    """Represents a segment of transcript with timestamp and content."""
    video_id: str
    video_title: str
    timestamp: str
    content: str
    embedding: Optional[np.ndarray] = None
    
    def __str__(self):
        return f"[{self.video_id} t={self.timestamp}] {self.content[:100]}..."


class TranscriptProcessor:
    """Processes transcript files and creates searchable segments."""
    
    def __init__(self):
        self.segments: List[TranscriptSegment] = []
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Video metadata
        self.video_metadata = {
            'aprilynne': 'Improving Video Introductions',
            'hayden': 'YouTube Storytelling Techniques'
        }
    
    def parse_timestamp(self, timestamp_str: str) -> str:
        """Parse timestamp string and return in standard format."""
        timestamp = timestamp_str.strip()
        if re.match(r'\d{2}:\d{2}:\d{2}', timestamp):
            return timestamp
        return "00:00:00"  # fallback
    
    def load_transcript(self, file_path: str, video_id: str) -> List[TranscriptSegment]:
        """Load a transcript file and return segments."""
        segments = []
        video_title = self.video_metadata.get(video_id, video_id)
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Split into lines and process
            lines = content.strip().split('\n')
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Extract timestamp and content
                timestamp_match = re.match(r'(\d{2}:\d{2}:\d{2})\s+(.+)', line)
                if timestamp_match:
                    timestamp = timestamp_match.group(1)
                    content = timestamp_match.group(2)
                    
                    segment = TranscriptSegment(
                        video_id=video_id,
                        video_title=video_title,
                        timestamp=timestamp,
                        content=content
                    )
                    segments.append(segment)
            
            print(f"✅ Loaded {len(segments)} segments from {video_id}")
            return segments
            
        except Exception as e:
            print(f"❌ Error loading {file_path}: {e}")
            return []
    
    def create_embeddings(self, segments: List[TranscriptSegment]):
        """Create embeddings for all segments."""
        print("🔄 Creating embeddings...")
        contents = [seg.content for seg in segments]
        embeddings = self.embedder.encode(contents)
        
        for i, segment in enumerate(segments):
            segment.embedding = embeddings[i]
        
        print(f"✅ Created embeddings for {len(segments)} segments")
    
    def load_all_transcripts(self, transcript_dir: str = "transcripts") -> List[TranscriptSegment]:
        """Load all transcript files and create embeddings."""
        all_segments = []
        
        # Load both transcript files
        transcript_files = [
            (os.path.join(transcript_dir, 'aprilynne.txt'), 'aprilynne'),
            (os.path.join(transcript_dir, 'hayden.txt'), 'hayden')
        ]
        
        for file_path, video_id in transcript_files:
            if os.path.exists(file_path):
                segments = self.load_transcript(file_path, video_id)
                all_segments.extend(segments)
            else:
                print(f"⚠️ File not found: {file_path}")
        
        if all_segments:
            self.create_embeddings(all_segments)
            self.segments = all_segments
        
        return all_segments