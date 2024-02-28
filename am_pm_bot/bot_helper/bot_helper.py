#!/usr/bin/env python
# -*- coding: utf-8 -*-

from am_pm_bot.strapi_helper import StrapiHelper
from am_pm_bot.models import Request
from am_pm_bot.callback_data.create_request import BaseCallback
from am_pm_bot.handlers import Message, CallbackQuery, FSMContext, User
from am_pm_bot.callback_data.payment_ticket import PaymentTicketCallback
from am_pm_bot.payment_helper.crypto_payment_helper import CryptoPaymentHelper
from am_pm_bot import Bot, InlineKeyboardButton, InlineKeyboardMarkup, logging
from am_pm_bot.payment_helper.yoomoney_payment_helper import YoomoneyPaymentHelper

class BotHelper:
    def __init__(self, tg_bot: Bot):
        self.__tg_bot = tg_bot
        self.__strapi_helper = StrapiHelper()
        self.__yoomoney_payment_helper = YoomoneyPaymentHelper()
        self.__crypto_payment_helper = CryptoPaymentHelper()
        self.MANAGERS = self.__strapi_helper.get_list_of_managers()
        self.MANAGER_IDS = [int(manager['attributes']['telegram_id']) for manager in self.MANAGERS]
        self.logger = logging.getLogger("bot_helper")
        self.logger.setLevel(logging.INFO)
        self.greeting_text = "AV Legal специализируется на оказании юридической помощи корпоративным и частным клиентам по вопросам российского и иностранного законодательства, а также представлении клиентов во взаимоотношениях с государственными органами законодательной, исполнительной и судебной власти.\n\nПрофессиональная команда юристов AV Legal позволяет достигать высоких результатов при реализации самых сложных и комплексных проектов. Успешный многолетний опыт сотрудничества со своими клиентами является залогом дальнейшего развития AV Legal и достижения новых высот.\n\nAV Legal специализируется на консультировании по вопросам корпоративного права, права интеллектуальной собственности, рекламного права и иным областям права. Мы также оказываем услуги по структурированию сложных сделок, регистрации объектов интеллектуальной собственности, регистрации юридических лиц как в России, так и за рубежом, а также разработке налоговых стратегий. Кроме того, AV Legal имеет значительный опыт в составлении досудебных и судебных документов, а также защите прав и интересов клиентов в судах, что обеспечивает нашим клиентам надежную помощь в любых юридических вопросах.\n\nМы придерживаемся мировых стандартов и этических принципов международного юридического консалтинга, обеспечивая профессионализм и стабильно высокое качество услуг. Наш добросовестный подход к выполнению своих обязательств и понимание специфики отрасли клиента составляют основу нашей деловой репутации."


    def __init_welcome_keyboard(self, message: Message):
        self.__request_button = InlineKeyboardButton(
            text="Создать запрос",
            callback_data=BaseCallback(command="create_request", user_id=message.from_user.id).pack()
        )
        return InlineKeyboardMarkup(inline_keyboard=[[self.__request_button]])

    def __init_about_us_keyboard(self, message: Message):
        self.__about_us_button = InlineKeyboardButton(
            text="Подробнее о нас",
            callback_data=BaseCallback(command="about_us", user_id=message.from_user.id).pack()
        )
        return InlineKeyboardMarkup(inline_keyboard=[[self.__about_us_button]])

    async def __init_pay_via_yoomoney_button(
            self,
            amount: float,
            telegram_id: int,
            currency: str,
            payment_ticket_id: int
    ):
        payment_url = await self.__yoomoney_payment_helper.generate_payment_url(
            telegram_id,
            amount,
            currency,
            payment_ticket_id
        )

        if currency == "rub":
            currency = "₽"
        else:
            currency = "$"

        return InlineKeyboardButton(
            text=f"{currency}{amount} через Yoomoney",
            url=payment_url
        )

    async def __init_pay_via_crypto_button(
            self,
            amount: float,
            telegram_id: int,
            currency: str,
            payment_ticket_id: int
    ):
        payment_url = await self.__crypto_payment_helper.generate_payment_url(
            telegram_id,
            amount,
            currency,
            payment_ticket_id
        )
        self.__strapi_helper.save_payment_ticket_crypto_invoice_id(payment_ticket_id, payment_url)

        if currency == "rub":
            currency = "₽"
        else:
            currency = "$"

        return InlineKeyboardButton(
            text=f"{currency}{amount} через USDT TRC-20",
            callback_data="pay_usdt_trc_20" 
        )

    async def __init_pay_choices_keyboard(
            self,
            amount: float,
            telegram_id: int,
            currency: str,
            payment_ticket_id: int
    ):
        self.__pay_via_yoomoney_button = await self.__init_pay_via_yoomoney_button(
            amount,
            telegram_id,
            currency,
            payment_ticket_id
        )
        self.__pay_via_crypto_button = await self.__init_pay_via_crypto_button(
            amount,
            telegram_id,
            currency,
            payment_ticket_id
        )

        return InlineKeyboardMarkup(inline_keyboard=[[self.__pay_via_yoomoney_button, self.__pay_via_crypto_button]])

    async def __init_payment_ticket_confirmation_button(self, amount: float, telegram_id: int, currency: str):
        if currency == "rub":
            currencyChar = "₽"
        else:
            currencyChar = "$"
        self.__payment_ticket_confirmation_button = InlineKeyboardButton(
            text=f"Подтвердить создание платежного талона на сумму {currencyChar}{amount}",
            callback_data=PaymentTicketCallback(
                command="send_payment_ticket_to_client",
                telegram_id=telegram_id,
                currency=currency,
                amount=amount
            ).pack()
        )

        return InlineKeyboardMarkup(inline_keyboard=[[self.__payment_ticket_confirmation_button]])

    def __init_contact_client_keyboard(self, request: Request):
        self.__contact_button = InlineKeyboardButton(
            text="Связаться с клиентом",
            callback_data=BaseCallback(command="contact_client", user_id=request.user.id).pack()
        )

        return InlineKeyboardMarkup(inline_keyboard=[[self.__contact_button]])

    async def welcome_user(self, message: Message):
        await message.answer("Добро пожаловать в AV Legal!")
        await message.answer("Благодарим Вас за выбор наших юридических услуг. AV Legal специализируется на предоставлении широкого спектра услуг, включая юридические консультации, подготовку документов, юридическое сопровождение сделок, а также защиту прав и интересов в суде. Мы гарантируем оперативность и эффективность в решении Ваших задач.",
                             reply_markup=self.__init_aboutUs_keyboard(message))
        await message.answer(f'Если у Вас есть запрос, пожалуйста, нажмите на кнопку "Создать запрос". Наши специалисты свяжутся с Вами в кратчайшие сроки.',
                             reply_markup=self.__init_welcome_keyboard(message))

    async def save_user(self, user: User):
        self.__strapi_helper.save_client_info(user)

    async def ask_request_description(self, callback_query: CallbackQuery):
        await self.__tg_bot.send_message(callback_query.from_user.id, f"Пожалуйста, опишите Вашу ситуацию максимально подробно, укажите все существенные факты и обстоятельства:")


    async def about_us_description(self, callback_query: CallbackQuery):
        await self.__tg_bot.send_message(callback_query.from_user.id, self.greeting_text)

    async def ask_payment_currency(self, message: Message):
        await self.__tg_bot.send_message(message.from_user.id, f"В какой валюте производится оплата?")

    async def ask_confirmation(self, message: Message, state: FSMContext):
        client_info = self.__strapi_helper.get_client_by_manager_telegram_id(
            manager_telegram_id=message.from_user.id
        )['attributes']

        await state.update_data(
            telegram_id=client_info['telegram_id']
        )

        payment_ticket_data = await state.get_data()
        await self.__tg_bot.send_message(
            chat_id=message.from_user.id,
            text=f"Вы подтверждаете создание платежного талона?\n"
                 f"Сумма: {payment_ticket_data['amount']}\n"
                 f"Валюта: {payment_ticket_data['currency']}\n"
                 f"Для пользователя: {client_info['last_name']} {client_info['first_name']} @{client_info['telegram_username']}",
            reply_markup=await self.__init_payment_ticket_confirmation_button(
                amount=payment_ticket_data['amount'],
                currency=payment_ticket_data['currency'],
                telegram_id=payment_ticket_data['telegram_id']
            )
        )

    async def send_payment_ticket_to_client(self,
                                            callback_query: CallbackQuery,
                                            callback_data: PaymentTicketCallback):
        payment_ticket = self.__strapi_helper.save_payment_ticket_info(callback_data)
        await self.__tg_bot.send_message(
            chat_id=callback_data.telegram_id,
            text="Вы только что получили платежный талон. Когда оплата будет завершена - отправьте /check_payment",
            reply_markup=await self.__init_pay_choices_keyboard(
                amount=callback_data.amount,
                telegram_id=callback_data.telegram_id,
                currency=callback_data.currency,
                payment_ticket_id=payment_ticket['data']['id']
            )
        )

        await self.__tg_bot.send_message(
            chat_id=callback_query.from_user.id,
            text="Запрос отправлен"
        )

        await self.__tg_bot.answer_callback_query(callback_query.id)

    async def check_yoomoney_payment(self, message: Message):
        unpaid_payment_tickets = self.__strapi_helper.get_unpaid_payment_tickets_by_telegram_id(message.from_user.id)
        self.logger.info(unpaid_payment_tickets)
        no_payment = True
        for payment_ticket in unpaid_payment_tickets:
            payment = await self.__yoomoney_payment_helper.check_payment_from_user(message.from_user, payment_ticket) #error 
            if payment is not None:
                self.logger.info(f"Получена оплата: {payment.status} {payment.amount} {payment.label} "
                                 f"{payment.operation_id} {payment.datetime}")
                await message.answer(f"Оплата {payment.operation_id} успешно завершена!")
                await self.notify_manager_about_successful_payment(message.from_user)
                self.__strapi_helper.change_payment_ticket_status(payment_ticket['id'], payment.status)
                self.__strapi_helper.save_yoomoney_payment_id_to_payment_ticket(
                    payment_ticket['id'],
                    payment.operation_id
                )
                no_payment = False

        if no_payment:
            await message.answer("Не удалось найти недавние платежи")

    async def check_plisio_payment(self, message: Message):
        payment_tickets = self.__strapi_helper.get_unpaid_payment_tickets_by_telegram_id(message.from_user.id)

        no_payment = True
        for payment_ticket in payment_tickets:
            payment = await self.__crypto_payment_helper.check_payment_from_user(payment_ticket['plisio_invoice_id'])
            if payment is not None:
                self.logger.info(f"Получена оплата: {payment['id']} {payment['status']} {payment['invoice_total_sum']}")
                await message.answer(f"Оплата {payment['id']} {payment['status']}!")
                await self.notify_manager_about_successful_payment(message.from_user)
                self.__strapi_helper.change_payment_ticket_status(payment_ticket['id'], payment['status'])
                no_payment = False

        if no_payment:
            await message.answer("Не удалось найти недавние платежи")

    async def save_request(self, state: FSMContext, message: Message):
        request_data = await state.get_data()
        request = Request(
            user=message.from_user,
            strapi_id=self.__strapi_helper.get_client_by_telegram_id(message.from_user.id),
            client_description=request_data['client_description']
        )
        self.__strapi_helper.save_request_info(request)
        await self.__tg_bot.send_message(message.from_user.id,
                                         f"Ваш запрос успешно получен. Мы благодарим вас за обращение в AV Legal. Наша команда специалистов приступит к обработке вашего запроса в кратчайшие сроки. Следите за обновлениями и ожидайте ответа от нас в ближайшее время.")
        return request

    async def notify_manager_about_successful_payment(self, user: User):
        manager = self.__strapi_helper.get_manager_by_client_telegram_id(user.id)
        await self.__tg_bot.send_message(manager['attributes']['telegram_id'], "Клиент выслал запрос на подтверждение оплаты.")

    async def notify_managers_about_new_request(self, request: Request):
        for manager in self.MANAGERS:
            await self.__tg_bot.send_message(
                chat_id=manager['attributes']['telegram_id'],
                text=f"Новый запрос от "
                     f"{'@' + request.user.username if request.user.username != 'None' else request.user.full_name}\n\n"
                     f"Описание: {request.client_description}\n\n",
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
                text="Успешно связан с клиентом. "
                     "Все новые сообщения будут перенаправлены клиенту. "
                     f"Для разрыва соединения отправьте /terminate_connection"
            )
        except Exception as e:
            self.logger.error(f"Не удалось связаться с клиентом с telegram id {client_telegram_id}: {e}")
            await self.__tg_bot.send_message(
                chat_id=callback_query.from_user.id,
                text="Не удалось установить соединение. Попробуйте еще раз или свяжитесь с клиентом вручную."
            )

    async def disconnect_manager_from_client(self,
                                             message: Message):
        manager_telegram_id = message.from_user.id
        try:
            self.__strapi_helper.disconnect_manager_from_client(manager_telegram_id)
            await self.__tg_bot.send_message(
                chat_id=message.from_user.id,
                text="Успешно разорвано соединение с клиентом."
            )
        except TypeError:
            await self.__tg_bot.send_message(
                chat_id=message.from_user.id,
                text="Не удалось разорвать соединение. Попробуйте еще раз."
            )

    async def send_message_from_manager_to_client(self, message: Message):
        manager = self.__strapi_helper.get_manager_by_telegram_id(message.from_user.id)

        await self.__tg_bot.send_message(
            chat_id=manager['attributes']['client']['data']['attributes']['telegram_id'],
            text=f"[Менеджер {manager['attributes']['name']}]: {message.text}"
        )

    async def send_message_from_client_to_manager(self, message: Message):
        manager = self.__strapi_helper.get_manager_by_client_telegram_id(message.from_user.id)

        await self.__tg_bot.send_message(chat_id=manager['attributes']['telegram_id'],
                                         text=f"[Клиент {message.from_user.first_name}]: {message.text}")

    async def create_payment_request(self, message: Message):
        await message.answer(f"Введите сумму для оплаты:")

    def verify_payment(self, payment_ticket):
        raise NotImplementedError("Этот метод должен быть реализован.")
