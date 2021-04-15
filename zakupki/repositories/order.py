from zakupki.models import Order


def load_orders(customer_inn='', reg_number=''):
    if customer_inn:
        return Order.objects.filter(customer__inn=customer_inn)
    elif reg_number:
        return Order.objects.get(reg_number=reg_number)
    else:
        return Order.objects.all()


def order_update_or_create(data):
    Order.objects.update_or_create(reg_number=data['reg_number'], defaults=data)
    return {'status': 'Закупка создана'}


def order_update(data):
    Order.objects.update_or_create(contract_reestr_number=data['contract_reestr_number'], defaults=data)
    return {'status': 'Закупка обновлена'}


def order_check_exists(reg_number):
    return Order.objects.filter(reg_number=reg_number).exists()
