import json

from database import pool, execute_update_query, execute_select_query
from aiogram import types

from generate_answer import generate_correct_answer, generate_wrong_answer
from keyboards import generate_options_keyboard
from send_content import send_video_note

async def get_user(user_id: int):
    get_user_query = f"""
        DECLARE $user_id AS Uint64;

        SELECT *
        FROM `users`
        WHERE user_id == $user_id;
    """
    results = execute_select_query(pool, get_user_query, user_id=user_id)
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

async def add_quiz_results(user_id: int, user_points: int):
    user = await get_user(user_id)
    if not user or len(user) == 0:
        print(f"User not found: {user_id}")
        print(f"Adding new user with points: {user_points}")
        print(f"Got user: {user}")
        return
    print(f"Current user points: {user[0]['user_points']}")
    current_points = user[0]['user_points'] if user[0]['user_points'] is not None else 0
    new_points = current_points + user_points
    update_quiz_results_query = f"""
        DECLARE $user_id AS Uint64;
        DECLARE $user_points AS Uint64;

        UPSERT INTO `users` (`user_id`, `user_points`)
        VALUES ($user_id, $user_points);
    """
    execute_update_query(pool, update_quiz_results_query, user_id=user_id, user_points=new_points)

async def update_quiz_results(user_id: int, user_points: int):
    update_quiz_results_query = f"""
        DECLARE $user_id AS Uint64;
        DECLARE $user_points AS Uint64;

        UPSERT INTO `users` (`user_id`, `user_points`)
        VALUES ($user_id, $user_points);
    """
    execute_update_query(pool, update_quiz_results_query, user_id=user_id, user_points=user_points)

async def get_user_nickname(user_id: int):
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

async def update_user_nickname(user_id: int, nickname: str):
    update_user_nickname_query = f"""
        DECLARE $user_id AS Uint64;
        DECLARE $nickname AS Utf8;

        UPDATE `users`
        SET nickname = $nickname
        WHERE user_id == $user_id;
    """
    execute_update_query(pool, update_user_nickname_query, user_id=user_id, nickname=nickname)

async def get_question(message: types.Message, user_id: int):
    # Получение текущего вопроса из словаря состояний пользователя
    current_question_index = await get_quiz_index(user_id)
    print(current_question_index)
    questions = await get_questions()
    if not len(questions):
        await message.answer('Нет вопросов')
        return False

    if len(questions) <= current_question_index:
        user = await get_user(user_id)
        results = f"Ваш результат: { user[0]['user_points'] if user[0]['user_points'] is not None else 0 } очков."
        await message.answer(f"Это был последний вопрос. Квиз завершен! { results }", parse_mode="HTML")
        return False

    current_question = questions[current_question_index]

    if current_question['has_question_image']:
        await message.bot.send_chat_action(message.chat.id, action='upload_photo')
        await message.answer_photo(current_question['question_image_link'])

    if current_question['has_question_video']:
        await message.bot.send_chat_action(message.chat.id, action='upload_video')
        await send_video_note(message, current_question['question_video_link'], current_question['question_video_duration'], current_question['question_video_length'])

    if current_question['has_question_voice']:
        await message.bot.send_chat_action(message.chat.id, action='upload_voice')
        await message.answer_voice(current_question['question_voice_link'])

    kb = generate_options_keyboard(json.loads(current_question['options']))
    await message.answer(f'{current_question["question_text"].decode("utf-8")}', parse_mode='HTML', reply_markup=kb)

    return True

async def check_question_answer(callback: types.CallbackQuery, user_id: int):
    current_question_index = await get_quiz_index(user_id)
    questions = await get_questions()
    print(f"Current question index: {current_question_index}")
    print(f"Questions count: { len(questions) }")
    if not len(questions):
        return False
    print(f"Questions: { questions }")

    if len(questions) <= current_question_index:
        print(f"No more questions. Current question index: {current_question_index}, questions count: { len(questions) }")
        return False
    
    current_question = questions[current_question_index]
    print(f"Current question: { current_question }")
    print(f"User answer index: {callback.data}")
    print(f"INT User answer index: {int(callback.data)}")
    print(f"Correct answer index: {current_question['correct_option']}")
    correct_option_index = current_question['correct_option']
    user_answer_index = int(callback.data)

    result_answer = ''
    if user_answer_index == correct_option_index:
        result_answer = generate_correct_answer(current_question['options'][user_answer_index])
        await add_quiz_results(user_id, 1)
        # Image
        if current_question['has_answer_image']:
            await callback.bot.send_chat_action(callback.from_user.id, action='upload_photo')
            await callback.message.answer_photo(current_question['answer_image_link'])
        # Video note
        if  current_question['has_answer_video']:
            await callback.bot.send_chat_action(callback.from_user.id, action='upload_video')
            await send_video_note(callback.message, current_question['answer_video_link'], current_question['answer_video_duration'], current_question['answer_video_length'])
        # Voice message        
        if current_question['has_answer_voice']:
            await callback.bot.send_chat_action(callback.from_user.id, action='upload_voice')
            await callback.message.answer_voice(current_question['answer_voice_link'])
    else:
        print(f"User answer index: {user_answer_index}")
        result_answer = generate_wrong_answer(current_question['options'][user_answer_index])

    

    current_question_index += 1
    await update_quiz_index(user_id, current_question_index)
    
    await callback.bot.edit_message_text(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        text=f'{callback.message.text}\n\nОтвет:', 
        reply_markup=None
    )

    await callback.message.answer(result_answer, parse_mode='HTML')

async def new_quiz(message: types.Message, user_id: int):
    current_question_index = 0
    await update_quiz_index(user_id, current_question_index)
    await get_question(message, user_id)


async def get_quiz_index(user_id: int):
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

async def update_quiz_index(user_id: int, question_index: int):
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

def decode_question(row):
    """Превращает байтовые поля вопроса в обычные строки"""
    for key, value in row.items():
        if isinstance(value, bytes):
            row[key] = value.decode('utf-8')
    return row    

async def get_questions():
    get_questions_query = f"""
        SELECT *
        FROM `questions`
        WHERE is_active = TRUE
        ORDER BY order_index ASC
    """
    results = execute_select_query(
        pool,
        get_questions_query
    )

    if not results:
        return []
    
    return [decode_question(row) for row in results]
