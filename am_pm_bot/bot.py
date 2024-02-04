from __init__ import (router, CommandStart, Message, hbold, types, Bot,
                      WEBAPP_HOST, WEBAPP_PORT, WEBHOOK_PATH, WEBHOOK_SECRET, WEBHOOK_HOST,
                      web, setup_application, SimpleRequestHandler, TOKEN, Dispatcher, ParseMode)


@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler will be called when user sends `/start` command
    """
    await message.answer(f"Hello, {hbold(message.from_user.full_name)}!")


@router.message()
async def echo_handler(message: types.Message) -> None:
    """
    Echoes back any received message.
    """
    await message.answer(message.text)


async def on_startup(bot: Bot) -> None:
    """
    Set webhook upon bot startup.
    """
    await bot.send_message(chat_id=231584958, text='Bot has been started')
    await bot.set_webhook(f"{WEBHOOK_HOST}{WEBHOOK_PATH}", secret_token=WEBHOOK_SECRET)


async def on_shutdown(bot: Bot) -> None:
    """
    Set webhook upon bot stop.
    """
    await bot.send_message(chat_id=231584958, text='Bot has been stopped')
    await bot.set_webhook(f"{WEBHOOK_HOST}{WEBHOOK_PATH}", secret_token=WEBHOOK_SECRET)


def main() -> None:
    """
    Main function to start the aiohttp web server.
    """
    # Initialize Bot and Dispatcher
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher()
    dp.include_router(router)

    # Register startup and shutdown hook
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    # Create aiohttp web application
    app = web.Application()

    # Setup request handler for webhook
    webhook_request_handler = SimpleRequestHandler(dispatcher=dp, bot=bot, secret_token=WEBHOOK_SECRET)
    webhook_request_handler.register(app, path=WEBHOOK_PATH)

    # Setup aiohttp application with dispatcher and bot
    setup_application(app, dp, bot=bot)

    # Start webserver
    web.run_app(app, host=WEBAPP_HOST, port=WEBAPP_PORT)


if __name__ == "__main__":
    main()
