# Design Document: YouTube Advisor Chatbot

## Architecture Overview

The YouTube Advisor follows a simple but effective RAG (Retrieval-Augmented Generation) architecture:

```
User Question → Semantic Search → Context Retrieval → LLM Generation → Cited Response
```

### Core Components

1. **TranscriptProcessor**
   - Parses timestamp-based transcript files
   - Creates semantic embeddings for each segment
   - Handles multiple video sources

2. **YouTubeAdvisor**
   - Main chatbot interface
   - Performs semantic search over transcript segments
   - Generates grounded responses with citations

3. **Data Structures**
   - `TranscriptSegment`: Represents timestamped content
   - `Citation`: Formats source references

## Key Design Decisions

### 1. Embedding-Based Search
**Choice**: SentenceTransformers 'all-MiniLM-L6-v2'
**Rationale**: 
- Fast, lightweight model suitable for beginners
- Good performance on semantic similarity tasks
- Runs locally without additional API costs

**Tradeoffs**:
- ✅ Fast inference and low memory usage
- ✅ No additional API costs
- ❌ Less sophisticated than larger models
- ❌ Limited context understanding

### 2. OpenAI GPT-3.5-turbo for Generation
**Choice**: GPT-3.5-turbo with temperature=0.3
**Rationale**:
- Reliable, well-documented API
- Good balance of cost and performance
- Strong instruction following for citation format

**Tradeoffs**:
- ✅ High-quality responses
- ✅ Reliable citation formatting
- ❌ Requires API key and internet
- ❌ Ongoing costs per request

### 3. Timestamp-Based Citations
**Choice**: Format `[source: "Video Title" t=HH:MM:SS]`
**Rationale**:
- Machine-readable format
- Includes both source identification and temporal reference
- Easy to validate with regex

### 4. CLI Interface
**Choice**: Simple command-line interface with argparse
**Rationale**:
- Beginner-friendly and familiar
- Easy to test and automate
- Minimal dependencies

**Tradeoffs**:
- ✅ Easy to understand and use
- ✅ Scriptable and testable
- ❌ Not as user-friendly as web interface
- ❌ Limited visual capabilities

## Error Handling Strategy

1. **API Failures**: Graceful degradation with informative error messages
2. **Missing Transcripts**: Clear file path validation and user guidance
3. **Out-of-Scope Questions**: Semantic similarity threshold to detect coverage
4. **Malformed Input**: Input validation and sanitization

## Performance Considerations

### Semantic Search
- **Time Complexity**: O(n) where n = number of transcript segments
- **Space Complexity**: O(n×d) where d = embedding dimension (384)
- **Optimization**: Could implement approximate nearest neighbors for larger datasets

### LLM Generation
- **Latency**: 2-5 seconds per request
- **Cost**: ~$0.01-0.02 per question
- **Optimization**: Could implement response caching for common questions

## Scalability Considerations

### Current Limitations
- In-memory storage of all embeddings
- Sequential processing of transcript files
- No caching or persistence layer

### Future Scaling Options
1. **Vector Database**: Pinecone, Weaviate, or ChromaDB for large-scale search
2. **Caching Layer**: Redis for response caching
3. **Async Processing**: For handling multiple concurrent requests
4. **Batch Processing**: For preprocessing large transcript collections

## Testing Strategy

### Automated Tests
1. **Schema Validation**: Citation format compliance
2. **Grounding Verification**: Correct source attribution
3. **Fallback Behavior**: Out-of-scope question handling

### Manual Testing
1. **Quality Assessment**: Human evaluation of response relevance
2. **Edge Cases**: Ambiguous questions, multiple valid answers
3. **User Experience**: Interface usability and error messages

## Security & Privacy

### Current Measures
- Environment variable management for API keys
- No persistent storage of user questions
- Local processing of transcript embeddings

### Production Considerations
- Rate limiting for API usage
- Input sanitization for web deployment
- User session management
- Audit logging

## Alternative Approaches Considered

### 1. Local LLM (e.g., Ollama, Llama.cpp)
**Pros**: No API costs, full privacy, offline operation
**Cons**: Larger resource requirements, more complex setup
**Decision**: Chose OpenAI for simplicity and reliability

### 2. Traditional Keyword Search
**Pros**: Simple implementation, fast execution
**Cons**: Poor semantic understanding, brittle matching
**Decision**: Chose semantic search for better relevance

### 3. Fine-tuned Model
**Pros**: Potentially better domain-specific performance
**Cons**: Requires training data, more complex deployment
**Decision**: Chose general model with RAG for flexibility

## Conclusion

This design prioritizes:
1. **Simplicity**: Easy to understand and modify
2. **Reliability**: Proven components and clear error handling
3. **Demonstrability**: Clear citations and testable behavior
4. **Extensibility**: Modular design allows for future improvements

The architecture successfully meets all core requirements while remaining accessible to beginners.