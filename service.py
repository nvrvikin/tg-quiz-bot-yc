import json

from database import pool, execute_update_query, execute_select_query
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram import types

from keyboards import generate_options_keyboard

async def get_results(user_id):
    get_results_query = f"""
        DECLARE $user_id AS Uint64;

        SELECT *
        FROM `users`
        WHERE user_id == $user_id;
    """
    results = execute_select_query(pool, get_results_query, user_id=user_id)
    return results

async def get_top_results():
    get_top_results_query = f"""
        SELECT user_id, nickname, user_points
        FROM `users`
        ORDER BY user_points DESC
        LIMIT 10;
    """
    results = execute_select_query(pool, get_top_results_query)
    return results

async def update_quiz_results(user_id, user_points):
    update_quiz_results_query = f"""
        DECLARE $user_id AS Uint64;
        DECLARE $user_points AS Uint64;

        UPSERT INTO `users` (`user_id`, `user_points`)
        VALUES ($user_id, $user_points);
    """
    execute_update_query(pool, update_quiz_results_query, user_id=user_id, user_points=user_points)

async def get_user_nickname(user_id):
    get_user_nickname_query = f"""
        DECLARE $user_id AS Uint64;

        SELECT nickname
        FROM `users`
        WHERE user_id == $user_id;
    """
    results = execute_select_query(pool, get_user_nickname_query, user_id=user_id)

    if len(results) == 0:
        return None

    return results[0]["nickname"]

async def update_user_nickname(user_id, nickname):
    update_user_nickname_query = f"""
        DECLARE $user_id AS Uint64;
        DECLARE $nickname AS String;

        UPDATE `users`
        SET nickname = $nickname
        WHERE user_id == $user_id;
    """
    execute_update_query(pool, update_user_nickname_query, user_id=user_id, nickname=nickname)

async def get_question(message, user_id):
    # Получение текущего вопроса из словаря состояний пользователя
    current_question_index = await get_quiz_index(user_id)
    print(current_question_index)
    questions = await get_questions()
    if not len(questions):
        await message.answer('Нет вопросов')
        return
    
    is_q_found = False
    q_text = ''
    q_options = []
    current_question = None
    for q in questions:
        if q['order_index'] == current_question_index:
            is_q_found = True
            current_question = q

    if not is_q_found:
        await message.answer('Вопрос не найден')
        return
    
    kb = generate_options_keyboard(json.loads(current_question['options']))
    await message.answer(f'{current_question["question_text"].decode("utf-8")}', reply_markup=kb)


async def new_quiz(message):
    user_id = message.from_user.id
    current_question_index = 1
    await update_quiz_index(user_id, current_question_index)
    await get_question(message, user_id)


async def get_quiz_index(user_id):
    get_user_index = f"""
        DECLARE $user_id AS Uint64;

        SELECT question_index
        FROM `users`
        WHERE user_id == $user_id;
    """
    results = execute_select_query(pool, get_user_index, user_id=user_id)

    if len(results) == 0:
        return 0
    if results[0]["question_index"] is None:
        return 0
    return results[0]["question_index"]    

async def update_quiz_index(user_id, question_index):
    set_quiz_state = f"""
        DECLARE $user_id AS Uint64;
        DECLARE $question_index AS Uint64;

        UPSERT INTO `users` (`user_id`, `question_index`)
        VALUES ($user_id, $question_index);
    """

    execute_update_query(
        pool,
        set_quiz_state,
        user_id=user_id,
        question_index=question_index,
    )
    
async def get_questions():
    get_questions_query = f"""
        SELECT *
        FROM `questions`
    """
    results = execute_select_query(
        pool,
        get_questions_query
    )

    if len(results) == 0:
        return 0

    return results
