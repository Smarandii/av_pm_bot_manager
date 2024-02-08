from am_pm_bot.forms import StatesGroup, State


class CreatePaymentTicketForm(StatesGroup):
    amount = State()
    currency = State()
    confirm = State()
