import streamlit as st
import os
from openai import OpenAI
import wikipedia
import requests
import urllib3
from engine import generate_radio_show_from_script
from pathlib import Path
from dotenv import load_dotenv
from show_history import add_show, get_all_shows, delete_show, get_show, clear_history
import shutil

# Load environment variables from .env file
load_dotenv()

# ===============================
# 🔒 SSL CERTIFICATE FIX (Windows)
# ===============================
# Disable SSL warnings for development
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configure wikipedia to handle SSL certificate issues on Windows
# This patches the requests library used by wikipedia
wikipedia.set_user_agent("RadioAI/1.0")

# Monkey patch requests.Session to disable SSL verification
# This is a workaround for Windows SSL certificate verification issues
_original_request = requests.Session.request
def _patched_request(self, method, url, **kwargs):
    kwargs.setdefault('verify', False)
    return _original_request(self, method, url, **kwargs)
requests.Session.request = _patched_request

# ===============================
# 🔑 API KEYS (from environment or default)
# ===============================
# Get API key from environment variable or use default
# For security, set OPENAI_API_KEY as environment variable
# You can update this key directly here or use environment variable
OPENAI_API_KEY_DEFAULT = os.getenv("OPENAI_API_KEY", "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")

# Initialize API keys in session state (will be updated if user inputs keys in sidebar)
if "openai_api_key" not in st.session_state:
    st.session_state.openai_api_key = OPENAI_API_KEY_DEFAULT

# Get ElevenLabs API key default
ELEVENLABS_API_KEY_DEFAULT = os.getenv("ELEVENLABS_API_KEY", "sk_a52f07ae99c1af530ac8850922443ae691ed6a40f0869449")
if "elevenlabs_api_key" not in st.session_state:
    st.session_state.elevenlabs_api_key = ELEVENLABS_API_KEY_DEFAULT

def get_openai_client():
    """Get OpenAI client with current API key."""
    return OpenAI(api_key=st.session_state.openai_api_key)

# ===============================
# PAGE CONFIG
# ===============================
st.set_page_config(
    page_title="Radio AI – Smart RJ Generator",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===============================
# CUSTOM CSS STYLING
# ===============================
st.markdown("""
<style>
    /* Main container styling */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Header styling */
    h1 {
        background: linear-gradient(90deg, #FF6B6B 0%, #4ECDC4 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 3rem !important;
        font-weight: 700 !important;
        text-align: center;
        margin-bottom: 0.5rem !important;
    }
    
    /* Subtitle styling */
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    
    /* Card-like containers */
    .stContainer {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* Input field styling */
    .stTextInput > div > div > input {
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        padding: 0.75rem;
        font-size: 1rem;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Button styling */
    .stButton > button {
        border-radius: 10px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        border: none;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
    }
    
    /* Textarea styling */
    .stTextArea > div > div > textarea {
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        font-family: 'Courier New', monospace;
        font-size: 0.95rem;
        line-height: 1.6;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* Success/Info messages */
    .stSuccess {
        border-radius: 10px;
        padding: 1rem;
    }
    
    .stInfo {
        border-radius: 10px;
        padding: 1rem;
    }
    
    /* Divider styling */
    hr {
        margin: 1.5rem 0;
        border: none;
        border-top: 2px solid #e0e0e0;
    }
    
    /* Card containers for sections */
    .info-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
    }
    
    /* Status indicators */
    .status-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 600;
        margin: 0.5rem 0;
    }
    
    .status-waiting {
        background: #fff3cd;
        color: #856404;
    }
    
    .status-generating {
        background: #d1ecf1;
        color: #0c5460;
    }
    
    .status-ready {
        background: #d4edda;
        color: #155724;
    }
</style>
""", unsafe_allow_html=True)

# ===============================
# SESSION STATE
# ===============================
if "current_script" not in st.session_state:
    st.session_state.current_script = None
if "current_topic" not in st.session_state:
    st.session_state.current_topic = None
if "pause_duration" not in st.session_state:
    st.session_state.pause_duration = 800  # milliseconds
if "bg_music_volume" not in st.session_state:
    st.session_state.bg_music_volume = -12  # dB
if "custom_bg_music" not in st.session_state:
    st.session_state.custom_bg_music = None
if "show_history_view" not in st.session_state:
    st.session_state.show_history_view = False

# ===============================
# UI HEADER
# ===============================
st.markdown("<h1>🎙️ Radio AI – Smart RJ Generator</h1>", unsafe_allow_html=True)
st.markdown('<p class="subtitle">Transform Wikipedia topics into engaging Hinglish radio conversations</p>', unsafe_allow_html=True)

# Add a decorative line
st.markdown("---")

# ===============================
# SHOW HISTORY / LIBRARY SECTION
# ===============================
if st.session_state.show_history_view:
    st.markdown("### 📚 Show History & Library")
    
    shows = get_all_shows()
    
    if shows:
        st.info(f"📊 You have {len(shows)} saved show(s)")
        
        for show in shows:
            with st.expander(f"🎙️ {show.get('topic', 'Untitled')} - {show.get('created_at', '')[:10]}"):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**Topic:** {show.get('topic', 'N/A')}")
                    st.markdown(f"**Created:** {show.get('created_at', 'N/A')}")
                    
                    audio_file = show.get('audio_file')
                    if audio_file and Path(audio_file).exists():
                        st.audio(audio_file, format="audio/mp3")
                    else:
                        st.warning("⚠️ Audio file not found")
                
                with col2:
                    if st.button("🗑️ Delete", key=f"delete_{show.get('id')}"):
                        delete_show(show.get('id'))
                        st.rerun()
                    
                    if st.button("📝 View Script", key=f"script_{show.get('id')}"):
                        st.text_area("Script", value=show.get('script', ''), height=200, key=f"script_view_{show.get('id')}")
        
        if st.button("🗑️ Clear All History"):
            clear_history()
            st.rerun()
    else:
        st.info("📭 No shows in history yet. Generate your first show to see it here!")
    
    if st.button("← Back to Generator"):
        st.session_state.show_history_view = False
        st.rerun()
    
    st.markdown("---")

# ===============================
# TOPIC INPUT SECTION
# ===============================
st.markdown("### 📝 Step 1: Enter Your Topic")
st.markdown("Choose any topic from Wikipedia to create your radio show")

# Create a container for the input section
with st.container():
    col1, col2 = st.columns([3, 1])
    
    with col1:
        topic = st.text_input(
            "Enter Wikipedia Topic",
            placeholder="e.g., National Stock Exchange, Mumbai, Python Programming, Artificial Intelligence",
            help="Enter any topic that exists on Wikipedia",
            label_visibility="collapsed"
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)  # Spacing
        generate_script_btn = st.button("🎧 Generate Script", type="primary", use_container_width=True)
    
    if topic:
        st.caption(f"✨ Ready to generate script for: **{topic}**")

# ===============================
# SCRIPT GENERATION
# ===============================
def fetch_wikipedia_summary(topic_name, sentences=20):
    """Fetch Wikipedia summary with SSL error handling."""
    try:
        # Try normal request first
        return wikipedia.summary(topic_name, sentences=sentences)
    except Exception as e:
        if "SSL" in str(e) or "CERTIFICATE" in str(e) or "certificate verify failed" in str(e):
            # If SSL error, try with SSL verification disabled
            import wikipedia.wikipedia as wiki_module
            # Temporarily disable SSL verification
            original_get = requests.get
            def patched_get(*args, **kwargs):
                kwargs['verify'] = False
                return original_get(*args, **kwargs)
            requests.get = patched_get
            try:
                result = wikipedia.summary(topic_name, sentences=sentences)
                return result
            finally:
                requests.get = original_get
        else:
            raise

def generate_script(topic_name):
    try:
        with st.spinner("🔍 Fetching Wikipedia content..."):
            wiki = fetch_wikipedia_summary(topic_name, sentences=20)
        
        with st.spinner("✍️ Writing radio conversation..."):
            # Fixed Intro
            intro = """Anjli: Hello dosto, welcome to Radio AI! Main hu Anjli.
Hitesh: Aur main hu Hitesh. Aaj Radio AI par hum baat karenge ek kaafi interesting topic ke baare mein.
Anjli: Ha yaar, toh bina time waste kiye chalo shuru karte hain aaj ka discussion."""

            # Fixed Outro
            outro = """Anjli: Toh dosto, umeed hai aaj ka discussion aapko pasand aaya hoga.
Hitesh: Agar pasand aaya ho toh Radio AI ke saath jude rahiye, aur aise hi interesting topics ke liye.
Anjli: Main hu Anjli,
Hitesh: Aur main hu Hitesh,
Anjli: Milte hain next episode mein, tab tak ke liye bye bye!"""

            prompt = f"""
You are a professional Indian FM RJ.

STRICT RULES:
- EXACTLY 30 lines
- 15 lines start with Anjli:
- 15 lines start with Hitesh:
- CRITICAL: Dialogue MUST alternate in sequence - Start with Anjli, then Hitesh, then Anjli, then Hitesh, and so on
- The sequence must be: Anjli, Hitesh, Anjli, Hitesh, Anjli, Hitesh... (alternating pattern)
- Hinglish, casual RJ tone
- Always use station name "Radio AI"
- Never use "Radio XYZ"
- Only dialogue
- Make it sound like a natural conversation between two hosts
- NOTE: Intro and Outro will be added automatically, so generate ONLY the main conversation content

Topic:
{wiki}

Output ONLY the main dialogue in alternating sequence (Anjli, Hitesh, Anjli, Hitesh...). Do NOT include intro or outro.
"""

            client = get_openai_client()
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8
            )

            main_script = response.choices[0].message.content.strip()
            
            # Combine intro + main script + outro
            full_script = f"{intro}\n\n{main_script}\n\n{outro}"
            
            st.session_state.current_script = full_script
            st.session_state.current_topic = topic_name
            return full_script
    except wikipedia.exceptions.DisambiguationError as e:
        st.error(f"❌ Multiple topics found. Please be more specific. Options: {', '.join(e.options[:5])}")
        return None
    except wikipedia.exceptions.PageError:
        st.error("❌ Topic not found on Wikipedia. Please try a different topic.")
        return None
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        return None

# ===============================
# MAIN INTERFACE
# ===============================
if generate_script_btn:
    if not topic.strip():
        st.warning("⚠️ Please enter a topic")
    else:
        script = generate_script(topic.strip())
        if script:
            st.success("✅ Script generated! Review it below.")

# ===============================
# SCRIPT DISPLAY SECTION
# ===============================
if st.session_state.current_script:
    st.markdown("---")
    st.markdown("### 📖 Step 2: Review & Edit Script")
    st.markdown("Review the generated script below. You can edit it before generating audio.")
    
    # Script editor with better styling
    script_text = st.text_area(
        "Edit the script if needed:",
        value=st.session_state.current_script,
        height=400,
        key="script_editor",
        help="Make any edits to the script. The format should be 'Anjli: ...' or 'Hitesh: ...'"
    )
    
    st.session_state.current_script = script_text
    
    # Audio Settings
    with st.expander("⚙️ Audio Settings"):
        col1, col2 = st.columns(2)
        
        with col1:
            pause_duration = st.slider(
                "⏸️ Pause Between Dialogues (ms)",
                min_value=0,
                max_value=2000,
                value=st.session_state.pause_duration,
                step=100,
                help="Duration of silence between dialogue lines"
            )
            st.session_state.pause_duration = pause_duration
        
        with col2:
            bg_volume = st.slider(
                "🔊 Background Music Volume (dB)",
                min_value=-30,
                max_value=0,
                value=st.session_state.bg_music_volume,
                step=1,
                help="Lower values = quieter background music (default: -12dB)"
            )
            st.session_state.bg_music_volume = bg_volume
    
    # Action buttons in a nice layout
    st.markdown("#### 🎬 Actions")
    col1, col2, col3 = st.columns([1.5, 1.5, 2])
    
    with col1:
        approve_btn = st.button("✅ Approve & Generate Audio", type="primary", use_container_width=True)
    
    with col2:
        regen_btn = st.button("🔁 Regenerate Script", use_container_width=True)
    
    with col3:
        st.caption("💡 Tip: Make sure the script follows the Anjli/Hitesh format")
    
    if regen_btn:
        if st.session_state.current_topic:
            script = generate_script(st.session_state.current_topic)
            if script:
                st.rerun()
        else:
            st.warning("⚠️ No topic available. Please generate a new script.")
    
    # ===============================
    # AUDIO GENERATION SECTION
    # ===============================
    if approve_btn:
        if not script_text.strip():
            st.error("❌ Script is empty. Please enter a valid script.")
        else:
            st.markdown("---")
            st.markdown("### 🎵 Step 3: Generating Audio")
            
            progress_container = st.container()
            with progress_container:
                # Status card
                with st.container():
                    st.markdown("""
                    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                padding: 1.5rem; border-radius: 15px; color: white; margin-bottom: 1rem;'>
                        <h4 style='color: white; margin: 0;'>🎙️ Generating Audio...</h4>
                        <p style='color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0;'>Please wait while we create your radio show</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                def progress_callback(msg):
                    status_text.text(msg)
                    # Simple progress update
                    if "Voice" in msg:
                        try:
                            # Extract number from "Voice X/Y"
                            parts = msg.split("/")
                            if len(parts) > 1:
                                current = int(parts[0].split()[-1])
                                total = int(parts[1])
                                progress_bar.progress(current / total)
                        except:
                            pass
                
                try:
                    # Determine background music path
                    bg_music_path = None
                    if st.session_state.custom_bg_music:
                        bg_music_path = st.session_state.custom_bg_music
                    
                    audio_file = generate_radio_show_from_script(
                        script_text,
                        progress_callback,
                        elevenlabs_api_key=st.session_state.elevenlabs_api_key,
                        pause_duration_ms=st.session_state.pause_duration,
                        bg_music_volume_db=st.session_state.bg_music_volume,
                        bg_music_path=bg_music_path
                    )
                    
                    progress_bar.progress(1.0)
                    status_text.markdown("""
                    <div style='background: #d4edda; padding: 1rem; border-radius: 10px; 
                                border-left: 4px solid #28a745; margin-top: 1rem;'>
                        <strong>✅ Radio show complete!</strong>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("---")
                    st.markdown("### 🎉 Your Radio Show is Ready!")
                    
                    # Success message with styling
                    st.markdown("""
                    <div style='background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); 
                                padding: 2rem; border-radius: 15px; color: white; text-align: center; margin: 1rem 0;'>
                        <h3 style='color: white; margin: 0 0 1rem 0;'>✨ Audio Generated Successfully!</h3>
                        <p style='color: rgba(255,255,255,0.95); margin: 0;'>Listen to your radio show below</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Audio player in a styled container
                    st.markdown("#### 🎧 Listen to Your Radio Show")
                    st.audio(audio_file, format="audio/mp3")
                    
                    # Download button with better styling
                    st.markdown("#### 📥 Download")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        with open(audio_file, "rb") as f:
                            st.download_button(
                                label="⬇️ Download Radio Show (MP3)",
                                data=f.read(),
                                file_name=f"radio_show_{st.session_state.current_topic.replace(' ', '_') if st.session_state.current_topic else 'show'}.mp3",
                                mime="audio/mp3",
                                use_container_width=True,
                                type="primary"
                            )
                    
                    with col2:
                        if st.button("💾 Save to History", use_container_width=True):
                            show_entry = add_show(
                                topic=st.session_state.current_topic or "Untitled",
                                script=script_text,
                                audio_file=audio_file,
                                metadata={
                                    "pause_duration": st.session_state.pause_duration,
                                    "bg_music_volume": st.session_state.bg_music_volume
                                }
                            )
                            st.success(f"✅ Show saved to history! (ID: {show_entry['id']})")
                    
                except Exception as e:
                    st.error(f"❌ Error generating audio: {str(e)}")
                    import traceback
                    st.code(traceback.format_exc())

# ===============================
# SIDEBAR INFO
# ===============================
with st.sidebar:
    # Logo/Header section
    st.markdown("""
    <div style='text-align: center; padding: 1rem 0;'>
        <h2 style='color: #667eea; margin: 0;'>🎙️ Radio AI</h2>
        <p style='color: #666; font-size: 0.9rem; margin: 0.5rem 0 0 0;'>Smart RJ Generator</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Show History Button
    if st.button("📚 Show History & Library", use_container_width=True):
        st.session_state.show_history_view = True
        st.rerun()
    
    st.markdown("---")
    
    # Custom Background Music Upload
    st.markdown("### 🎵 Custom Background Music")
    uploaded_music = st.file_uploader(
        "Upload Background Music",
        type=['mp3', 'wav', 'ogg', 'm4a'],
        help="Upload your own background music file (MP3, WAV, OGG, or M4A)"
    )
    
    if uploaded_music is not None:
        # Save uploaded file temporarily
        custom_music_path = Path(__file__).parent / "custom_bg_music.mp3"
        with open(custom_music_path, "wb") as f:
            f.write(uploaded_music.getbuffer())
        st.session_state.custom_bg_music = str(custom_music_path)
        st.success(f"✅ Custom music uploaded: {uploaded_music.name}")
        
        if st.button("🗑️ Remove Custom Music"):
            if custom_music_path.exists():
                custom_music_path.unlink()
            st.session_state.custom_bg_music = None
            st.rerun()
    elif st.session_state.custom_bg_music and Path(st.session_state.custom_bg_music).exists():
        st.info(f"🎵 Using custom music: {Path(st.session_state.custom_bg_music).name}")
        if st.button("🗑️ Remove Custom Music"):
            Path(st.session_state.custom_bg_music).unlink()
            st.session_state.custom_bg_music = None
            st.rerun()
    else:
        st.caption("💡 Leave empty to use default background music")
    
    st.markdown("---")
    
    # About section with better styling
    st.markdown("### 📚 How It Works")
    st.markdown("""
    <div style='background: white; padding: 1rem; border-radius: 10px; margin: 0.5rem 0;'>
        <p style='margin: 0.5rem 0;'>1️⃣ <strong>Fetch</strong> content from Wikipedia</p>
        <p style='margin: 0.5rem 0;'>2️⃣ <strong>Generate</strong> Hinglish conversation</p>
        <p style='margin: 0.5rem 0;'>3️⃣ <strong>Convert</strong> to natural speech</p>
        <p style='margin: 0.5rem 0;'>4️⃣ <strong>Mix</strong> with background music</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### ✨ Features")
    st.markdown("""
    - 🎤 Two AI hosts (Anjli & Hitesh)
    - 💬 Natural Hinglish conversations
    - 🎵 Background music mixing
    - ✏️ Script review & editing
    - 🎧 High-quality audio output
    """)
    
    st.markdown("---")
    
    st.markdown("### ⚙️ API Configuration")
    
    # OpenAI API Key Input with better styling
    with st.container():
        st.markdown("#### 🤖 OpenAI API Key")
        st.caption("For script generation")
        openai_key_input = st.text_input(
            "OpenAI API Key:",
            value=st.session_state.openai_api_key,
            type="password",
            key="openai_key_input",
            help="Get your API key from https://platform.openai.com/api-keys",
            label_visibility="collapsed"
        )
        if openai_key_input and openai_key_input != st.session_state.openai_api_key:
            st.session_state.openai_api_key = openai_key_input
            st.success("✅ OpenAI API key updated!")
        
        if os.getenv("OPENAI_API_KEY"):
            st.info("ℹ️ Using environment variable")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ElevenLabs API Key Input with better styling
    with st.container():
        st.markdown("#### 🎤 ElevenLabs API Key")
        st.caption("For text-to-speech")
        elevenlabs_key_input = st.text_input(
            "ElevenLabs API Key:",
            value=st.session_state.elevenlabs_api_key,
            type="password",
            key="elevenlabs_key_input",
            help="Get your API key from https://elevenlabs.io/app/settings/api-keys",
            label_visibility="collapsed"
        )
        if elevenlabs_key_input and elevenlabs_key_input != st.session_state.elevenlabs_api_key:
            st.session_state.elevenlabs_api_key = elevenlabs_key_input
            st.success("✅ ElevenLabs API key updated!")
        
        if os.getenv("ELEVENLABS_API_KEY"):
            st.info("ℹ️ Using environment variable")
    
    st.markdown("---")
    
    # Tips section
    st.markdown("""
    <div style='background: #e3f2fd; padding: 1rem; border-radius: 10px; border-left: 4px solid #2196f3;'>
        <p style='margin: 0; font-size: 0.9rem;'><strong>💡 Tip:</strong> API keys are saved in session. 
        Changes take effect immediately.</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🔄 Clear Session"):
        st.session_state.current_script = None
        st.session_state.current_topic = None
        st.rerun()

