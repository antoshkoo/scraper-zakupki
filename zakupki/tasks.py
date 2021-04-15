from time import sleep

from fbk_gos.celery import app
from zakupki.models import Order

from zakupki.services.parser import ContractParser, ContractParserFull


@app.task
def get_contract_short():
    item = Order.objects.filter(parser_status=0).values_list('reg_number').last()
    if item:
        ContractParser().parse(str(item[0]))
        return f'Short contract for {item[0]} done'
    else:
        return 'No orders to get short contract'


@app.task
def get_contract_full():
    item = Order.objects.filter(
        parser_status=1,
        contract_reestr_number__gt='',
        contract_reestr_number__isnull=False).values_list('contract_reestr_number', 'reg_number').last()
    if item:
        ContractParserFull().parse(str(item[0]))
        return f'Full contract for {item[1]} done'
    else:
        return 'No orders to get full contract'
