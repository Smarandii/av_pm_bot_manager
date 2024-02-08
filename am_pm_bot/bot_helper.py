from am_pm_bot import Bot
from am_pm_bot.handlers import Message, CallbackQuery
from am_pm_bot.callback_data.create_request import CreateRequestCallback
from aiogram.utils.keyboard import InlineKeyboardMarkup, InlineKeyboardButton


class BotHelper:
    def __init__(self, tg_bot: Bot):
        self.__tg_bot = tg_bot

    def __init_welcome_keyboard(self, message: Message):
        self.__create_request_button = InlineKeyboardButton(
            text="Create Request",
            callback_data=CreateRequestCallback(command="create_request", user_id=message.from_user.id).pack()
        )
        return InlineKeyboardMarkup(inline_keyboard=[[self.__create_request_button]])

    async def welcome_user(self, message: Message):
        await message.answer(f"Hello, {message.from_user.full_name}! If you wish to leave a request press button:",
                             reply_markup=self.__init_welcome_keyboard(message))

    async def ask_request_details(self, callback_query: CallbackQuery, callback_data: CreateRequestCallback):
        await self.__tg_bot.send_message(callback_query.from_user.id, f"Please provide request details:")


    def save_request(self, request):
        raise NotImplementedError("This method needs to be implemented.")

    def notify_manager(self, request):
        raise NotImplementedError("This method needs to be implemented.")

    def relay_message_to_user(self, message, user):
        raise NotImplementedError("This method needs to be implemented.")

    def relay_message_to_manager(self, message, manager):
        raise NotImplementedError("This method needs to be implemented.")

    def request_payment(self, payment_ticket):
        raise NotImplementedError("This method needs to be implemented.")

    def verify_payment(self, payment_ticket):
        raise NotImplementedError("This method needs to be implemented.")
