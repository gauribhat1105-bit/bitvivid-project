import os
from dotenv import load_dotenv
from deepgram import DeepgramClient

load_dotenv()

DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")

# Initialize Deepgram client
deepgram = DeepgramClient(DEEPGRAM_API_KEY)


async def transcribe_audio(audio_bytes: bytes) -> str:

    try:

        print(f"[Deepgram] Audio size: {len(audio_bytes)} bytes")

        # Audio payload
        payload = {
            "buffer": audio_bytes,
            "mimetype": "audio/webm"   # supports browser recordings
        }

        # Improved robust options
        options = {
            "model": "nova-2",
            "smart_format": True,
            "punctuate": True,
            "language": "en-IN",        # Best for Indian English
            "detect_language": False,
            "diarize": False,
            "utterances": False,
            "profanity_filter": False
        }

        # Transcribe
        response = deepgram.listen.prerecorded.v("1").transcribe_file(
            payload,
            options
        )

        transcript = (
            response.results.channels[0]
            .alternatives[0]
            .transcript
        )

        print("[Deepgram] Transcript:", transcript)

        return transcript.strip()

    except Exception as e:

        print("[Deepgram] ERROR:", str(e))

        return ""
