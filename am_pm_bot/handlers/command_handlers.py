from am_pm_bot.handlers import FSMContext
from am_pm_bot import router, bot, logging
from am_pm_bot.bot_helper.bot_helper import BotHelper
from am_pm_bot.handlers import CommandStart, Command, Message
from am_pm_bot.forms.create_payment_ticket_form import CreatePaymentTicketForm


bot_pm = BotHelper(tg_bot=bot)
logger = logging.getLogger("command_handler_logger")
logger.setLevel(logging.INFO)


@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await bot_pm.welcome_user(message)
    try:
        await bot_pm.save_user(message.from_user)
        logger.info("User saved")
    except Exception as e:
        logger.error(f"User not saved: {e}")


@router.message(Command("terminate_connection"))
async def command_terminate_connection_handler(message: Message) -> None:
    await bot_pm.disconnect_manager_from_client(message)


@router.message(Command("request_payment"))
async def command_request_payment_handler(message: Message, state: FSMContext) -> None:
    await state.set_state(CreatePaymentTicketForm.amount)
    await bot_pm.create_payment_request(message)


@router.message(Command("check_payment"))
async def command_payment_success_handler(message: Message) -> None: 
    #await bot_pm.check_yoomoney_payment(message) # error 
    #await bot_pm.check_plisio_payment(message)
    await bot_pm.notify_manager_about_successful_payment(message.from_user)