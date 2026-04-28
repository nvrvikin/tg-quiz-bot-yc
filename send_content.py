from aiogram import types
from aiogram.types import BufferedInputFile
import aiohttp

async def send_video_note(message: types.Message, video_url: str, duration: int = 49, length: int = 600):
    """
    Sends a video note (circle video) to the user.

    Args:
        message (types.Message): The message object to reply to.
        video_url (str): The URL of the video to send.
        duration (int, optional): Duration of the video note in seconds. Defaults to 49.
        length (int, optional): Diameter of the video note in pixels. Defaults to 600.
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(video_url) as resp:
                if resp.status == 200:
                    # Читаем всё содержимое в память
                    video_data = await resp.read()
                    file = BufferedInputFile(video_data, filename="circle.mp4")
                    
                    sent = await message.answer_video_note(
                        video_note=file,
                        duration=duration,
                        length=length
                    )
                    
                    file_id = sent.video_note.file_id
                    print(f"file_id видео кружочка: {file_id}")
                else:
                    await message.answer("Не удалось загрузить видео")
    except Exception as e:
        print(f"Ошибка при отправке видео: {e}")
        await message.answer(f"Ошибка: {e}")


async def send_voice(message: types.Message, voice_url: str):
    sent_message = await message.answer_voice(
        voice=voice_url
    )

    if sent_message.voice:
        file_id = sent_message.voice.file_id
        print(f"file_id голосового: {file_id}")

async def send_photo(message: types.Message, photo_url: str, caption: str):
    sent_message = await message.answer_photo(
        photo=photo_url,
        caption=f'{caption}'
    )
