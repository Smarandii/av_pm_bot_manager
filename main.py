from am_pm_bot import (router, bot, dp,
                       WEBAPP_HOST, WEBAPP_PORT, WEBHOOK_PATH, WEBHOOK_SECRET,
                       web, setup_application, SimpleRequestHandler)
from am_pm_bot.handlers.init_handlers import on_startup, on_shutdown


def main() -> None:
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
    import am_pm_bot.handlers.command_handlers
    import am_pm_bot.handlers.command_handlers
    import am_pm_bot.handlers.callback_query_handlers
    import am_pm_bot.handlers.form_handlers
    import am_pm_bot.handlers.redirect_messages_handlers

    main()
