from am_pm_bot import router, bot
from am_pm_bot.bot_helper import BotHelper
from am_pm_bot.handlers import CallbackQuery, F
from am_pm_bot.callback_data.create_request import CreateRequestCallback

bot_pm = BotHelper(tg_bot=bot)


@router.callback_query(CreateRequestCallback.filter(F.command == "create_request"))
async def create_request_handler(callback_query: CallbackQuery, callback_data: CreateRequestCallback) -> None:
    await bot_pm.ask_request_details(callback_query, callback_data)
    await callback_query.answer()
