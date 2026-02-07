import whisper
import edge_tts
import asyncio
import pyaudio
import wave
import tempfile
import os


class VoiceHandler:
    """Handles speech-to-text (Whisper) and text-to-speech (Edge TTS).

    STT: Records audio from the microphone, saves to a temp WAV file,
    and transcribes with OpenAI Whisper (local, offline).

    TTS: Converts text to speech using Microsoft Edge TTS (free, online),
    saves to a temp MP3, and plays it with the system audio player.
    """

    def __init__(self):
        print("Loading Whisper...")
        # "base" model is a good balance of speed vs accuracy (~150MB)
        self.whisper_model = whisper.load_model("base")
        # Edge TTS voice — AriaNeural is clear and natural-sounding
        self.tts_voice = "en-US-AriaNeural"

    def listen(self, duration: int = 5) -> str:
        """Record audio from the microphone and transcribe with Whisper.

        Args:
            duration: Seconds to record (default 5).

        Returns:
            Transcribed text string.
        """
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 16000

        p = pyaudio.PyAudio()

        print("🎤 Listening...")
        stream = p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK,
        )

        frames = []
        for _ in range(0, int(RATE / CHUNK * duration)):
            data = stream.read(CHUNK)
            frames.append(data)

        stream.stop_stream()
        stream.close()
        p.terminate()

        # Write recorded audio to a temp WAV file for Whisper
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
            wf = wave.open(temp_audio.name, "wb")
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(p.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b"".join(frames))
            wf.close()

            result = self.whisper_model.transcribe(temp_audio.name)
            os.unlink(temp_audio.name)

        return result["text"]

    async def speak(self, text: str):
        """Convert text to speech using Edge TTS and play it.

        Uses afplay (macOS) for audio playback.
        """
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_tts:
            communicate = edge_tts.Communicate(text, self.tts_voice)
            await communicate.save(temp_tts.name)

            # afplay is the built-in macOS audio player
            os.system(f"afplay {temp_tts.name}")
            os.unlink(temp_tts.name)
