from am_pm_bot.callback_data import CallbackData


class PaymentTicketCallback(CallbackData, prefix="av_pm"):
    command: str
    currency: str
    amount: float
    telegram_id: int
