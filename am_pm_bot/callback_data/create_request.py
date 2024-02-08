from am_pm_bot.callback_data import CallbackData


class BaseCallback(CallbackData, prefix="av_pm"):
    command: str
    user_id: int
