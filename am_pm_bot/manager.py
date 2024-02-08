class Manager:
    def __init__(self, manager_id, name):
        self.manager_id = manager_id
        self.name = name

    def contact_user(self, user):
        raise NotImplementedError("This method needs to be implemented.")

    def create_payment_ticket(self, amount, user):
        raise NotImplementedError("This method needs to be implemented.")

    def cancel_payment_ticket(self, payment_ticket):
        raise NotImplementedError("This method needs to be implemented.")