from aiogram.types import User


class CryptoPaymentHelper:
    async def generate_payment_url(
            self,
            user_telegram_id: int,
            amount: float,
            currency: str,
            payment_ticket_id: int
        ):
        return "https://pastebin.com/raw/CND5701p"

