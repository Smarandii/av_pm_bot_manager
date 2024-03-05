from am_pm_bot import router, bot
from am_pm_bot.callback_data.payment_ticket import PaymentTicketCallback
from am_pm_bot.forms.init_form import InitForm
from am_pm_bot.bot_helper.bot_helper import BotHelper
from am_pm_bot.handlers import CallbackQuery, F, FSMContext
from am_pm_bot.callback_data.create_request import BaseCallback
from aiogram import types

bot_pm = BotHelper(tg_bot=bot)


@router.callback_query(BaseCallback.filter(F.command == "create_request"))
async def create_request_handler(callback_query: CallbackQuery,
                                 callback_data: BaseCallback,
                                 state: FSMContext) -> None:
    await state.set_state(InitForm.description)
    await bot_pm.ask_request_description(callback_query)
    await callback_query.answer()
    


    
    
    
    
@router.callback_query(lambda c: c.data == 'pay_usdt_trc_20')
async def process_usdt_trc_20_payment(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, "TW4FQqc76GbqSKSJQWzyJXd7MVqkxbec4A")

    await bot.send_photo(callback_query.from_user.id, "https://cdn.discordapp.com/attachments/1001830460734853211/1211021667346681967/qr.jpg?ex=65ecaed1&is=65da39d1&hm=8d29ec3d08bc96c03a9cc40c4f6eb1603492d6dcaf141f3017262c3fdccc030b&")

    await callback_query.answer()





@router.callback_query(BaseCallback.filter(F.command == "about_us"))
async def about_us_handler(callback_query: CallbackQuery,
                                 callback_data: BaseCallback,
                                 state: FSMContext) -> None:
    await state.set_state(InitForm.description)
    await bot_pm.about_us_description(callback_query)
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
