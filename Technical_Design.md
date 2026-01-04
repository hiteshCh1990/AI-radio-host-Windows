# Technical Design Document

## Project Overview
The Radio AI – Smart RJ Generator converts Wikipedia articles into natural Hinglish radio-style conversations and audio. It provides a complete workflow from topic selection to final audio production with customizable settings.

## Architecture

### System Components

1. **Frontend (Streamlit Web Interface)**
   - User input and topic selection
   - Script generation and editing interface
   - Audio settings configuration
   - Show history and library management
   - Custom background music upload

2. **Content Processing Layer**
   - Wikipedia API integration for content fetching
   - OpenAI GPT-4o-mini for script generation
   - Script validation and parsing

3. **Audio Generation Engine**
   - ElevenLabs TTS API for voice synthesis
   - Audio segment processing with pydub
   - Background music mixing
   - Pause insertion between dialogues

4. **Data Persistence**
   - Show history storage (JSON-based)
   - Audio file management
   - Custom music file handling

### Data Flow

```
User Input (Topic)
    ↓
Wikipedia API → Content Summary
    ↓
OpenAI API → Hinglish Script
    ↓
User Review & Edit
    ↓
ElevenLabs API → Voice Segments (Anjli & Hitesh)
    ↓
Audio Engine → Combine + Pauses + Background Music
    ↓
Final MP3 Output
    ↓
Save to History (Optional)
```

## Tech Stack

- **Frontend**: Streamlit (Python web framework)
- **Language**: Python 3.8+
- **APIs**:
  - OpenAI API (GPT-4o-mini) for script generation
  - ElevenLabs API for text-to-speech
  - Wikipedia API for content fetching
- **Audio Processing**: pydub (FFmpeg wrapper)
- **Data Storage**: JSON files for show history
- **Testing**: pytest

## Key Features

### 1. Script Generation
- Fetches Wikipedia content for any topic
- Generates 30-line Hinglish conversations
- Alternating dialogue between two hosts
- Fixed intro and outro segments

### 2. Audio Processing
- Configurable pause duration between dialogues (0-2000ms)
- Adjustable background music volume (-30dB to 0dB)
- Custom background music upload support
- Automatic audio mixing and normalization

### 3. Show Management
- Save generated shows to history
- View and replay past shows
- Delete individual shows or clear history
- Metadata tracking (topic, date, settings)

### 4. User Interface
- Modern Streamlit-based web interface
- Real-time progress indicators
- Script editing capabilities
- Audio preview and download

## Setup Instructions

1. Install Python 3.8 or higher
2. Install dependencies: `pip install -r requirements.txt`
3. Install FFmpeg for audio processing
4. Configure API keys (OpenAI and ElevenLabs)
5. Run: `streamlit run app.py`

## File Structure

```
synthetic-radio-host/
├── app.py                 # Main Streamlit application
├── engine.py              # Audio generation engine
├── show_history.py        # Show history management
├── radio_ai_gui.py        # Legacy Jupyter notebook version
├── requirements.txt       # Python dependencies
├── run.bat / run.sh       # Launch scripts
├── Audios/                # Generated audio segments
├── tests/                 # Unit tests
│   └── test_engine.py
└── Docs/                  # Documentation
    ├── Technical_Design.md
    └── Hinglish_Prompt_Explanation.md
```

## API Integration

### OpenAI API
- **Model**: gpt-4o-mini
- **Purpose**: Generate Hinglish radio conversation scripts
- **Input**: Wikipedia content summary
- **Output**: Formatted dialogue script

### ElevenLabs API
- **Model**: eleven_multilingual_v2
- **Purpose**: Text-to-speech conversion
- **Voices**: 
  - Anjli (Female): `CtsswjMPVCOJeWrOc8lS`
  - Hitesh (Male): `m5qndnI7u4OAdXhH0Mr5`

### Wikipedia API
- **Library**: wikipedia (Python)
- **Purpose**: Fetch topic summaries
- **Error Handling**: Disambiguation and page not found

## Error Handling

1. **Script Validation**: Ensures valid dialogue format before audio generation
2. **API Errors**: Graceful handling of API failures with user-friendly messages
3. **File Operations**: Checks for file existence before operations
4. **SSL Issues**: Workarounds for Windows SSL certificate verification
5. **Empty Input**: Validation for empty topics and scripts

## Performance Considerations

- Audio segments are generated sequentially (could be parallelized)
- Background music is looped to match audio length
- Show history uses JSON storage (could be upgraded to database)
- Audio files are stored locally (consider cleanup mechanism)

## Security

- API keys stored in environment variables or .env file
- Input sanitization for Wikipedia topics
- File path validation for uploaded music

## Future Enhancements

- Parallel audio generation for faster processing
- Database storage for show history
- Cloud storage integration
- Multiple voice options
- Real-time audio preview
- Batch processing capabilities
