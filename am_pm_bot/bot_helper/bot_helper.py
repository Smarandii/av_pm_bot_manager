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
import math
import requests
import datetime as dt
from datetime import datetime, timedelta


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


    def __init_welcome_keyboard(self, message: Message):
        self.__request_button = InlineKeyboardButton(
            text=f"Создать запрос",
            callback_data=BaseCallback(command="create_request", user_id=message.from_user.id).pack()
        )
        return InlineKeyboardMarkup(inline_keyboard=[[self.__request_button]])

    def __init_aboutUs_keyboard(self, message: Message):
        self.__request_button = InlineKeyboardButton(
            text="Подробнее о нас",
            callback_data=BaseCallback(command="about_us", user_id=message.from_user.id).pack()
        )
        return InlineKeyboardMarkup(inline_keyboard=[[self.__request_button]])

    



    async def get_transact_data(self, state: FSMContext):
        user_data = await state.get_data()
        print("Transaction hash:")
        print(user_data['transaction_hash'])

        return user_data['transaction_hash']
        

    async def __init_pay_via_yoomoney_button(
            self,
            amount: float,
            telegram_id: int,
            currency: str,
            payment_ticket_id: int
    ):
        print(f"AMOUNT {amount}")
        usd_rate = requests.get('https://www.cbr-xml-daily.ru/daily_json.js').json()['Valute']['USD']["Value"]

        payment_url = await self.__yoomoney_payment_helper.generate_payment_url(
            telegram_id,
            amount*usd_rate,
            currency,
            payment_ticket_id
        )
        aamount = 0
        if currency.lower() == "rub":
            ok_amount = round(amount*usd_rate)
            print(f"{ok_amount} AMOUNT BLAA")
            currency = "₽"
            text_output = f"{currency}{ok_amount} / Yoomoney"
            aamount = amount*usd_rate
            currency = "rub"
        else:
            currency = "$"
            text_output = f"{currency}{round(amount)} / Yoomoney"
            aamount = amount
            currency = "usd"

        payment_url = await self.__yoomoney_payment_helper.generate_payment_url(
            telegram_id,
            aamount,
            currency,
            payment_ticket_id
        )

        return InlineKeyboardButton(
            text=text_output,
            url=payment_url
        )

    global repeatPayment




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

        usd_rate = round(requests.get('https://www.cbr-xml-daily.ru/daily_json.js').json()['Valute']['USD']["Value"])        
        if currency.lower() == "rub":
            currency = "$"
            ok_amount = round(amount*usd_rate)
            next_repeat_payment = f"Оплатите ₽{ok_amount} / {currency}{amount}"
        else:
            currency = "$"
            next_repeat_payment = f"Оплатите {currency}{amount}"

        global repeatPayment
        repeatPayment = f"{next_repeat_payment} через USDT TRC-20, после подтверждения транзакции в блокчейне отправьте /check_crypto_payment."

        return InlineKeyboardButton(
            text=f"{currency}{amount} / USDT TRC-20",
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
        usd_rate = round(requests.get('https://www.cbr-xml-daily.ru/daily_json.js').json()['Valute']['USD']["Value"])
        print("()"*10 + "\n"+amount)
        aamount = float(amount)

        if currency.lower() == "rub":
            currencyChar = "₽"
            aamount = round(aamount/usd_rate, 4)
            print(f"AAAAMOUNT : {aamount}")
            print(f"USD RATE: {usd_rate}")
        else:
            currencyChar = "$"
            aamount = aamount
        self.__payment_ticket_confirmation_button = InlineKeyboardButton(
            text=f"Подтвердить создание платежного талона на сумму {currencyChar}{amount}",
            callback_data=PaymentTicketCallback(
                command="send_payment_ticket_to_client",
                telegram_id=telegram_id,
                currency=currency,
                amount=aamount
            ).pack()
        )

        return InlineKeyboardMarkup(inline_keyboard=[[self.__payment_ticket_confirmation_button]])

    async def __init_transaction_help(self):
        self.__help_with_transaction_hash_button = InlineKeyboardButton(
            text = f"Как посмотреть хэш транзакции",
            url = "https://telegra.ph/Instrukciya-kak-smotret-hehsh-Txid-tranzakcii-03-17"
        )
        return InlineKeyboardMarkup(inline_keyboard=[[self.__help_with_transaction_hash_button]])


    def __init_contact_client_keyboard(self, request: Request):
        self.__contact_button = InlineKeyboardButton(
            text="Связаться с клиентом",
            callback_data=BaseCallback(command="contact_client", user_id=request.user.id).pack()
        )

        return InlineKeyboardMarkup(inline_keyboard=[[self.__contact_button]])

    global greeting_text
    greeting_text = "AV Legal специализируется на оказании юридической помощи корпоративным и частным клиентам по вопросам российского и иностранного законодательства, а также представлении клиентов во взаимоотношениях с государственными органами законодательной, исполнительной и судебной власти.\n\nПрофессиональная команда юристов AV Legal позволяет достигать высоких результатов при реализации самых сложных и комплексных проектов. Успешный многолетний опыт сотрудничества со своими клиентами является залогом дальнейшего развития AV Legal и достижения новых высот.\n\nAV Legal специализируется на консультировании по вопросам корпоративного права, права интеллектуальной собственности, рекламного права и иным областям права. Мы также оказываем услуги по структурированию сложных сделок, регистрации объектов интеллектуальной собственности, регистрации юридических лиц как в России, так и за рубежом, а также разработке налоговых стратегий. Кроме того, AV Legal имеет значительный опыт в составлении досудебных и судебных документов, а также защите прав и интересов клиентов в судах, что обеспечивает нашим клиентам надежную помощь в любых юридических вопросах.\n\nМы придерживаемся мировых стандартов и этических принципов международного юридического консалтинга, обеспечивая профессионализм и стабильно высокое качество услуг. Наш добросовестный подход к выполнению своих обязательств и понимание специфики отрасли клиента составляют основу нашей деловой репутации."


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


    async def ask_for_transaction_id(self, message: Message):
        await self.__tg_bot.send_message(chat_id = message.from_user.id, text = f"Отправьте, пожалуйста, Transaction ID (хэш)", reply_markup = await self.__init_transaction_help())

    async def about_us_description(self, callback_query: CallbackQuery):
        await self.__tg_bot.send_message(callback_query.from_user.id, greeting_text)

    async def text_for_user(self, callback_query: CallbackQuery):
        await self.__tg_bot.send_message(callback_query.from_user.id, repeatPayment)

    async def ask_payment_currency(self, message: Message):
        await self.__tg_bot.send_message(message.from_user.id, f"В какой валюте производится оплата?")

    async def notify_about_process_payment(self, message: Message):
        await self.__tg_bot.send_message(message.from_user.id, f"Пожалуйста подождите, идёт проверка транзакции... 🕔")



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

    global unpaid_payment_ticket_id 

    async def send_payment_ticket_to_client(self,
                                            callback_query: CallbackQuery,
                                            callback_data: PaymentTicketCallback):
        payment_ticket = self.__strapi_helper.save_payment_ticket_info(callback_data)
        global unpaid_payment_ticket_id
        unpaid_payment_ticket_id = payment_ticket['data']['id']
        await self.__tg_bot.send_message(
            chat_id=callback_data.telegram_id,
            text="Вы только что получили платежный талон. Когда оплата будет завершена - отправьте /check_payment для платежа банковской картой и /check_crypto_payment для платежа криптовалютой.",
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

    async def check_plisio_payment(self, message: Message):
        payment_id = unpaid_payment_ticket_id # получаем айди текущей транзакции
        unpaid_payment_tickets = self.__strapi_helper.get_unpaid_payment_tickets_by_telegram_id(message.from_user.id) # список всех транзакций
        
        
        current_transaction_data = next((transaction for transaction in unpaid_payment_tickets if transaction['id'] == payment_id), None) # неоплаченная транзакция


        amount = current_transaction_data['attributes']['amount']


        target = "TW4FQqc76GbqSKSJQWzyJXd7MVqkxbec4A"
        blockchain_network = "trc20"


        response = requests.get(
            f"https://api.trongrid.io/v1/accounts/{target}/transactions/{blockchain_network}",
            headers = {"accept": "application/json"}
           )

        def find_amount_after_commission(amount, list_amounts):
            commission = 3
            start_amount = amount - commission

            for i in range((start_amount * 100), (amount + 1) * 100):
                current_amount = i / 100
        
                for number in list_amounts:
                    if round(current_amount, 2) == number:
                        return number

            return False

        transaction_chain = []

        for transaction in response.json().get('data', []):
            currency = transaction.get("token_info", {}).get('symbol')
            sender = transaction.get('from')
            receiver = transaction.get("to")
            money_amount_non_tempered = transaction.get('value', '')
            dec = -1 * int(transaction.get('token_info', {}).get('decimals', '6'))
            money_amount_final = float(money_amount_non_tempered[:dec] + '.' + money_amount_non_tempered[dec:])
            transaction_time = dt.datetime.fromtimestamp(float(transaction.get('block_timestamp', '')) / 1000)

            if receiver == target:
                if currency == "USDT":
                    output = f'{transaction_time}|{money_amount_final}'
                    transaction_chain.append(output)

        print(transaction_chain)

        transactions_datetime = [datetime.strptime(transaction.split('|')[0], '%Y-%m-%d %H:%M:%S') for transaction in transaction_chain]

        # Определение даты, которая была сутки назад от текущего момента времени
        one_day_ago = datetime.now() - timedelta(days=3)

        # Фильтрация списка
        filtered_transactions = [transaction for transaction in transactions_datetime if transaction >= one_day_ago]

        # Преобразование обратно в формат строк
        transaction_chain = [transaction for transaction in transaction_chain if datetime.strptime(transaction.split('|')[0], '%Y-%m-%d %H:%M:%S') in filtered_transactions]

        if len(transaction_chain) > 1:
            print("3@$#"*20)
        else:
            pass

        print("A"*30)
        print(transaction_chain)
        print("A"*30)

        transaction_chain_only_amount = []
        for i in range(len(transaction_chain)):
            transaction_chain_only_amount.append(float(transaction_chain[i].split('|')[1]))
        print(transaction_chain_only_amount)

        def get_time(entry):
            return dt.datetime.strptime(
              entry.split('|')[0],
              "%Y-%m-%d %H:%M:%S"
            )

        transaction_chain = sorted(transaction_chain, key=get_time)

        for item in transaction_chain:
            print(item)
        amount = find_amount_after_commission(amount, transaction_chain_only_amount)
        print("AMOUNT N")
        print(amount)
        print("AMOUNT N")


        async def approve_payment(position):
            if float(transaction_chain[position].split('|')[1]) == amount:
                manager = self.__strapi_helper.get_manager_by_client_telegram_id(message.from_user.id)
                filtered_data = [item for item in transaction_chain if float(item.split('|')[1]) == amount]
                print(filtered_data)
                filtered_data = [item.split('|')[0] for item in filtered_data]
                print("#####")
                print(filtered_data)
                current_time = datetime.now() - timedelta(hours=72)

                end_time = current_time + timedelta(hours=72)


                filtered_data_list = []

                for date_str in filtered_data:
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
    
                    if current_time < date_obj < end_time:
                        await self.__tg_bot.send_message(chat_id=message.from_user.id, text=f"Оплата получена.")
                        await self.__tg_bot.send_message(chat_id=message.from_user.id, text=f"Благодарим Вас за выбор AV Legal. В случае возникновения дополнительных вопросов или потребности в дальнейшей консультации,  обращайтесь к нам. Наша команда всегда готова предоставить Вам квалифицированную помощь и поддержку в решении любых правовых вопросов.")
                        await self.__tg_bot.send_message(manager['attributes']['telegram_id'], text=f"Транзакция подтверждена.\nВремя: {date_str}\nОплачено: {amount} USDT")
                        filtered_data_list.append(date_str)
                        self.__strapi_helper.change_payment_ticket_status(payment_id, "success")
                    else:
                        print(f"{position} didn't work")

        print(float(transaction_chain[-1].split('|')[1]))
        if float(transaction_chain[-1].split('|')[1]) == amount:
            await approve_payment(-1)
        else:
            if float(transaction_chain[-2].split('|')[1]) == amount:
                await approve_payment(-2)
            else:
                if float(transaction_chain[-3].split('|')[1]) == amount:
                    await approve_payment(-3)
                else:
                    if float(transaction_chain[-4].split('|')[1]) == amount:
                        await approve_payment(-4)
                    else:
                        if float(transaction_chain[-5].split('|')[1]) == amount:
                            await approve_payment(-5)
                        else:
                            await self.__tg_bot.send_message(chat_id=message.from_user.id, text="Не удалось найти недавние платежи.")



    async def check_crypto_payment(self, message: Message, txid_hash):

        txid = txid_hash

        manager = self.__strapi_helper.get_manager_by_client_telegram_id(message.from_user.id)

        payment_id = unpaid_payment_ticket_id # получаем айди текущей транзакции
        unpaid_payment_tickets = self.__strapi_helper.get_unpaid_payment_tickets_by_telegram_id(message.from_user.id) # список всех транзакций
        
        
        current_transaction_data = next((transaction for transaction in unpaid_payment_tickets if transaction['id'] == payment_id), None) # неоплаченная транзакция


        amount = current_transaction_data['attributes']['amount']


        target = "TW4FQqc76GbqSKSJQWzyJXd7MVqkxbec4A"
        blockchain_network = "trc20"


        response = requests.get(
            f"https://api.trongrid.io/v1/accounts/{target}/transactions/{blockchain_network}",
            headers = {"accept": "application/json"}
           )


        transaction_chain = []

        for transaction in response.json().get('data', []):
            currency = transaction.get("token_info", {}).get('symbol')
            sender = transaction.get('from')
            transact_id = transaction.get('transaction_id')
            receiver = transaction.get("to")
            money_amount_non_tempered = transaction.get('value', '')
            dec = -1 * int(transaction.get('token_info', {}).get('decimals', '6'))
            money_amount_final = float(money_amount_non_tempered[:dec] + '.' + money_amount_non_tempered[dec:])
            transaction_time = dt.datetime.fromtimestamp(float(transaction.get('block_timestamp', '')) / 1000)

            if receiver == target:
                if currency == "USDT":
                    output = f'{transaction_time}|{money_amount_final}%{transact_id}'
                    transaction_chain.append(output)

        keyword_found = False

        for item in transaction_chain:
            if txid in item:
                keyword_found = True
                break

        if keyword_found:
            pass
        else:
            await self.__tg_bot.send_message(chat_id=message.from_user.id, text=f"Транзакция не подтверждена.")

        for data in transaction_chain:
            parts = data.split('%')

            if len(parts) > 1:
                txid_from_data = parts[-1].strip()

                if txid_from_data == txid:


                    data_parts = parts[0].split('|')
            
                    transaction_date = data_parts[0]
                    transaction_amount = data_parts[1]

                    if amount == 4:
                        if float(amount) == math.ceil(float(transaction_amount) / 2) * 2 or math.ceil(float(transaction_amount) / 3) * 3:
                            await self.__tg_bot.send_message(manager['attributes']['telegram_id'], text=f"Транзакция за {transaction_date} на сумму {transaction_amount} успешно выполнена.")
                            await self.__tg_bot.send_message(chat_id=message.from_user.id, text=f"Транзакция за {transaction_date} на сумму {transaction_amount} успешно выполнена.")
                            await self.__tg_bot.send_message(chat_id=message.from_user.id, text=f"Оплата получена.")
                            await self.__tg_bot.send_message(chat_id=message.from_user.id, text=f"Благодарим Вас за выбор AV Legal. В случае возникновения дополнительных вопросов или потребности в дальнейшей консультации,  обращайтесь к нам. Наша команда всегда готова предоставить Вам квалифицированную помощь и поддержку в решении любых правовых вопросов.")
                            self.__strapi_helper.change_payment_ticket_status(payment_id, "success")
                    elif amount == 3:
                        if float(amount) == math.ceil(float(transaction_amount) / 2) * 2 or math.ceil(float(transaction_amount) / 3) * 3:
                            await self.__tg_bot.send_message(manager['attributes']['telegram_id'], text=f"Транзакция за {transaction_date} на сумму {transaction_amount} успешно выполнена.")
                            await self.__tg_bot.send_message(chat_id=message.from_user.id, text=f"Транзакция за {transaction_date} на сумму {transaction_amount} успешно выполнена.")
                            await self.__tg_bot.send_message(chat_id=message.from_user.id, text=f"Оплата получена.")
                            await self.__tg_bot.send_message(chat_id=message.from_user.id, text=f"Благодарим Вас за выбор AV Legal. В случае возникновения дополнительных вопросов или потребности в дальнейшей консультации,  обращайтесь к нам. Наша команда всегда готова предоставить Вам квалифицированную помощь и поддержку в решении любых правовых вопросов.")
                            self.__strapi_helper.change_payment_ticket_status(payment_id, "success")
                    elif amount < 100:
                        if float(amount) == math.ceil(float(transaction_amount) / 2) * 2 or math.ceil(float(transaction_amount) / 3) * 3 or math.ceil(float(transaction_amount) / 4) * 4:
                            await self.__tg_bot.send_message(manager['attributes']['telegram_id'], text=f"Транзакция за {transaction_date} на сумму {transaction_amount} успешно выполнена.")
                            await self.__tg_bot.send_message(chat_id=message.from_user.id, text=f"Транзакция за {transaction_date} на сумму {transaction_amount} успешно выполнена.")
                            await self.__tg_bot.send_message(chat_id=message.from_user.id, text=f"Оплата получена.")
                            await self.__tg_bot.send_message(chat_id=message.from_user.id, text=f"Благодарим Вас за выбор AV Legal. В случае возникновения дополнительных вопросов или потребности в дальнейшей консультации,  обращайтесь к нам. Наша команда всегда готова предоставить Вам квалифицированную помощь и поддержку в решении любых правовых вопросов.")
                            self.__strapi_helper.change_payment_ticket_status(payment_id, "success")
                    else:
                        if float(amount) == math.ceil(float(transaction_amount) / 5) * 5:
                            await self.__tg_bot.send_message(manager['attributes']['telegram_id'], text=f"Транзакция за {transaction_date} на сумму {transaction_amount} успешно выполнена.")

                            await self.__tg_bot.send_message(chat_id=message.from_user.id, text=f"Оплата получена.")
                            await self.__tg_bot.send_message(chat_id=message.from_user.id, text=f"Благодарим Вас за выбор AV Legal. В случае возникновения дополнительных вопросов или потребности в дальнейшей консультации,  обращайтесь к нам. Наша команда всегда готова предоставить Вам квалифицированную помощь и поддержку в решении любых правовых вопросов.")
                            self.__strapi_helper.change_payment_ticket_status(payment_id, "success")
                else:
                    print("Txid не соответствует заданному значению.")
            else:
                await self.__tg_bot.send_message(chat_id=message.from_user.id, text=f"Транзакция не подтверждена.")

        print(transaction_chain)

    async def check_yoomoney_payment(self, message: Message):
        unpaid_payment_tickets = self.__strapi_helper.get_unpaid_payment_tickets_by_telegram_id(message.from_user.id)
        self.logger.info(unpaid_payment_tickets)
        no_payment = True
        for payment_ticket in unpaid_payment_tickets:
            payment = await self.__yoomoney_payment_helper.check_payment_from_user(message.from_user, payment_ticket) #error 
            print(f"User BH: {message.from_user.id}")
            print(f"Payment ticket BH: {payment_ticket['id']}")
            print(payment)
            if payment is not None:
                self.logger.info(f"Получена оплата: {payment.status} {payment.amount} {payment.label} "
                                 f"{payment.operation_id} {payment.datetime}")

                await message.answer("Оплата получена.")
                await message.answer(f"Благодарим Вас за выбор AV Legal. В случае возникновения дополнительных вопросов или потребности в дальнейшей консультации,  обращайтесь к нам. Наша команда всегда готова предоставить Вам квалифицированную помощь и поддержку в решении любых правовых вопросов.")
                await self.notify_manager_about_successful_payment(message.from_user, payment)


                self.__strapi_helper.change_payment_ticket_status(payment_ticket['id'], payment.status)
                self.__strapi_helper.save_yoomoney_payment_id_to_payment_ticket(
                    payment_ticket['id'],
                    payment.operation_id
                )
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

    async def notify_manager_about_successful_payment(self, user: User, payment):
        manager = self.__strapi_helper.get_manager_by_client_telegram_id(user.id)
        await self.__tg_bot.send_message(manager['attributes']['telegram_id'], f"Клиент оплатил услугу.\nВремя оплаты: {payment.datetime}\nСтатус транзакции: {payment.status}\nПолученная сумма: {payment.amount}\nID операции: {payment.operation_id}")



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
