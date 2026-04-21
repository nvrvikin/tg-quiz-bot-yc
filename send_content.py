from aiogram import types
import aiohttp

async def send_video_note(message: types.Message, video_url: str):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(video_url) as resp:
                if resp.status == 200:
                    # Читаем всё содержимое в память
                    video_data = await resp.read()
                    file = types.BufferedInputFile(video_data, filename="circle.mp4")
                    
                    sent = await message.answer_video_note(
                        video_note=file,
                        duration=49,
                        length=600
                    )
                    
                    file_id = sent.video_note.file_id
                    print(f"file_id видео кружочка: {file_id}")
                else:
                    await message.answer("Не удалось загрузить видео")
    except Exception as e:
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
