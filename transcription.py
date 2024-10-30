from pathlib import Path
import logging
from openai import OpenAI
from typing import Optional

from config import settings

logger = logging.getLogger(__name__)
client = OpenAI(api_key=settings.OPENAI_API_KEY)

def transcribe_recording(file_path: Path) -> Optional[str]:
    """
    Transcribe an audio recording using OpenAI's Whisper API.

    Args:
        file_path: Path to the audio file to transcribe.

    Returns:
        str: Transcribed text if successful, None otherwise.
    """
    try:
        with open(file_path, 'rb') as audio_file:
            response = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
            transcription = response.text
            logger.info(f"Transcription complete: {len(transcription)} characters")
            return transcription
    except Exception as e:
        logger.error(f"Transcription failed: {e}")
        return None

