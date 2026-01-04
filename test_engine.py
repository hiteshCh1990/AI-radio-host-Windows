"""
Tests for the radio show generation engine.
"""
import pytest
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
from engine import generate_radio_show_from_script, VOICE_MAP

# Skip tests if API keys are not set (for CI/CD)
SKIP_TESTS = not os.getenv("ELEVENLABS_API_KEY") and not os.getenv("OPENAI_API_KEY")


def test_script_parsing_basic():
    """Test basic script parsing and audio generation."""
    script = """
    Anjli: Hello dosto, welcome to Radio AI!
    Hitesh: Hi Anjli, aaj hum baat karenge ek interesting topic ke baare mein.
    Anjli: Ha yaar, toh chalo shuru karte hain.
    """
    
    # Mock the API call to avoid actual API usage in tests
    with patch('engine.generate_audio'):
        # Create a mock audio file
        mock_audio = MagicMock()
        mock_audio.__len__ = lambda x: 1000  # Mock duration
        mock_audio.__add__ = lambda x, y: mock_audio  # Mock sum() operation
        mock_audio.__mul__ = lambda x, y: mock_audio  # Mock multiplication
        mock_audio.__getitem__ = lambda x, y: mock_audio  # Mock slicing
        mock_audio.overlay = lambda x: mock_audio  # Mock overlay method
        mock_audio.export = MagicMock()  # Mock export method
        
        with patch('pydub.AudioSegment.from_mp3', return_value=mock_audio):
            with patch('pydub.AudioSegment.silent', return_value=mock_audio):
                # Mock Path.exists() - it's called as a method on Path objects
                # We need to patch it at the Path class level
                original_exists = Path.exists
                def mock_exists(self):
                    # Return False for bg_music files, True otherwise
                    path_str = str(self)
                    if 'bg_music' in path_str:
                        return False
                    # For other paths, use original behavior or return True
                    try:
                        return original_exists(self)
                    except:
                        return True
                
                with patch.object(Path, 'exists', mock_exists):
                    output = generate_radio_show_from_script(
                        script,
                        pause_duration_ms=500,
                        bg_music_volume_db=-12
                    )
                    assert output.endswith(".mp3")
                    # Check that output path is valid (string ends with .mp3)
                    assert isinstance(output, str)


def test_script_parsing_empty():
    """Test that empty script raises exception."""
    script = ""
    
    with pytest.raises(Exception, match="No valid dialogue"):
        generate_radio_show_from_script(script)


def test_script_parsing_invalid_format():
    """Test that script without proper format raises exception."""
    script = "This is not a valid script format"
    
    with pytest.raises(Exception, match="No valid dialogue"):
        generate_radio_show_from_script(script)


def test_script_parsing_anjli_only():
    """Test script with only Anjli lines."""
    script = """
    Anjli: Hello dosto
    Anjli: This is a test
    """
    
    with patch('engine.generate_audio'):
        mock_audio = MagicMock()
        mock_audio.__len__ = lambda x: 1000
        mock_audio.__add__ = lambda x, y: mock_audio
        mock_audio.__mul__ = lambda x, y: mock_audio
        mock_audio.__getitem__ = lambda x, y: mock_audio
        mock_audio.overlay = lambda x: mock_audio
        mock_audio.export = MagicMock()
        
        with patch('pydub.AudioSegment.from_mp3', return_value=mock_audio):
            with patch('pydub.AudioSegment.silent', return_value=mock_audio):
                with patch('pathlib.Path.exists', return_value=False):
                    output = generate_radio_show_from_script(script)
                    assert output.endswith(".mp3")


def test_script_parsing_hitesh_only():
    """Test script with only Hitesh lines."""
    script = """
    Hitesh: Hello everyone
    Hitesh: This is a test
    """
    
    with patch('engine.generate_audio'):
        mock_audio = MagicMock()
        mock_audio.__len__ = lambda x: 1000
        mock_audio.__add__ = lambda x, y: mock_audio
        mock_audio.__mul__ = lambda x, y: mock_audio
        mock_audio.__getitem__ = lambda x, y: mock_audio
        mock_audio.overlay = lambda x: mock_audio
        mock_audio.export = MagicMock()
        
        with patch('pydub.AudioSegment.from_mp3', return_value=mock_audio):
            with patch('pydub.AudioSegment.silent', return_value=mock_audio):
                with patch('pathlib.Path.exists', return_value=False):
                    output = generate_radio_show_from_script(script)
                    assert output.endswith(".mp3")


def test_pause_duration_parameter():
    """Test that pause duration parameter is accepted."""
    script = """
    Anjli: Test line 1
    Hitesh: Test line 2
    """
    
    with patch('engine.generate_audio'):
        mock_audio = MagicMock()
        mock_audio.__len__ = lambda x: 1000
        mock_audio.__add__ = lambda x, y: mock_audio
        mock_audio.__mul__ = lambda x, y: mock_audio
        mock_audio.__getitem__ = lambda x, y: mock_audio
        mock_audio.overlay = lambda x: mock_audio
        mock_audio.export = MagicMock()
        
        with patch('pydub.AudioSegment.from_mp3', return_value=mock_audio):
            with patch('pydub.AudioSegment.silent') as mock_silent:
                mock_silent.return_value = mock_audio
                with patch('pathlib.Path.exists', return_value=False):
                    generate_radio_show_from_script(
                        script,
                        pause_duration_ms=1000
                    )
                    # Verify silent audio was called (for pause)
                    assert mock_silent.called


def test_bg_music_volume_parameter():
    """Test that background music volume parameter is accepted."""
    script = """
    Anjli: Test line 1
    Hitesh: Test line 2
    """
    
    with patch('engine.generate_audio'):
        mock_audio = MagicMock()
        mock_audio.__len__ = lambda x: 1000
        mock_audio.__add__ = lambda x, y: mock_audio
        mock_audio.__mul__ = lambda x, y: mock_audio
        mock_audio.__getitem__ = lambda x, y: mock_audio
        mock_audio.overlay = lambda x: mock_audio
        mock_audio.export = MagicMock()
        # Mock __add__ for volume adjustment (bg + volume_db)
        mock_audio.__radd__ = lambda x, y: mock_audio
        
        with patch('pydub.AudioSegment.from_mp3', return_value=mock_audio):
            with patch('pydub.AudioSegment.silent', return_value=mock_audio):
                with patch('pathlib.Path.exists', return_value=False):
                    # Should not raise error with custom volume
                    output = generate_radio_show_from_script(
                        script,
                        bg_music_volume_db=-20
                    )
                    assert output.endswith(".mp3")


def test_voice_map():
    """Test that voice map contains expected voices."""
    assert "Anjli" in VOICE_MAP
    assert "Hitesh" in VOICE_MAP
    assert len(VOICE_MAP) == 2