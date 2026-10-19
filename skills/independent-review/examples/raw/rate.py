def estimate(subtotal, delivery):
    if any(type(value) is not int or value < 0 for value in (subtotal, delivery)):
        raise ValueError('nonnegative integer cents required')
    discount = subtotal // 10 if subtotal + delivery >= 10000 else 0
    return subtotal - discount + delivery
