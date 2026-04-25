from aiogram import types
from aiogram.fsm.context import FSMContext
from handlers.common_functions import main_menu_state


async def end_quiz(message: types.Message, user_id: int, state: FSMContext, results: str):
    await message.answer(f"Это был последний вопрос. Квиз завершен! { results }", parse_mode="HTML")
    await main_menu_state(message=message, user_id=user_id, state=state)