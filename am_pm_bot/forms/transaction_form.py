from am_pm_bot.forms import StatesGroup, State


class getTransactionForm(StatesGroup):
    transaction_hash = State()
    nxtForm = State()