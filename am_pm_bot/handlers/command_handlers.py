from am_pm_bot import router, bot
from am_pm_bot.bot_helper import BotHelper
from am_pm_bot.handlers import CommandStart, Message

bot_pm = BotHelper(tg_bot=bot)


@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await bot_pm.welcome_user(message)
