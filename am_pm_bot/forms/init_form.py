from am_pm_bot.forms import StatesGroup, State


class InitForm(StatesGroup):
    description = State()
    budget = State()
