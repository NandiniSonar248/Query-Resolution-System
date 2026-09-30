import httpx
from fastapi import HTTPException, status
from app.core.config import settings

async def transcribe_audio(file_bytes: bytes, filename: str) -> str:
    """
    Send audio file to ElevenLabs Speech-to-Text API.
    Returns the transcribed text.
    """
    if not settings.SPEECH_ENABLED or not settings.ELEVENLABS_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Speech services are not configured or disabled."
        )
    
    url = f"{settings.ELEVENLABS_BASE_URL}/speech-to-text"
    headers = {
        "xi-api-key": settings.ELEVENLABS_API_KEY,
    }
    
    files = {
        "file": (filename, file_bytes, "audio/mpeg") # Defaulting to mpeg/webm, elevenlabs handles various formats
    }
    
    data = {
        "model_id": settings.ELEVENLABS_STT_MODEL,
    }
    
    async with httpx.AsyncClient(timeout=settings.SPEECH_REQUEST_TIMEOUT_SECONDS) as client:
        try:
            response = await client.post(url, headers=headers, files=files, data=data)
            response.raise_for_status()
            result = response.json()
            return result.get("text", "")
        except httpx.HTTPStatusError as e:
            error_msg = e.response.text
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"ElevenLabs STT error: {error_msg}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to transcribe audio: {str(e)}"
            )

async def synthesize_speech(text: str) -> bytes:
    """
    Send text to ElevenLabs Text-to-Speech API.
    Returns the audio bytes.
    """
    if not settings.SPEECH_ENABLED or not settings.ELEVENLABS_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Speech services are not configured or disabled."
        )
        
    if len(text) > settings.SPEECH_MAX_TTS_CHARS:
        text = text[:settings.SPEECH_MAX_TTS_CHARS]
        
    url = f"{settings.ELEVENLABS_BASE_URL}/text-to-speech/{settings.ELEVENLABS_VOICE_ID}?output_format={settings.ELEVENLABS_TTS_OUTPUT_FORMAT}"
    
    headers = {
        "xi-api-key": settings.ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }
    
    data = {
        "text": text,
        "model_id": settings.ELEVENLABS_TTS_MODEL,
    }
    
    async with httpx.AsyncClient(timeout=settings.SPEECH_REQUEST_TIMEOUT_SECONDS) as client:
        try:
            response = await client.post(url, headers=headers, json=data)
            response.raise_for_status()
            return response.content
        except httpx.HTTPStatusError as e:
            error_msg = e.response.text
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"ElevenLabs TTS error: {error_msg}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to synthesize speech: {str(e)}"
            )
