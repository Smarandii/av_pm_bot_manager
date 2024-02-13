from am_pm_bot.handlers import User


class Request:
    def __init__(self, user: User, strapi_id: int, client_description: str, budget: int, status: str = None):
        self.user = user
        self.strapi_id = strapi_id
        self.client_description = client_description
        self.budget = budget
        self.status = "new" if status is None else status
