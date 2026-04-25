from aiogram.fsm.context import FSMContext
from aiogram import F, types

from service import get_user_nickname
from generate_answer import show_main_menu
from states.state import UserForm


async def check_nickname(message: types.Message, user_id: int, state: FSMContext):
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
    if not await get_user_nickname(user_id):
        await no_nickname_state(message, state)
        return False
    return True

async def no_nickname_state(message: types.Message, state: FSMContext):
    await message.bot.send_chat_action(message.chat.id, action='typing')
    await state.set_state(UserForm.no_nickname)
    await message.answer('Требуется придумать ник от 3 до 20 символов для отображения в общих результатах')

async def main_menu_state(message: types.Message, user_id: int, state: FSMContext):
    await message.bot.send_chat_action(message.chat.id, action='typing')
    nickname = await get_user_nickname(user_id)
    print(nickname)
    await state.set_state(UserForm.main_menu)
    await show_main_menu(message, nickname)

async def end_quiz(message: types.Message, user_id: int, state: FSMContext, results: str):
    await message.answer(f"Это был последний вопрос. Квиз завершен! { results }", parse_mode="HTML")
    await main_menu_state(message=message, user_id=user_id, state=state)