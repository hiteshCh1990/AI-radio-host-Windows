
import ipywidgets as widgets
from IPython.display import display, Audio, clear_output
from engine import generate_radio_show_from_script
from openai import OpenAI
import wikipedia

# ===============================
# 🔑 OPENAI API KEY
# ===============================
OPENAI_API_KEY = "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"
client = OpenAI(api_key="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")

# ===============================
# GLOBAL STATE
# ===============================
current_script = None
current_topic = None

# ===============================
# UI ELEMENTS
# ===============================

title = widgets.HTML("<h2>🎙️ Radio AI – Smart RJ Generator</h2>")

topic_input = widgets.Text(
    placeholder="Enter Wikipedia topic (e.g. National Stock Exchange)",
    description="Topic:",
    layout=widgets.Layout(width="70%")
)

status = widgets.HTML("<b>Status:</b> Waiting")

generate_btn = widgets.Button(
    description="🎧 Generate Audio",
    button_style="success",
    layout=widgets.Layout(width="40%")
)

approve_btn = widgets.Button(
    description="✅ Approve & Continue",
    button_style="info",
    disabled=True,
    layout=widgets.Layout(width="40%")
)

regen_btn = widgets.Button(
    description="🔁 Regenerate Script",
    button_style="warning",
    disabled=True,
    layout=widgets.Layout(width="40%")
)

script_box = widgets.Textarea(
    layout=widgets.Layout(width="95%", height="360px"),
    disabled=True
)

output = widgets.Output()

# ===============================
# SCRIPT GENERATION
# ===============================

def generate_script():
    global current_script

    status.value = "🔍 Fetching Wikipedia content"
    wiki = wikipedia.summary(current_topic, sentences=20)

    status.value = "✍️ Writing radio conversation"

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

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8
    )

    main_script = response.choices[0].message.content.strip()
    
    # Combine intro + main script + outro
    current_script = f"{intro}\n\n{main_script}\n\n{outro}"
    script_box.value = current_script
    script_box.disabled = False

    approve_btn.disabled = False
    regen_btn.disabled = False

    status.value = "📖 Review the script, then approve or regenerate"

# ===============================
# AUDIO GENERATION (APPROVED SCRIPT ONLY)
# ===============================

def generate_audio():
    with output:
        clear_output()
        status.value = "🎙️ Generating audio from approved script"

        approved_script = script_box.value.strip()
        if not approved_script:
            print("❌ Script is empty")
            return

        def progress(msg):
            print(msg)

        audio = generate_radio_show_from_script(
            approved_script,
            progress
        )

        status.value = "✅ Radio show complete"
        display(Audio(audio))

# ===============================
# BUTTON HANDLERS
# ===============================

def on_generate_clicked(b):
    global current_topic
    current_topic = topic_input.value.strip()

    if not current_topic:
        status.value = "❌ Please enter a topic"
        return

    approve_btn.disabled = True
    regen_btn.disabled = True
    script_box.disabled = True

    generate_script()

def on_approve_clicked(b):
    approve_btn.disabled = True
    regen_btn.disabled = True
    generate_audio()

def on_regen_clicked(b):
    approve_btn.disabled = True
    regen_btn.disabled = True
    generate_script()

generate_btn.on_click(on_generate_clicked)
approve_btn.on_click(on_approve_clicked)
regen_btn.on_click(on_regen_clicked)

# ===============================
# DISPLAY GUI
# ===============================

display(
    widgets.VBox([
        title,
        topic_input,
        status,
        generate_btn,
        script_box,
        widgets.HBox([approve_btn, regen_btn]),
        output
    ])
)
