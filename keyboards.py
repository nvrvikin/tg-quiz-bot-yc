from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types

from data.callbacks import CB_CANCEL, CB_RESULTS_MENU, CB_RESULTS_TOP, CB_START_QUIZ, CB_CHANGE_NICKNAME

# Клавиатура с вариантами ответа на вопрос
def generate_options_keyboard(answer_options):
    builder = InlineKeyboardBuilder()

    for key, value in answer_options.items():
        builder.add(types.InlineKeyboardButton(
            text = f'{key}. {value}',
            callback_data = f'{key}')
        )

    builder.adjust(1)
    return builder.as_markup()

def generate_main_menu_keyboard():
    builder = InlineKeyboardBuilder()

    builder.add(types.InlineKeyboardButton(
        text='Начать игру',
        callback_data=CB_START_QUIZ
    ))

    builder.add(types.InlineKeyboardButton(
        text='Изменить никнейм',
        callback_data=CB_CHANGE_NICKNAME
    ))

    builder.add(types.InlineKeyboardButton(
        text='Посмотреть результаты',
        callback_data=CB_RESULTS_MENU
    ))

    builder.adjust(1)

    return builder.as_markup()

def generate_change_nickname_keyboard():
    builder = InlineKeyboardBuilder()

    builder.add(types.InlineKeyboardButton(
        text='Отмена',
        callback_data=CB_CANCEL
    ))

    return builder.as_markup()

def generate_results_menu_keyboard():
    builder = InlineKeyboardBuilder()

    builder.add(types.InlineKeyboardButton(
        text='Топ результатов',
        callback_data=CB_RESULTS_TOP
    ))

    builder.add(types.InlineKeyboardButton(
        text='Назад',
        callback_data=CB_CANCEL
    ))

    builder.adjust(1)

    return builder.as_markup()

def generate_results_top_keyboard():
    builder = InlineKeyboardBuilder()

    builder.add(types.InlineKeyboardButton(
        text='Мои результаты',
        callback_data=CB_RESULTS_MENU
    ))

    builder.add(types.InlineKeyboardButton(
        text='Главное меню',
        callback_data=CB_CANCEL
    ))

    builder.adjust(1)

    return builder.as_markup()