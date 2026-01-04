
import os
import requests
from pydub import AudioSegment
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ===============================
# 🔑 ELEVENLABS API KEY
# ===============================
# Default key (can be overridden by passing api_key parameter)
ELEVENLABS_API_KEY_DEFAULT = os.getenv("ELEVENLABS_API_KEY", "sk_a52f07ae99c1af530ac8850922443ae691ed6a40f0869449")

# ===============================
# 📁 PATHS (Local execution)
# ===============================
BASE_PATH = Path(__file__).parent
AUDIO_PATH = BASE_PATH / "Audios"
BG_MUSIC = BASE_PATH / "bg_music.mp3"

os.makedirs(AUDIO_PATH, exist_ok=True)

# ===============================
# 🎙️ VOICE MAP (ONLY THESE)
# ===============================
VOICE_MAP = {
    "Anjli": "CtsswjMPVCOJeWrOc8lS",
    "Hitesh": "m5qndnI7u4OAdXhH0Mr5"
}

# ===============================
# 🎧 ELEVENLABS TTS
# ===============================
def generate_audio(text, voice_id, filename, api_key=None):
    """Generate audio using ElevenLabs TTS.
    
    Args:
        text: Text to convert to speech
        voice_id: ElevenLabs voice ID
        filename: Output filename
        api_key: Optional API key (uses default if not provided)
    """
    api_key = api_key or ELEVENLABS_API_KEY_DEFAULT
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json"
    }
    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2"
    }

    r = requests.post(url, json=payload, headers=headers)
    if r.status_code != 200:
        raise Exception(r.text)

    with open(filename, "wb") as f:
        f.write(r.content)

# ===============================
# 🧠 FINAL ENGINE FUNCTION
# ===============================
def generate_radio_show_from_script(
    script_text, 
    progress_callback=None, 
    elevenlabs_api_key=None,
    pause_duration_ms=800,
    bg_music_volume_db=-12,
    bg_music_path=None
):
    """Generate radio show audio from script.
    
    Args:
        script_text: The dialogue script
        progress_callback: Optional callback function for progress updates
        elevenlabs_api_key: Optional ElevenLabs API key (uses default if not provided)
        pause_duration_ms: Duration of pause between dialogues in milliseconds (default: 800ms)
        bg_music_volume_db: Background music volume in dB (default: -12, negative = quieter)
        bg_music_path: Optional custom path to background music file
    """
    def log(msg):
        if progress_callback:
            progress_callback(msg)

    log("🎙️ Generating audio from approved script")

    dialogue = []
    for line in script_text.split("\n"):
        line = line.strip()
        if line.startswith("Anjli:"):
            dialogue.append(("Anjli", line[6:].strip()))
        elif line.startswith("Hitesh:"):
            dialogue.append(("Hitesh", line[7:].strip()))

    if not dialogue:
        raise Exception("No valid dialogue found in script")

    audio_segments = []
    pause = AudioSegment.silent(duration=pause_duration_ms)

    for i, (speaker, text) in enumerate(dialogue):
        log(f"🔊 Voice {i+1}/{len(dialogue)}")
        filename = AUDIO_PATH / f"{i}_{speaker}.mp3"
        generate_audio(text, VOICE_MAP[speaker], str(filename), api_key=elevenlabs_api_key)
        segment = AudioSegment.from_mp3(str(filename))
        audio_segments.append(segment)
        
        # Add pause after each dialogue (except the last one)
        if i < len(dialogue) - 1:
            audio_segments.append(pause)

    final_audio = sum(audio_segments)

    # Determine background music path
    music_path = Path(bg_music_path) if bg_music_path else BG_MUSIC
    
    if music_path.exists():
        log("🎼 Mixing background music")
        bg = AudioSegment.from_mp3(str(music_path))
        # Apply volume adjustment
        bg = bg + bg_music_volume_db
        # Loop background music to match audio length
        bg = bg * (len(final_audio)//len(bg)+1)
        # Overlay background music with dialogue
        final_audio = bg[:len(final_audio)].overlay(final_audio)
    elif BG_MUSIC.exists():
        # Fallback to default if custom path doesn't exist
        log("🎼 Mixing background music (using default)")
        bg = AudioSegment.from_mp3(str(BG_MUSIC)) + bg_music_volume_db
        bg = bg * (len(final_audio)//len(bg)+1)
        final_audio = bg[:len(final_audio)].overlay(final_audio)

    output_file = BASE_PATH / "final_radio_show.mp3"
    final_audio.export(str(output_file), format="mp3")

    log("✅ Radio show complete")
    return str(output_file)
