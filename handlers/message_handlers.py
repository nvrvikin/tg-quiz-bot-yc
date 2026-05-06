from aiogram import Router, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext

from data.constants import MSG_CHOOSE_ACTION, MSG_NICKNAME_TOO_LONG, MSG_NICKNAME_TOO_SHORT, MSG_NICKNAME_UPDATED
from keyboards import generate_main_menu_keyboard
import states
from states import state

from .common_functions import main_menu_state
from service import get_user_state, set_user_state, update_user_nickname
from generate_answer import generate_unhandled_message_answer
from states.state import UserForm

# Init text message router
router = Router()

async def process_nickname(message: types.Message):
    """
    Checks if a message meets the requirements of a nickname and then
    updates user one in the db and changes the state to [main_menu]
    
    :param message: User message object, that conatins message text
    :type message: types.Message
    :param state: Aiogram bot current state of a user chat
    :type state: FSMContext
    """

    username = message.text.strip()
    
    # Validate with max and min string length
    if len(username) > 20:
        await message.answer("Слишком длинный ник! Максимум 20 символов.")
        return
    if len(username) < 3:
        await message.answer("Слишком короткий ник! Минимум 3 символа.")
        return
    
    await update_user_nickname(message.from_user.id, username)
    await message.answer(f"Отлично, { username }!")
    await main_menu_state(message=message, user_id=message.from_user.id)

@router.message
async def handle_text_messages(message: types.Message):
    user_id = message.from_user.id
    current_state = await get_user_state(user_id)
    text = message.text.strip() if message.text else ""

    if current_state in (state.NO_NICKNAME, state.CHANGE_NICKNAME):
        if len(text) > 20:
            await message.answer(MSG_NICKNAME_TOO_LONG)
            return
        if len(text) < 3:
            await message.answer(MSG_NICKNAME_TOO_SHORT)
            return
        await update_user_nickname(user_id, text)
        await message.answer(MSG_NICKNAME_UPDATED.format(nickname=text))
        await set_user_state(user_id, state.MAIN_MENU)
        kb = generate_main_menu_keyboard()
        await message.answer(f"{MSG_CHOOSE_ACTION}, {text}", reply_markup=kb)
        return
    await message.answer(generate_unhandled_message_answer())