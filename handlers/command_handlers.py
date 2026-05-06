from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from service import new_quiz

from .common_functions import check_nickname, main_menu_state
from data.phrases import PHRASE_GREET

# Init command router
router = Router()

# ОБРАБОТКА /start
@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.bot.send_chat_action(message.chat.id, action='typing')
    await message.answer_photo('https://storage.yandexcloud.net/souls-bucket/cover/ds_quiz_cover.png', caption=PHRASE_GREET, parse_mode='HTML')
    user_id = message.from_user.id

    if not await check_nickname(message, user_id):
        return
    
    await main_menu_state(message, user_id)