from zakupki.models import Customer


def load_customer(inn=''):
    if inn:
        return Customer.objects.get(inn=inn)
    else:
        return Customer.objects.all()


def customer_update_or_create(data):
    Customer.objects.update_or_create(inn=data['inn'], defaults=data)
    return {'status': 'Заказчик обновлен'}
