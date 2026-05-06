from random import randint
from aiogram import types
from data.constants import CORRECT_PHRASES, UNHANDLED_MESSAGES_PHRASES, WRONG_PHRASES, PRE_WRONG_PHRASE, EMOJI_CORRECT, EMOJI_WRONG
from keyboards import generate_main_menu_keyboard


def generate_correct_answer(user_answer):
    rand_answer = randint(0, len(CORRECT_PHRASES) - 1)
    return f"{ EMOJI_CORRECT } <i>{ CORRECT_PHRASES[rand_answer] }</i>\n<u>{ user_answer }</u>"

def generate_wrong_answer(user_answer):
    rand_answer = randint(0, len(WRONG_PHRASES) - 1)
    return f"{ EMOJI_WRONG } <i>{ WRONG_PHRASES[rand_answer] }</i>\n{ PRE_WRONG_PHRASE } <u>{ user_answer }</u>"

def generate_unhandled_message_answer():
    '''
    Returns a random answer string for cases of unhandled iser messages
    '''
    rand_answer = randint(0, len(UNHANDLED_MESSAGES_PHRASES) - 1)
    return f'{ UNHANDLED_MESSAGES_PHRASES[rand_answer] }'
    

def generate_results_list(results):
    '''
    Returns a list 
    
    :param results: An array of tuples of the following format: (user_id: int, question_index: int, answer_index: int).
    They are rows of quiz_results table.
    '''
    if not len(results):
        return 'Нет результатов, пройдите тест ещё раз.'
    response = '\n\n<b>Твой результат:</b>\n'
    for r in results:
        # Пробелы, чтобы выглядело ровнее
        human_count = r[1] + 1
        digit = f'{ human_count }  ' if human_count < 10 else f'{ human_count }'
        # Обозначаем эмодзи в зависимости от ответа
        response += f'{ digit } - { EMOJI_CORRECT if r[2] > 0 else EMOJI_WRONG }\n'
    return response

async def generate_top_results_list(results, get_user_nickname):
    if not len(results):
        return 'Нет топа. Похоже, ещё никто не прошёл квиз.'
    
    user_scores = {}

    for r in results:
        if r[0] not in user_scores:
            user_scores[r[0]] = r[2]
        else:
            user_scores[r[0]] += r[2]
            pass
    
    sorted_users = sorted(user_scores.items(), key=lambda x: x[1], reverse=True)

    results_list = ''

    for u in sorted_users:
        nickname = await get_user_nickname(u[0])
        if nickname:
            results_list += f'<i>{ nickname }</i>: { u[1] }\n'

    response = '<b>Топ результатов:</b>\n\n'
    return f'{response}{results_list}'

async def show_main_menu(message: types.Message, nickname: str):
    kb = generate_main_menu_keyboard()
    await message.answer(f"<b>{ nickname }</b>, на ваш выбор:", parse_mode="HTML", reply_markup=kb)