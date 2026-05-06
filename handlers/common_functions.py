from aiogram.fsm.context import FSMContext
from aiogram import F, types

from data.constants import MSG_CURRENT_NICKNAME
from keyboards import generate_change_nickname_keyboard
from service import get_user_nickname, set_user_state
from generate_answer import show_main_menu
from states import state


async def check_nickname(message: types.Message, user_id: int):
    """Checks if user has a nickname in the db, if not - sends message with requirements and sets state to [no_nickname]

    :param message: User message object, that conatins message text
    :type message: types.Message
    :param user_id: User id in Telegram. Takes it separately for convinience of calling this function from different handlers like callback handler, where Message object gives wrong user_id.
    :type user_id: int
    :param state: FSM context
    :type state: FSMContext
    
    :return: True if user has a nickname, False if not
    :rtype: bool
    """
    nickname = await get_user_nickname(user_id)
    if not nickname:
        await set_user_state(user_id, state.NO_NICKNAME)
        await no_nickname_state(message)
        kb = generate_change_nickname_keyboard()
        await message.answer(MSG_CURRENT_NICKNAME.format(nickname="не задан"), reply_markup=kb)
        return False
    return True

async def no_nickname_state(message: types.Message):
    await message.bot.send_chat_action(message.chat.id, action='typing')
    await set_user_state(message.from_user.id, state.NO_NICKNAME)
    await message.answer('Требуется придумать ник от 3 до 20 символов для отображения в общих результатах')

async def main_menu_state(message: types.Message, user_id: int):
    await message.bot.send_chat_action(message.chat.id, action='typing')
    nickname = await get_user_nickname(user_id)
    print(nickname)
    await set_user_state(user_id, state.MAIN_MENU)
    await show_main_menu(message, nickname)

async def end_quiz(message: types.Message, user_id: int, results: str):
    await message.answer(f"Это был последний вопрос. Квиз завершен! { results }", parse_mode="HTML")
    await main_menu_state(message=message, user_id=user_id)