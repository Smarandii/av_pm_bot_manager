from am_pm_bot import router, bot
from am_pm_bot.callback_data.payment_ticket import PaymentTicketCallback
from am_pm_bot.forms.init_form import InitForm
from am_pm_bot.bot_helper.bot_helper import BotHelper
from am_pm_bot.handlers import CallbackQuery, F, FSMContext
from am_pm_bot.callback_data.create_request import BaseCallback

bot_pm = BotHelper(tg_bot=bot)


@router.callback_query(BaseCallback.filter(F.command == "create_request"))
async def create_request_handler(callback_query: CallbackQuery,
                                 callback_data: BaseCallback,
                                 state: FSMContext) -> None:
    await state.set_state(InitForm.description)
    await bot_pm.ask_request_description(callback_query)
    await callback_query.answer()


@router.callback_query(BaseCallback.filter(F.command == "contact_client"))
async def contact_client_handler(callback_query: CallbackQuery,
                                 callback_data: BaseCallback) -> None:
    await bot_pm.connect_manager_to_client(callback_query, callback_data)
    await callback_query.answer()


@router.callback_query(PaymentTicketCallback.filter(F.command == "send_payment_ticket_to_client"))
async def send_payment_ticket_to_client_callback_handler(callback_query: CallbackQuery,
                                                         callback_data: PaymentTicketCallback):
    await bot_pm.send_payment_ticket_to_client(callback_query, callback_data)
    await callback_query.answer()
