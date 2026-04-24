from aiogram.fsm.state import State, StatesGroup

class UserForm(StatesGroup):
    no_nickname = State()
    change_nickname = State()
    main_menu = State()
    quiz = State()
    results_menu = State()
    results_top = State()