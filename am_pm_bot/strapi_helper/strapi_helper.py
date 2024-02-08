from am_pm_bot import getenv, requests, logging
from am_pm_bot.strapi_helper import Request, User


class StrapiHelper:

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
        return requests.post(
            url=url, json=payload, headers=self.AUTH_HEADER
        )

    def __send_put(self, url: str, payload: dict):
        return requests.put(
            url=url, json=payload, headers=self.AUTH_HEADER
        )

    def __send_get(self, url: str):
        return requests.get(
            url=url, headers=self.AUTH_HEADER
        )

    def get_client_by_telegram_id(self, telegram_id: int):
        return self.__send_get(
            url=f"{self.host}/api/clients?filters[$and][0][telegram_id][$eq]={telegram_id}"
        ).json()["data"][0]

    def get_manager_by_telegram_id(self, telegram_id: int):
        return self.__send_get(
            url=f"{self.host}/api/managers?filters[$and][0][telegram_id][$eq]={telegram_id}&populate=*"
        ).json()["data"][0]

    def get_manager_by_client_telegram_id(self, client_telegram_id: int):
        return self.__send_get(
            url=f"{self.host}/api/managers?filters[$and][0][client][telegram_id][$eq]={client_telegram_id}&populate=*"
        ).json()["data"][0]

    def get_list_of_managers(self):
        return self.__send_get(
            url=f"{self.host}/api/managers"
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

        return self.__send_post(url=f"{self.host}/api/clients", payload=json_body)

    def save_request_info(self, request: Request):
        json_body = {
            "data": {
                "status": request.status,
                "client_description": request.client_description,
                "budget": request.budget,
                "client": {
                    "connect": [{"id": request.strapi_id}]
                }
            }
        }

        return self.__send_post(url=f"{self.host}/api/requests", payload=json_body)

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

        return self.__send_put(url=f"{self.host}/api/managers/{manager['id']}", payload=json_body)

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

        return self.__send_put(url=f"{self.host}/api/managers/{manager['id']}", payload=json_body)


if __name__ == '__main__':
    s = StrapiHelper()
    print(s.token)
    print(s.host)
