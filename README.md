Radio AI – Smart RJ Generator
A Python application that generates synthetic radio shows from Wikipedia topics.
What it does
Takes a Wikipedia topic (e.g., "Artificial Intelligence", "Mumbai", "Python Programming")
Fetches content from Wikipedia
Generates a Hinglish radio conversation using OpenAI GPT-4o-mini
Converts the script to speech using ElevenLabs TTS with two voices:
Anjli (female)
Hitesh (male)
Mixes dialogue with background music
Produces a final MP3 radio show
Features
Web interface (Streamlit)
Script review and editing
Audio settings: pause duration, background music volume
Custom background music upload
Show history: save and replay past shows
Two AI hosts for conversational format
How it works
Wikipedia Topic → Content Fetching → AI Script Generation → Voice Synthesis → Audio Mixing → Final Radio Show (MP3)
Use cases
Content creators
Podcasters
Educational content
Radio-style entertainment
Demo videos and presentations
Technology stack
Frontend: Streamlit
AI: OpenAI GPT-4o-mini (script generation)
TTS: ElevenLabs (voice synthesis)
Audio: pydub/FFmpeg (processing)
In short: enter a topic, get a ready-to-use radio show in minutes.
