"""
Show History Management
Stores and retrieves generated radio shows
"""
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

HISTORY_FILE = Path(__file__).parent / "show_history.json"

def load_history() -> List[Dict]:
    """Load show history from JSON file."""
    if not HISTORY_FILE.exists():
        return []
    try:
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []

def save_history(history: List[Dict]):
    """Save show history to JSON file."""
    try:
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
    except IOError:
        pass

def add_show(topic: str, script: str, audio_file: str, metadata: Optional[Dict] = None) -> Dict:
    """Add a new show to history.
    
    Args:
        topic: The topic of the show
        script: The script text
        audio_file: Path to the audio file
        metadata: Optional additional metadata
        
    Returns:
        The created show entry
    """
    history = load_history()
    
    show_entry = {
        "id": len(history) + 1,
        "topic": topic,
        "script": script,
        "audio_file": audio_file,
        "created_at": datetime.now().isoformat(),
        "metadata": metadata or {}
    }
    
    history.append(show_entry)
    save_history(history)
    return show_entry

def get_show(show_id: int) -> Optional[Dict]:
    """Get a specific show by ID."""
    history = load_history()
    for show in history:
        if show.get("id") == show_id:
            return show
    return None

def get_all_shows(limit: Optional[int] = None) -> List[Dict]:
    """Get all shows, optionally limited to most recent N."""
    history = load_history()
    # Return in reverse chronological order (newest first)
    history.reverse()
    if limit:
        return history[:limit]
    return history

def delete_show(show_id: int) -> bool:
    """Delete a show from history."""
    history = load_history()
    original_length = len(history)
    history = [show for show in history if show.get("id") != show_id]
    
    if len(history) < original_length:
        save_history(history)
        return True
    return False

def clear_history():
    """Clear all show history."""
    save_history([])

