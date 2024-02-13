from am_pm_bot import getenv
from am_pm_bot.payment_helper import Quickpay, Client
from am_pm_bot.handlers import User
import datetime


class YoomoneyPaymentHelper:
    DOMAIN = "av_pm_bot"

    def __init__(self):
        self.token = getenv("YOOMONEY_TOKEN")
        self.yoomoney_client = Client(self.token)

    def __generate_yoomoney_label(self, telegram_id: int, payment_ticket_id: int):
        return f"{self.DOMAIN} | payment from: {telegram_id} | payment ticket id: {payment_ticket_id}"

    async def generate_payment_url(
            self,
            telegram_id: int,
            amount: float,
            currency: str,
            payment_ticket_id: int
    ):
        return Quickpay(
            receiver="4100117136887722",
            quickpay_form="shop",
            targets="Sponsor this project",
            paymentType="SB",
            sum=await self.__calculate_amount_based_on_currency(amount, currency),
            label=self.__generate_yoomoney_label(telegram_id, payment_ticket_id),
            successURL="https://t.me/av_pm_bot"
        ).base_url

    async def __calculate_amount_based_on_currency(self, amount: float, currency: str):
        result = {
            "rub": amount,
            "руб": amount,
            "usdt": round(amount * self.__get_usdt_value_to_rub(), 2),
            "usd": round(amount * self.__get_usdt_value_to_rub(), 2),
        }

        return result[currency.lower()]

    def __get_usdt_value_to_rub(self):
        return 90

    async def check_payment_from_user(self, from_user: User, payment_ticket: dict):
        history = self.yoomoney_client.operation_history(
            records=1, label=self.__generate_yoomoney_label(from_user.id, payment_ticket['id'])
        )

        for operation in history.operations:
            return operation
