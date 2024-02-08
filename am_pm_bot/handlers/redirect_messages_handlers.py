from am_pm_bot import router, bot
from am_pm_bot.handlers import Message
from am_pm_bot.bot_helper.bot_helper import BotHelper

bot_pm = BotHelper(tg_bot=bot)


@router.message()
async def redirect_messages_handler(message: Message) -> None:
    print("MANAGERS:", bot_pm.MANAGER_IDS)
    if message.from_user.id in bot_pm.MANAGER_IDS:
        await bot_pm.send_message_from_manager_to_client(message)
    else:
        await bot_pm.send_message_from_client_to_manager(message)
