from aiogram import F, Router, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext

from .common_functions import check_nickname, main_menu_state
from data.callbacks import CB_CANCEL, CB_RESULTS_MENU, CB_RESULTS_TOP, CB_START_QUIZ
from service import check_question_answer, get_question, get_user, get_top_results, get_user_nickname, new_quiz


from keyboards import generate_change_nickname_keyboard, generate_results_menu_keyboard, generate_results_top_keyboard

from states.state import UserForm

router = Router()



# STATE TRANSITIONS
async def change_nickname_state(message: types.Message, user_id: int, state: FSMContext):
    await state.set_state(UserForm.change_nickname)
    current_nickname = await get_user_nickname(user_id)
    kb = generate_change_nickname_keyboard()
    await message.answer(f'Текущий никнейм: <b>{ current_nickname }</b>. Если хотите изменить, напишите мне новый никнейм.', reply_markup=kb, parse_mode='HTML')

async def quiz_state(message: types.Message, user_id: int, state: FSMContext):
    await state.set_state(UserForm.quiz)
    await message.answer(f"Начинаем квиз!")
    await new_quiz(message)

async def resluts_menu_state(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(UserForm.results_menu)
    kb = generate_results_menu_keyboard()
    user_id = callback.from_user.id
    message = await get_user(user_id)
    nickname = await get_user_nickname(user_id)
    await callback.message.answer(f'<b>Меню результатов</b>\n{ nickname }{ message }', reply_markup=kb, parse_mode='HTML')

async def resluts_top_state(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(UserForm.results_top)
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

async def handle_quiz_answer(callback: types.CallbackQuery, state: FSMContext):
    await clear_markup(callback)

    user_id = callback.from_user.id

    # Проверка наличия никнейма
    if not await check_nickname(message=callback.message, user_id=user_id, state=state):
        return
    await check_question_answer(callback, user_id)
    #await callback.message.answer(result_answer, parse_mode="HTML")
    has_question = await get_question(callback.message, user_id)
    if not has_question:
        # End quiz
        await main_menu_state(message=callback.message, user_id=user_id, state=state)


async def cancel(callback: types.CallbackQuery, state: FSMContext):
    await main_menu_state(message=callback.message, user_id=callback.from_user.id, state=state)


# ON CANCEL CALLBACK IN ALLOWED STATES
@router.callback_query(StateFilter(
        UserForm.change_nickname,
        UserForm.quiz,
        UserForm.results_menu,
        UserForm.results_top,
    ),
    F.data == CB_CANCEL
)
async def allowed_cancel(callback: types.CallbackQuery, state: FSMContext):
    await clear_markup(callback)
    await cancel(callback, state)

# ON CANCEL CALLBACK IN OTHER STATES
@router.callback_query(F.data == CB_CANCEL)
async def other_states_cancel(callback: types.CallbackQuery):
    await clear_markup(callback)
    await callback.answer('Отмена не поддерживается в текущем состоянии диалога', show_alert=True)

# ОБРАБОТКА CB_START_QUIZ
@router.callback_query(UserForm.main_menu, F.data == CB_START_QUIZ)
async def cmd_quiz(callback: types.CallbackQuery, state: FSMContext):
    await clear_markup(callback)

    user_id = callback.from_user.id
    has_nickname = await check_nickname(message=callback.message, user_id=user_id, state=state)
    if not has_nickname:
        return
    
    await quiz_state(message=callback.message, user_id=user_id, state=state)

# ОБРАБОТКА ОТВЕТОВ НА ВОПРОСЫ КВИЗА
@router.callback_query(UserForm.quiz, F.data.in_(['0', '1', '2', '3', '4']))
async def quiz_answer(callback: types.CallbackQuery, state: FSMContext):
    await handle_quiz_answer(callback, state)

# Кнопка меню результатов
@router.callback_query(StateFilter(UserForm.main_menu, UserForm.results_top), F.data == CB_RESULTS_MENU)
async def results_menu(callback: types.CallbackQuery, state: FSMContext):
    await clear_markup(callback)
    await resluts_menu_state(callback, state)

# Кнопка топа результатов
@router.callback_query(UserForm.results_menu, F.data == CB_RESULTS_TOP)
async def results_menu(callback: types.CallbackQuery, state: FSMContext):
    await clear_markup(callback)
    await resluts_top_state(callback, state)

    