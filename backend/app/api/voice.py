import os
import tempfile
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel

router = APIRouter(prefix="/voice", tags=["voice"])


class SpeakRequest(BaseModel):
    text: str
    rate: int = 175
    volume: float = 1.0
    voice: str | None = None


def _transcribe_local(path: str, language: str | None = None) -> dict:
    try:
        from faster_whisper import WhisperModel
    except ImportError as exc:
        raise HTTPException(
            status_code=503,
            detail="Local Whisper is not installed. Run the Phase 2 setup command."
        ) from exc

    model_name = os.getenv("AETHER_WHISPER_MODEL", "base")
    device = os.getenv("AETHER_WHISPER_DEVICE", "cpu")
    compute_type = os.getenv("AETHER_WHISPER_COMPUTE_TYPE", "int8")

    try:
        model = WhisperModel(model_name, device=device, compute_type=compute_type)
        segments, info = model.transcribe(
            path,
            language=language or None,
            vad_filter=True,
            beam_size=5,
        )
        text = " ".join(segment.text.strip() for segment in segments).strip()
        return {
            "text": text,
            "language": info.language,
            "language_probability": info.language_probability,
            "provider": "local-whisper",
            "model": model_name,
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Local transcription failed: {exc}") from exc


@router.post("/transcribe")
async def transcribe(
    audio: UploadFile = File(...),
    language: str | None = None,
):
    suffix = Path(audio.filename or "audio.webm").suffix or ".webm"
    data = await audio.read()
    if not data:
        raise HTTPException(status_code=400, detail="Audio file is empty.")
    if len(data) > 25 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Audio file is too large.")

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(data)
        tmp_path = tmp.name

    try:
        return _transcribe_local(tmp_path, language)
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


@router.post("/speak")
async def speak(payload: SpeakRequest, background_tasks: BackgroundTasks):
    text = payload.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text is empty.")

    try:
        import pyttsx3
    except ImportError as exc:
        raise HTTPException(
            status_code=503,
            detail="Windows TTS is not installed. Run the Phase 2 setup command."
        ) from exc

    output = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    output.close()

    try:
        engine = pyttsx3.init()
        engine.setProperty("rate", max(80, min(payload.rate, 300)))
        engine.setProperty("volume", max(0.0, min(payload.volume, 1.0)))
        if payload.voice:
            for voice in engine.getProperty("voices"):
                if payload.voice.lower() in (voice.id + " " + voice.name).lower():
                    engine.setProperty("voice", voice.id)
                    break
        engine.save_to_file(text, output.name)
        engine.runAndWait()
        engine.stop()
        if not Path(output.name).exists() or Path(output.name).stat().st_size == 0:
            raise RuntimeError("Windows TTS produced no audio.")
        background_tasks.add_task(os.unlink, output.name)
        return FileResponse(
            output.name,
            media_type="audio/wav",
            filename="aether-response.wav",
        )
    except Exception as exc:
        try:
            os.unlink(output.name)
        except OSError:
            pass
        raise HTTPException(status_code=500, detail=f"Windows TTS failed: {exc}") from exc


@router.get("/providers")
def providers():
    return {
        "stt": [{"id": "local-whisper", "name": "Local Whisper", "paid": False}],
        "tts": [{"id": "windows-sapi", "name": "Windows TTS", "paid": False}],
        "wake_word": [{"id": "push-to-talk", "name": "Push to Talk", "paid": False}],
    }
