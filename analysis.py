import logging
from openai import OpenAI
from typing import Optional, Dict, Any

from config import settings

logger = logging.getLogger(__name__)
client = OpenAI(api_key=settings.OPENAI_API_KEY)

SYSTEM_PROMPT = """You are an AI assistant analyzing customer service call transcriptions to discover voice agent capabilities.
Your task is to:
1. Identify the customer's primary intent and any secondary intents
2. List all specific capabilities demonstrated by the voice agent
3. Note any limitations or scenarios the agent struggled with
4. Suggest additional test scenarios based on the interaction

Format your response as a structured JSON object with these keys:
- primary_intent: string
- secondary_intents: list of strings
- capabilities: list of strings
- limitations: list of strings
- suggested_scenarios: list of strings"""

def analyze_transcript(transcription: str) -> Optional[Dict[str, Any]]:
    """
    Analyze a call transcription using GPT-4o to extract insights.

    Args:
        transcription: The text transcription to analyze.

    Returns:
        dict: Structured analysis if successful, None otherwise.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Analyze this call transcription:\n\n{transcription}"}
            ],
            response_format={ "type": "json_object" }
        )

        analysis = response.choices[0].message.content
        logger.info("Analysis complete")
        return analysis
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        return None
