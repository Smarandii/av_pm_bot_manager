from am_pm_bot import Bot, WEBHOOK_HOST, WEBHOOK_PATH, WEBHOOK_SECRET


async def on_startup(bot: Bot) -> None:
    """
    Set webhook upon bot startup.
    """
    await bot.send_message(chat_id=231584958, text='Bot has been started ' + f"{WEBHOOK_HOST}{WEBHOOK_PATH}")
    await bot.set_webhook(f"{WEBHOOK_HOST}{WEBHOOK_PATH}", secret_token=WEBHOOK_SECRET, drop_pending_updates=True)


async def on_shutdown(bot: Bot) -> None:
    """
    Set webhook upon bot stop.
    """
    await bot.send_message(chat_id=231584958, text='Bot has been stopped')
    await bot.delete_webhook(drop_pending_updates=True)
