from am_pm_bot.callback_data import CallbackData


class CreateRequestCallback(CallbackData, prefix="av_pm"):
    command: str
    user_id: int
