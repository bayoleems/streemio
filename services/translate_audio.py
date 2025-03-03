import whisper
import numpy as np
import asyncio
from googletrans import Translator


class TranslateAudio:
    def __init__(self, stream_file="recorded_audio/stream.wav"):
        self.model = whisper.load_model("medium")
        self.translator = Translator()
        self.stream_file = stream_file
        self.last_position = 0
        self.languages = {
            "French": "fr",
            "English": "en",
            "Spanish": "es",
            "German": "de",
            "Italian": "it",
            "Portuguese": "pt",
            "Russian": "ru",
            "Chinese": "zh-cn",
            "Japanese": "ja",
            "Korean": "ko",
            "Arabic": "ar",
            "Dutch": "nl",
            "Swedish": "sv",
            "Norwegian": "no",
            "Danish": "da",
            "Finnish": "fi",
            "Greek": "el",
            "Hebrew": "he",
            "Hungarian": "hu",
            "Indonesian": "id",
            "Korean": "ko",
            "Norwegian": "no",
            "Polish": "pl",
            "Romanian": "ro",
            "Turkish": "tr",
            "Ukrainian": "uk",
            "Vietnamese": "vi"
        }

    def transcribe_audio(self, audio_bytes):
        """
        Convert raw audio bytes to transcribed text using Whisper.
        """
        # Convert bytes to NumPy array
        audio_np = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0
        
        # Transcribe speech
        result = self.model.transcribe(audio_np)
        text = result["text"]
        print(f"English: {text}\n")
        return text
    
    async def translate_text(self, text, target_language):
        """
        Translate transcribed text to the target language.
        """
        translated_text = await self.translator.translate(text, dest=self.languages[target_language])
        print(f"{target_language}: {translated_text.text}\n")
        return translated_text.text
    
    async def process_audio(self, audio_bytes, target_language):
        text = self.transcribe_audio(audio_bytes)
        translated_text = await self.translate_text(text, target_language)
        
        return translated_text

    async def process_stream_loop(self, target_language="French"):
        while True:
            with open(self.stream_file, "rb") as file:
                # Store last processed position
                file.seek(self.last_position)
                audio_chunk = file.read()
                if audio_chunk:
                    await self.process_audio(audio_chunk, target_language)
                    # Update last processed position
                    self.last_position = file.tell()
                    await asyncio.sleep(1)  # Add small delay between processing
