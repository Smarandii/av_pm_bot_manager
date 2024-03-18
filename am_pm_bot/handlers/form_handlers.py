from am_pm_bot import router, bot
from am_pm_bot.forms.init_form import InitForm
from am_pm_bot.handlers import Message, FSMContext
from am_pm_bot.bot_helper.bot_helper import BotHelper
from am_pm_bot.forms.create_payment_ticket_form import CreatePaymentTicketForm
from am_pm_bot.forms.transaction_form import getTransactionForm


bot_pm = BotHelper(tg_bot=bot)


@router.message(InitForm.description)
async def init_form_description_handler(message: Message,
                                        state: FSMContext) -> None:
    await state.update_data(client_description=message.text)
    req = await bot_pm.save_request(state, message)
    await bot_pm.notify_managers_about_new_request(req)

    await state.set_state(None)

@router.message(CreatePaymentTicketForm.amount)
async def create_payment_ticket_form_amount_handler(message: Message,
                                                    state: FSMContext) -> None:
    await state.update_data(amount=message.text)
    await state.set_state(CreatePaymentTicketForm.currency)
    await bot_pm.ask_payment_currency(message)


@router.message(CreatePaymentTicketForm.currency)
async def create_payment_ticket_form_currency_handler(message: Message,
                                                      state: FSMContext) -> None:
    await state.update_data(currency=message.text)
    await state.set_state(CreatePaymentTicketForm.confirm)
    await bot_pm.ask_confirmation(message, state)


@router.message(getTransactionForm.transaction_hash)
async def get_transaction_hash_from_user(message: Message, 
                                         state: FSMContext) -> None:
    await state.update_data(transaction_hash=message.text)

    await bot_pm.notify_about_process_payment(message)

    hashtx = await bot_pm.get_transact_data(state)
    await bot_pm.check_crypto_payment(message, hashtx)

    await state.set_state(None)