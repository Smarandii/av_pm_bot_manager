from am_pm_bot import router, bot
from am_pm_bot.forms.init_form import InitForm
from am_pm_bot.handlers import Message, FSMContext
from am_pm_bot.bot_helper.bot_helper import BotHelper
from am_pm_bot.forms.create_payment_ticket_form import CreatePaymentTicketForm

bot_pm = BotHelper(tg_bot=bot)


@router.message(InitForm.description)
async def init_form_description_handler(message: Message,
                                        state: FSMContext) -> None:
    await state.update_data(client_description=message.text)
    await state.set_state(InitForm.budget)
    await bot_pm.ask_request_budget(message)


@router.message(InitForm.budget)
async def init_form_budget_handler(message: Message,
                                   state: FSMContext) -> None:
    await state.update_data(budget=message.text)
    request = await bot_pm.save_request(state, message)
    await bot_pm.notify_managers(request)
    await state.clear()


@router.message(CreatePaymentTicketForm.amount)
async def create_payment_ticket_form_amount_handler(message: Message,
                                                    state: FSMContext) -> None:
    await state.update_data(amount=message.text)
    await bot_pm.get_client_telegram_id_by_manager_id(message.from_user.id)
    await state.set_state(CreatePaymentTicketForm.currency)
    await bot_pm.ask_payment_currency(message)


@router.message(CreatePaymentTicketForm.currency)
async def create_payment_ticket_form_currency_handler(message: Message,
                                                      state: FSMContext) -> None:
    await state.update_data(currency=message.text)
    await bot_pm.create_ticket_confirmation(message, state)
