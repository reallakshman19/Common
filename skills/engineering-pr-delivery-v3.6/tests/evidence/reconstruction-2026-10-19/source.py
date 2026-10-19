class Order:
    def __init__(self):
        self.quantity = 2
        self.displayed_quantity = 2
        self.unit_price = 7

    def apply(self, quantity):
        self.displayed_quantity = quantity

    def subtotal(self):
        return self.quantity * self.unit_price
