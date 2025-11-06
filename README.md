# YouTube Advisor Chatbot

A beginner-friendly chatbot that provides YouTube creators with practical, grounded advice based on video transcripts.

## Features

- ✅ Grounded responses based only on provided transcripts
- ✅ Timestamp citations for all recommendations
- ✅ Graceful handling of out-of-scope questions
- ✅ Simple CLI interface
- ✅ Comprehensive testing suite

## Setup

### Prerequisites
- Python 3.8+
- OpenAI API key
- pip (Python package manager)

### Installation

1. **Get OpenAI API Key**
   - Visit: https://platform.openai.com/api-keys
   - Create a new API key
   - Keep it secure!

2. **Clone/Download this project**
   ```bash
   cd "Youtube transcript"
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up API Key**
   Create a `.env` file in the project root:
   ```
   OPENAI_API_KEY=your-api-key-here
   ```

## Usage

### Quick Start
```bash
python src/chat.py --q "How can I improve my video introductions?"
```

### Interactive Mode
```bash
python src/chat.py
```

### Example Questions
- "How can I improve my video introductions?"
- "What are the best practices for thumbnails?"
- "How should I structure my videos for better storytelling?"
- "How do I maintain viewer retention?"

### Sample Output
```
Q: How can I improve my video introductions?

A: To improve your video introductions:

1. Keep intros extremely short (3-5 seconds maximum) then jump straight into value [source: "Improving Video Introductions" t=00:01:15]

2. Start with a hook - use questions or bold statements that create curiosity [source: "Improving Video Introductions" t=00:02:15]

3. Avoid long intros with music, graphics, or "Hey guys, welcome back" [source: "Improving Video Introductions" t=00:03:30]
```

## Testing

Run the test suite to validate functionality:

```bash
python tests/test_advisor.py
```

The test suite validates:
- ✅ **Citation Format**: All responses include properly formatted citations
- ✅ **Grounding**: Responses cite correct videos and timestamps
- ✅ **Fallback**: Graceful handling of out-of-scope questions

## Model Details

- **LLM**: OpenAI GPT-3.5-turbo
- **Embeddings**: SentenceTransformers 'all-MiniLM-L6-v2'
- **Similarity**: Cosine similarity for semantic search
- **Temperature**: 0.3 (for consistent, factual responses)

## Cost & Performance

- **Expected cost**: ~$0.01-0.02 per question
- **Response time**: 2-5 seconds per question
- **Memory usage**: ~200MB for embeddings

## Limitations

- Only covers topics in the provided transcripts (video introductions & storytelling)
- Requires OpenAI API key and internet connection
- Limited to ~800 token responses
- Sample transcripts are simplified for demonstration

## Future Improvements

- Add more transcript sources
- Implement local LLM support
- Add web interface
- Include video analytics integration
- Support for longer context windows

## Project Structure

```
.
├── README.md                # Setup and usage instructions
├── DESIGN.md               # Architecture decisions and tradeoffs
├── requirements.txt        # Python dependencies
├── .env                   # API keys (create this)
├── src/
│   ├── __init__.py
│   ├── chat.py            # Main CLI interface
│   ├── advisor.py         # Core chatbot logic
│   └── transcript_processor.py  # Transcript processing
├── tests/
│   ├── __init__.py
│   ├── test_advisor.py    # Test suite
│   └── eval.py           # Evaluation harness
└── transcripts/
    ├── aprilynne.txt     # Video introductions transcript
    └── hayden.txt        # Storytelling transcript
```

## License

This project is for educational purposes. Please ensure you comply with OpenAI's usage policies.