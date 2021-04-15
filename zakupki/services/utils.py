import csv
from io import StringIO
from html.parser import HTMLParser
import datetime as dt

import requests
from django.http import HttpResponse

from zakupki.repositories.order import load_orders


class MLStripper(HTMLParser):

    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.text = StringIO()

    def handle_data(self, d):
        self.text.write(d)

    def get_data(self):
        return self.text.getvalue()


def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()


def date_format(date):
    return dt.datetime.strptime(date, "%d.%m.%Y")


def get_page(url, params=''):
    _headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8 application/signed-exchange;v=b3;q=0.9',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.41 Mobile Safari/537.36'
    }
    try:
        result = requests.get(url, headers=_headers, params=params).text
    except Exception:
        return 'Страница не найдена'
    return result


def url_generator(search_params: dict):
    s = search_params
    base_url = f'https://zakupki.gov.ru/epz/order/extendedsearch/rss.html?sortDirection=false'
    if s["customer_inn"]:
        base_url += f'&searchString={s["customer_inn"]}'
    if s["client_inn"]:
        base_url += f'&participantName={s["client_inn"]}'
    if s["keywords"]:
        base_url += f'&searchTextInAttachedFile={s["keywords"]}'
    if s["af"]:
        base_url += f'&af=on'
    if s["ca"]:
        base_url += f'&ca=on'
    if s["pc"]:
        base_url += f'&pc=on'
    if s["pa"]:
        base_url += f'&pa=on'
    if s["fz44"]:
        base_url += f'&fz44=on'
    if s["fz223"]:
        base_url += f'&fz223=on'
    if s["ppRf615"]:
        base_url += f'&ppRf615=on'
    if s["fz94"]:
        base_url += f'&fz94=on'
    if s["price_start"]:
        base_url += f'&priceFromGeneral={s["price_start"]}'
    if s["price_end"]:
        base_url += f'&priceToGeneral={s["price_end"]}'
    if s["date_start"]:
        base_url += f'&publishDateFrom={date_format(s["date_start"])}'
    if s["date_update"]:
        base_url += f'&updateDateFrom={date_format(s["date_update"])}'
    if s["date_end"]:
        base_url += f'&SubmissionCloseDateTo={date_format(s["date_end"])}'
    return base_url


def export_csv(customer_inn):
    response = HttpResponse(content_type='text/csv')
    writer = csv.writer(response)
    writer.writerow(['Заказчик', 'Номер закупки', 'Исполнитель', 'Наименование', 'Статус', 'ИКЗ', 'Цена', 'Закон',
                     'Дата размещения', 'Дата обновления', ' Цена контракта', 'Номер контракта', 'Реестровый номер',
                     'Статус', 'Подписан', 'Начало исполнения', 'Конец исполнения', 'Вложения закупки',
                     'Вложения контракта', 'Добавлен в парсер', 'Обновлен в парсере'])
    for order in load_orders(customer_inn=customer_inn):
        writer.writerow(
            [customer_inn, f'=HYPERLINK("{order.order_link}={order.reg_number}","{order.reg_number}")', order.client,
             order.title, order.order_status, order.order_ikz,
             order.order_price, order.order_law, order.order_published, order.order_update, order.contract_price,
             order.contract_number, order.contract_reestr_number, order.contract_status, order.contract_date_signature,
             order.contract_date_start, order.contract_date_end,
             f'=HYPERLINK("https://zakupki.gov.ru/epz/order/notice/ok504/view/documents.html?regNumber={order.reg_number}","Закупка")',
             f'=HYPERLINK("https://zakupki.gov.ru/epz/contract/contractCard/document-info.html?reestrNumber={order.contract_reestr_number}","Контракт")',
             order.created_at, order.updated_at]
        )

    response['Content-Disposition'] = f'attachment; filename="{customer_inn}.csv"'
    return response
