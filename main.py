from services.translate_audio import TranslateAudio
from services.stream_audio import StreamAudio
import asyncio

stream_audio = StreamAudio(
    # youtube_url="https://www.youtube.com/watch?v=b3EynviZh_Y",
    youtube_url="https://www.youtube.com/watch?v=gCNeDWCI0vo",
    play_stream=True
    )

translate_audio = TranslateAudio(
    stream_file=str(stream_audio.stream_file)
    )
loop = asyncio.get_event_loop()


async def run():
    # Create tasks for both functions
    stream_task = loop.run_in_executor(None, stream_audio.stream_audio)
    refresh_task = stream_audio.refresh_audio_url()
    process_task = translate_audio.process_stream_loop()
    
    # Run both tasks concurrently
    # await asyncio.gather(process_task, stream_task)

    await asyncio.gather(process_task, stream_task, refresh_task)


loop.run_until_complete(run())
