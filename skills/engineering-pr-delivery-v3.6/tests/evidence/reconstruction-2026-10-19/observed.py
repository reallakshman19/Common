from source import Order
order = Order()
order.apply(3)
print({'displayed_quantity': order.displayed_quantity, 'model_quantity': order.quantity, 'subtotal': order.subtotal()})
