import yt_dlp
import ffmpeg
import pyaudio
import wave
import os
import asyncio

class StreamAudio:
    def __init__(self, youtube_url: str, play_stream: bool = False):
        self.youtube_url = youtube_url
        self.audio_url = self.get_youtube_audio_url(self.youtube_url) if self.youtube_url else exit()
        self.process = None
        self.player = None
        self.stream = None
        self.wav_file = None
        self.play_stream = play_stream
        self.stream_file = None
        if not self.audio_url:
            print("Failed to retrieve audio URL.")
            exit()

        self.setup_stream_directory()
        self.setup_process()

    def stop_stream(self):
        self.process.kill()
        self.wav_file.close()
        if self.play_stream:
            self.stream.stop_stream()
            self.stream.close()
            self.player.terminate()

    def get_youtube_audio_url(self, youtube_url):
        ydl_opts = {
            'format': 'bestaudio',
            'quiet': True,
            'noplaylist': True,
            'extract_flat': False,  # Changed to False to get full info
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=False)
            if 'url' in info:
                return info['url']
            else:
                print("Failed to retrieve audio URL.")
                return None

    async def refresh_audio_url(self):
        while True:
            print("Refreshing audio URL...")
            self.audio_url = self.get_youtube_audio_url(self.youtube_url)
            print("Refreshing the process...")
            self.process = (
            ffmpeg.input(self.audio_url)
            .output('pipe:', format='wav', acodec='pcm_s16le', ac=1, ar='16000')
            .run_async(pipe_stdout=True, pipe_stderr=True)
            )
            await asyncio.sleep(100)
            
    def setup_stream_directory(self):
        if not self.wav_file:
            output_dir = "recorded_audio"
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            output_filename = os.path.join(output_dir, "stream.wav")
            self.wav_file = wave.open(output_filename, 'wb')
            self.wav_file.setnchannels(1)  # Mono
            self.wav_file.setsampwidth(2)  # 2 bytes per sample (16-bit)
            self.wav_file.setframerate(16000)  # 16kHz sample rate
            self.stream_file = output_filename

    def setup_process(self):
        # Stream and process the audio
        self.process = (
            ffmpeg.input(self.audio_url)
            .output('pipe:', format='wav', acodec='pcm_s16le', ac=1, ar='16000')
            .run_async(pipe_stdout=True, pipe_stderr=True)
        )

        if self.play_stream:
            self.player = pyaudio.PyAudio()
            self.stream = self.player.open(
                format=pyaudio.paInt16, 
                channels=1, 
                rate=16000, 
                output=True, 
                frames_per_buffer=1024)

    def stream_audio(self):
        try:
            print("\nStreaming audio...")
            while True:
                in_bytes = self.process.stdout.read(1024 * 200)
                if not in_bytes:
                    print("\nNo more audio to stream.")
                    break
                
                    # Save to WAV file
                    # Write audio to file
                self.wav_file.writeframes(in_bytes)
                
                if self.play_stream:
                    # Play audio
                    self.stream.write(in_bytes)
                    
        except KeyboardInterrupt:
            print("\nStopping stream...")
            # Cleanup
            self.process.kill()
            self.wav_file.close()

            if self.play_stream:
                self.stream.stop_stream()
                self.stream.close()
                self.player.terminate()
        

    