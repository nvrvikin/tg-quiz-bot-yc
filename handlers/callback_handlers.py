"""
from aiogram import F, Router, types
from aiogram.filters import StateFilter


from .common_functions import check_nickname, main_menu_state
from data.callbacks import CB_CANCEL, CB_RESULTS_MENU, CB_RESULTS_TOP, CB_START_QUIZ
from service import check_question_answer, get_question, get_user, get_top_results, get_user_nickname, new_quiz


from keyboards import generate_change_nickname_keyboard, generate_results_menu_keyboard, generate_results_top_keyboard

from states.state import UserForm
"""
from aiogram import F, Router, types
from aiogram.exceptions import TelegramBadRequest
from data.callbacks import CB_CANCEL, CB_RESULTS_MENU, CB_RESULTS_TOP, CB_START_QUIZ
from data.constants import MSG_BUTTON_NOT_ACTIVE, MSG_QUIZ_NOT_ACTIVE, MSG_NOT_IN_QUIZ
from handlers.common_functions import check_nickname, main_menu_state
from service import (
    get_user_state, set_user_state, clear_user_state,
    check_question_answer, get_question, new_quiz,
    get_top_results, get_user, get_user_nickname
)
from keyboards import (
    generate_change_nickname_keyboard, generate_results_menu_keyboard, generate_results_top_keyboard,
    generate_main_menu_keyboard
)
from states import state

router = Router()

# STATE TRANSITIONS
async def change_nickname_state(message: types.Message, user_id: int):
    await set_user_state(user_id, state.CHANGE_NICKNAME)
    current_nickname = await get_user_nickname(user_id)
    kb = generate_change_nickname_keyboard()
    await message.answer(f'Текущий никнейм: <b>{ current_nickname }</b>. Если хотите изменить, напишите мне новый никнейм.', reply_markup=kb, parse_mode='HTML')

async def quiz_state(message: types.Message, user_id: int):
    await set_user_state(user_id, state.QUIZ)
    await message.answer(f"Начинаем квиз!")
    await new_quiz(message, user_id)

async def resluts_menu_state(callback: types.CallbackQuery):
    await set_user_state(callback.from_user.id, state.RESULTS_MENU)
    kb = generate_results_menu_keyboard()
    user_id = callback.from_user.id
    message = await get_user(user_id)
    nickname = await get_user_nickname(user_id)
    await callback.message.answer(f'<b>Меню результатов</b>\n{ nickname }{ message }', reply_markup=kb, parse_mode='HTML')

async def resluts_top_state(callback: types.CallbackQuery):
    await set_user_state(callback.from_user.id, state.RESULTS_TOP)
    kb = generate_results_top_keyboard()
    message = await get_top_results()
    await callback.message.answer(f'{ message }', reply_markup=kb, parse_mode='HTML')

async def clear_markup(callback: types.CallbackQuery):
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )

async def change_question_text(callback: types.CallbackQuery):
    await callback.bot.edit_message_text(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        text=f'{callback.message.text}\n\nОтвет:', 
        reply_markup=None
    )

async def handle_quiz_answer(callback: types.CallbackQuery):
    #await clear_markup(callback)

    user_id = callback.from_user.id

    # Проверка наличия никнейма
    if not await check_nickname(message=callback.message, user_id=user_id):
        return
    await check_question_answer(callback, user_id)
    #await callback.message.answer(result_answer, parse_mode="HTML")
    has_question = await get_question(callback.message, user_id)
    if not has_question:
        # End quiz
        await main_menu_state(message=callback.message, user_id=user_id)

    
async def cancel(callback: types.CallbackQuery):
    await clear_markup(callback)
    await main_menu_state(message=callback.message, user_id=callback.from_user.id)


# ON CANCEL CALLBACK
@router.callback_query(F.data == CB_CANCEL)
async def allowed_cancel(callback: types.CallbackQuery):
    current_state = await get_user_state(callback.from_user.id)
    if not current_state in [state.CHANGE_NICKNAME, state.QUIZ, state.RESULTS_MENU, state.RESULTS_TOP]:
        await clear_markup(callback)
        await callback.answer(MSG_BUTTON_NOT_ACTIVE, show_alert=True)
        return
    await cancel(callback)

# ОБРАБОТКА CB_START_QUIZ
@router.callback_query(F.data == CB_START_QUIZ)
async def cmd_quiz(callback: types.CallbackQuery):
    current_state = await get_user_state(callback.from_user.id)
    if not current_state == state.MAIN_MENU:
        return
    
    await clear_markup(callback)

    user_id = callback.from_user.id
    has_nickname = await check_nickname(message=callback.message, user_id=user_id)
    if not has_nickname:
        return
    
    await quiz_state(message=callback.message, user_id=user_id)
# ОБРАБОТКА ОТВЕТОВ НА ВОПРОСЫ КВИЗА
@router.callback_query(F.data.in_(['0', '1', '2', '3', '4']))
async def quiz_answer(callback: types.CallbackQuery):
    current_state = await get_user_state(callback.from_user.id)
    if not current_state == state.QUIZ:
        await callback.answer(MSG_BUTTON_NOT_ACTIVE, show_alert=True)
        return
    await handle_quiz_answer(callback)

# Кнопка меню результатов
@router.callback_query(F.data == CB_RESULTS_MENU)
async def results_menu(callback: types.CallbackQuery):
    current_state = await get_user_state(callback.from_user.id)
    if not current_state in [state.MAIN_MENU, state.RESULTS_TOP]:
        await callback.answer(MSG_BUTTON_NOT_ACTIVE, show_alert=True)
        return
    await clear_markup(callback)
    await resluts_menu_state(callback, state)

# Кнопка топа результатов
@router.callback_query(F.data == CB_RESULTS_TOP)
async def results_top(callback: types.CallbackQuery):
    current_state = await get_user_state(callback.from_user.id)
    if not current_state == state.RESULTS_MENU:
        await callback.answer(MSG_BUTTON_NOT_ACTIVE, show_alert=True)
        return
    await clear_markup(callback)
    await resluts_top_state(callback)



    