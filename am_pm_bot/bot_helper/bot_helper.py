from am_pm_bot.strapi_helper import StrapiHelper
from am_pm_bot.models import Request, PaymentTicket
from am_pm_bot.callback_data.create_request import BaseCallback
from am_pm_bot.handlers import Message, CallbackQuery, FSMContext, User
from am_pm_bot import Bot, InlineKeyboardButton, InlineKeyboardMarkup, logging


class BotHelper:
    def __init__(self, tg_bot: Bot):
        self.__tg_bot = tg_bot
        self.__strapi_helper = StrapiHelper()
        self.MANAGERS = self.__strapi_helper.get_list_of_managers()
        self.MANAGER_IDS = [int(manager['attributes']['telegram_id']) for manager in self.MANAGERS]
        self.logger = logging.getLogger("strapi_helper")
        self.logger.setLevel(logging.INFO)

    def __init_welcome_keyboard(self, message: Message):
        self.__request_button = InlineKeyboardButton(
            text="Create Request",
            callback_data=BaseCallback(command="create_request", user_id=message.from_user.id).pack()
        )
        return InlineKeyboardMarkup(inline_keyboard=[[self.__request_button]])

    def __init_contact_client_keyboard(self, request: Request):
        self.__contact_button = InlineKeyboardButton(
            text="Contact Client",
            callback_data=BaseCallback(command="contact_client", user_id=request.user.id).pack()
        )

        return InlineKeyboardMarkup(inline_keyboard=[[self.__contact_button]])

    async def welcome_user(self, message: Message):
        await message.answer(f"Hello, {message.from_user.full_name}! If you wish to leave a request press button:",
                             reply_markup=self.__init_welcome_keyboard(message))

    async def save_user(self, user: User):
        self.__strapi_helper.save_client_info(user)

    async def ask_request_description(self, callback_query: CallbackQuery, callback_data: BaseCallback):
        await self.__tg_bot.send_message(callback_query.from_user.id, f"Please provide description for your request:")

    async def ask_request_budget(self, message: Message):
        await self.__tg_bot.send_message(message.from_user.id, f"What's your budget?")

    async def ask_payment_currency(self, message: Message):
        await self.__tg_bot.send_message(message.from_user.id, f"What currency?")

    async def create_ticket_confirmation(self, message: Message, state: FSMContext):
        payment_ticket_data = await state.get_data()
        await self.__tg_bot.send_message(
            chat_id=message.from_user.id,
            text=f"Do you confirm creation of payment ticket?\n"
                 f"Amount: {payment_ticket_data['amount']}\n"
                 f"Currency: {payment_ticket_data['currency']}\n"
                 f"For user: {payment_ticket_data['client_id']}"
        )

    async def save_request(self, state: FSMContext, message: Message):
        request_data = await state.get_data()
        request = Request(
            user=message.from_user,
            strapi_id=self.__strapi_helper.get_client_by_telegram_id(message.from_user.id),
            client_description=request_data['client_description'],
            budget=request_data['budget']
        )
        self.__strapi_helper.save_request_info(request)
        await self.__tg_bot.send_message(message.from_user.id,
                                         f"Thank you for your request! Manager will contact you soon.")
        return request

    async def notify_managers(self, request: Request):
        for manager in self.MANAGERS:
            await self.__tg_bot.send_message(
                chat_id=manager['attributes']['telegram_id'],
                text=f"New request from "
                     f"{'@' + request.user.username if request.user.username != 'None' else request.user.full_name}",
                reply_markup=self.__init_contact_client_keyboard(request)
            )

    async def connect_manager_to_client(self,
                                        callback_query: CallbackQuery,
                                        callback_data: BaseCallback):
        manager_telegram_id = callback_query.from_user.id
        client_telegram_id = callback_data.user_id
        try:
            self.__strapi_helper.connect_manager_to_client(manager_telegram_id, client_telegram_id)
            await self.__tg_bot.send_message(
                chat_id=callback_query.from_user.id,
                text="Successfully connected with client. "
                     "All new messages would be redirected to client. "
                     f"To terminate the connection - send /terminate_connection"
            )
        except Exception as e:
            self.logger.error(f"Failed to connect to client with telegram id {client_telegram_id}: {e}")
            await self.__tg_bot.send_message(
                chat_id=callback_query.from_user.id,
                text="Connection failed. Try again or contact client manually."
            )

    async def disconnect_manager_from_client(self,
                                             message: Message):
        manager_telegram_id = message.from_user.id
        try:
            self.__strapi_helper.disconnect_manager_from_client(manager_telegram_id)
            await self.__tg_bot.send_message(
                chat_id=message.from_user.id,
                text="Successfully disconnected from client."
            )
        except TypeError:
            await self.__tg_bot.send_message(
                chat_id=message.from_user.id,
                text="Disconnection failed. Try again."
            )

    async def send_message_from_manager_to_client(self, message: Message):
        manager = self.__strapi_helper.get_manager_by_telegram_id(message.from_user.id)

        await self.__tg_bot.send_message(
            chat_id=manager['attributes']['client']['data']['attributes']['telegram_id'],
            text=f"[Manager {manager['attributes']['name']}]: {message.text}"
        )

    async def send_message_from_client_to_manager(self, message: Message):
        manager = self.__strapi_helper.get_manager_by_client_telegram_id(message.from_user.id)

        await self.__tg_bot.send_message(chat_id=manager['attributes']['telegram_id'], text=f"[Client {message.from_user.first_name}]: {message.text}")

    async def create_payment_request(self, message: Message):
        await message.answer(f"Enter amount to pay:")

    def verify_payment(self, payment_ticket):
        raise NotImplementedError("This method needs to be implemented.")
