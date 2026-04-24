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
async def cmd_start(message: types.Message, state: FSMContext):
    await message.answer(PHRASE_GREET)
    user_id = message.from_user.id

    if not await check_nickname(message, user_id, state):
        return
    
    await main_menu_state(message, user_id, state)

@router.message(Command("quiz"))
async def cmd_quiz(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    #if not await check_nickname(message, user_id, state):
    #    return
    
    await new_quiz(message, user_id)