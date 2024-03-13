from am_pm_bot import getenv, requests, logging
from am_pm_bot.callback_data.payment_ticket import PaymentTicketCallback
from am_pm_bot.strapi_helper import Request, User


class StrapiHelper:

    CLIENT_ENTITY_NAME_PLURAL = 'clients'
    MANAGER_ENTITY_NAME_PLURAL = 'managers'
    REQUEST_ENTITY_NAME_PLURAL = 'requests'
    PAYMENT_TICKET_ENTITY_PLURAL = 'payment-tickets'

    def __init__(self):
        self.token = getenv("STRAPI_TOKEN")
        self.host = getenv("STRAPI_HOST") if getenv("STRAPI_HOST")[-1] != "/" else getenv("STRAPI_HOST")[:-2:]
        self.AUTH_HEADER = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        self.logger = logging.getLogger("strapi_helper")
        self.logger.setLevel(logging.INFO)

    def __send_post(self, url: str, payload: dict):
        result = requests.post(
            url=url, json=payload, headers=self.AUTH_HEADER
        )
        self.logger.info(f"POST {url} resulted: {result.json()}")
        return result

    def __send_put(self, url: str, payload: dict):
        result = requests.put(
            url=url, json=payload, headers=self.AUTH_HEADER
        )
        self.logger.info(f"PUT {url} resulted: {result.json()}")
        return result

    def __send_get(self, url: str):
        result = requests.get(
            url=url, headers=self.AUTH_HEADER
        )
        self.logger.info(f"GET {url} resulted: {result.json()}")
        return result

    def get_client_by_telegram_id(self, telegram_id: int):
        return self.__send_get(
            url=f"{self.host}/api/{self.CLIENT_ENTITY_NAME_PLURAL}?"
                f"filters[$and][0][telegram_id][$eq]={telegram_id}"
        ).json()["data"][0]

    def get_manager_by_telegram_id(self, telegram_id: int):
        return self.__send_get(
            url=f"{self.host}/api/{self.MANAGER_ENTITY_NAME_PLURAL}?"
                f"filters[$and][0][telegram_id][$eq]={telegram_id}&"
                f"populate=*"
        ).json()["data"][0]

    def get_manager_by_client_telegram_id(self, client_telegram_id: int):
        return self.__send_get(
            url=f"{self.host}/api/{self.MANAGER_ENTITY_NAME_PLURAL}?"
                f"filters[$and][0][client][telegram_id][$eq]={client_telegram_id}&"
                f"populate=*"
        ).json()["data"][0]

    def get_client_by_manager_telegram_id(self, manager_telegram_id: int):
        managers_list = self.__send_get(
            url=f"{self.host}/api/{self.MANAGER_ENTITY_NAME_PLURAL}?"
                f"[$and][0][telegram_id][$eq]={manager_telegram_id}"
                f"&populate=client"
        ).json()["data"]
        
        manager_telegram_id_str = str(manager_telegram_id)
        target_telegram_id = manager_telegram_id_str

        index = None
        for i, item in enumerate(managers_list):
            if item['attributes']['telegram_id'] == target_telegram_id:
                index = i
                break

        if index is not None:
            found_item = managers_list[index]
            print("Number:", index)
            print("Element content:", found_item)
        else:
            print("Didn't find")

        return self.__send_get(
            url=f"{self.host}/api/{self.MANAGER_ENTITY_NAME_PLURAL}?"
                f"[$and][0][telegram_id][$eq]={manager_telegram_id}"
                f"&populate=client"
        ).json()["data"][index]['attributes']['client']['data']

    def get_list_of_managers(self):
        return self.__send_get(
            url=f"{self.host}/api/{self.MANAGER_ENTITY_NAME_PLURAL}"
        ).json()["data"]

    def get_unpaid_payment_tickets_by_telegram_id(self, telegram_id: int):
        return self.__send_get(
            url=f"{self.host}/api/{self.PAYMENT_TICKET_ENTITY_PLURAL}?"
                f"filters[$and][0][client][telegram_id][$eq]={telegram_id}&"
                f"filters[$and][1][status][$eq]=unpaid&"
                f"populate=client"
        ).json()["data"]

    def save_client_info(self, user: User):
        json_body = {
            "data": {
                "telegram_id": user.id,
                "first_name": user.first_name if user.first_name is not None and user.first_name != "None" else "",
                "last_name": user.last_name if user.last_name is not None and user.last_name != "None" else "",
                "telegram_username": user.username if user.username is not None and user.username != "None" else ""
            }
        }

        return self.__send_post(url=f"{self.host}/api/{self.CLIENT_ENTITY_NAME_PLURAL}", payload=json_body)

    def save_request_info(self, request: Request):
        json_body = {
            "data": {
                "status": request.status,
                "client_description": request.client_description,
                "client": {
                    "connect": [{"id": request.strapi_id}]
                }
            }
        }


        return self.__send_post(url=f"{self.host}/api/{self.REQUEST_ENTITY_NAME_PLURAL}", payload=json_body)

    def save_payment_ticket_info(self, payment_ticket: PaymentTicketCallback):
        json_body = {
            "data": {
                "amount": payment_ticket.amount,
                "status": "unpaid",
                "client": {
                    "connect": [{"id": self.get_client_by_telegram_id(payment_ticket.telegram_id)['id']}]
                }
            }
        }

        return self.__send_post(url=f"{self.host}/api/{self.PAYMENT_TICKET_ENTITY_PLURAL}", payload=json_body).json()

    def save_payment_ticket_crypto_invoice_id(self, payment_ticket_id: int, payment_url: str):
        json_body = {
            "data": {
                "plisio_invoice_id": payment_url.removeprefix("https://plisio.net/invoice/"),
            }
        }

        return self.__send_put(url=f"{self.host}/api/{self.PAYMENT_TICKET_ENTITY_PLURAL}/{payment_ticket_id}",
                               payload=json_body).json()

    def connect_manager_to_client(self, manager_telegram_id: int, client_telegram_id: int):
        manager = self.get_manager_by_telegram_id(manager_telegram_id)
        client = self.get_client_by_telegram_id(client_telegram_id)
        print(manager, client)
        self.logger.info(f"Connecting {manager['id']} with {client['id']}")

        json_body = {
            "data": {
                "client": {
                    "connect": [{"id": client['id']}],
                }
            }
        }
        try:
            json_body['data']['client']['disconnect'] = [{"id": manager['attributes']['client']['data']['id']}]
        except TypeError:
            pass

        return self.__send_put(url=f"{self.host}/api/{self.MANAGER_ENTITY_NAME_PLURAL}/{manager['id']}", payload=json_body)

    def disconnect_manager_from_client(self, manager_telegram_id: int):
        manager = self.get_manager_by_telegram_id(manager_telegram_id)
        client = manager['attributes']['client']['data']

        self.logger.info(f"Disconnecting {manager['id']} from {client['id']}")

        json_body = {
            "data": {
                "client": {
                    "disconnect": [{"id": client['id']}]
                }
            }
        }

        return self.__send_put(url=f"{self.host}/api/{self.MANAGER_ENTITY_NAME_PLURAL}/{manager['id']}", payload=json_body)

    def change_payment_ticket_status(self, payment_ticket_id: int, status: str):
        json_body = {
            "data": {
                "status": status
            }
        }

        return self.__send_put(url=f"{self.host}/api/{self.PAYMENT_TICKET_ENTITY_PLURAL}/{payment_ticket_id}",
                               payload=json_body)

    def save_yoomoney_payment_id_to_payment_ticket(self, payment_ticket_id: int, operation_id: str):
        json_body = {
            "data": {
                "yoomoney_operation_id": operation_id
            }
        }

        return self.__send_put(url=f"{self.host}/api/{self.PAYMENT_TICKET_ENTITY_PLURAL}/{payment_ticket_id}",
                               payload=json_body)


if __name__ == '__main__':
    s = StrapiHelper()
    print(s.token)
    print(s.host)
