from os import getenv
import requests
from aiogram.types import User


class CryptoPaymentHelper:
    DOMAIN = "av_pm_bot"
    API_TOKEN = getenv("PLISIO_API_TOKEN")
    API_HOST = 'https://plisio.net/api/v1'

    def get_invoice_url(
            self,
            source_amount: float,
            order_number: int,
            order_name: str,
            currency="USDT"
    ):
        return requests.get(
            url=f"{self.API_HOST}/invoices/new?source_currency=USD"
                f"&source_amount={source_amount}"
                f"&order_number={order_number}"
                f"&currency={currency}"
                f"&email=av_pm_bot@paymet.com"
                f"&order_name={order_name}"
                f"&api_key={self.API_TOKEN}"
        ).json()["data"]["invoice_url"]

    async def generate_payment_url(
            self,
            user_telegram_id: int,
            amount: float,
            currency: str,
            payment_ticket_id: int
    ):
        return self.get_invoice_url(
            source_amount=amount,
            order_number=payment_ticket_id,
            order_name=self.__generate_order_name(
                user_telegram_id,
                payment_ticket_id
            )
        )

    def __generate_order_name(self, telegram_id: int, payment_ticket_id: int):
        return f"{self.DOMAIN} | payment from: {telegram_id} | payment ticket id: {payment_ticket_id}"

    async def __calculate_amount_based_on_currency(self, amount: float, currency: str):
        result = {
            "rub": round(amount / self.__get_usdt_value_to_rub(), 2),
            "руб": round(amount / self.__get_usdt_value_to_rub(), 2),
            "usdt": amount,
            "usd": amount,
        }

        return result[currency]

    def __get_usdt_value_to_rub(self):
        return 90

    async def check_payment_from_user(self, plisio_invoice_id: str):
        invoice = requests.get(
            url=f"{self.API_HOST}/operations/{plisio_invoice_id}"
                f"&api_key={self.API_TOKEN}"
        ).json()

        if invoice['status'] == "success":
            return invoice['data']
        else:
            return None
