import re
import datetime as dt

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from ..repositories.customer import customer_update_or_create, load_customer
from ..repositories.order import order_update_or_create, order_update, order_check_exists, load_orders
from .utils import url_generator, strip_tags, get_page, date_format

HOST = 'https://zakupki.gov.ru/'

_option = webdriver.FirefoxOptions()
_option.set_preference('dom.webdriver.enabled', False)  # Отключение детектора с помощью WebDriver
_option.set_preference('dom.webnotifications.enabled', False)  # Отключение всплывающих уведомлений
_option.set_preference('media.volume_scale', '0.0')  # Отключение звуков
_option.headless = True  # Работа в фоне


"""
    Статусы парсера 'parser_status':
    0 - Есть новые закупки, надо получить данные контрактов (по нему запускаем ContractParser)
    1 - Надо получить полные данные контракта (по нему запускаем ContractParserFull)
    11 - Контракт спаршен, но еще незаключен (надо перепроверить через какое-то время)
    12 - Контракт спаршен закупка произведена, но еще не поставлена исполнителем (надо перепроверить через какое-то время)
    91 - Контракт спаршен и закупка завершена (больше не производится никаких действий)
    92 - Контакт спаршен и закупка отменена (больше не производится никаких действий)
    93 - Контракт спаршен и закупка аннулирована (больше не производится никаких действий)
"""


class CustomerParser:
    def __init__(self):
        self.browser = webdriver.Firefox(options=_option)

    def get_page(self):
        """Загружаем страницу поиска закупок"""
        self.browser.get('http://zakupki.gov.ru/epz/order/extendedsearch/results.html')

    def user_actions(self, limit: int):
        """Эмуляриуем поведение пользователя"""
        html = self.browser.find_element_by_tag_name('html')
        for i in range(limit):
            html.send_keys(Keys.DOWN)

    def search_input(self, inn: int):
        """Ищем поле ввода для поиска по инн или огрн"""
        search_input_xpath = '/html/body/form/section[1]/div/div/div/div[2]/div/div/input'
        self.browser.find_element_by_xpath(search_input_xpath).send_keys(inn)

    def search_button(self):
        """Ищем кнопку поиска и нажимаем на нее"""
        search_button_xpath = '/html/body/form/section[1]/div/div/div/div[2]/div/div/button'
        self.browser.find_element_by_xpath(search_button_xpath).click()

    def count_orders(self):
        """Получаем количество закупок"""
        orders_total_xpath = '/html/body/form/section[2]/div/div/div[1]/div[1]/div[2]'
        orders_total = self.browser.find_element_by_xpath(orders_total_xpath).text
        return ''.join([i for i in orders_total if i.isdigit()])

    def get_gos_id(self):
        """Получаем внутренний ID на госзакупках"""
        customer_xpath = '/html/body/form/section[2]/div/div/div[1]/div[3]/div[1]/div/div[1]/div[2]/div[2]/div[2]/a'
        return self.browser.find_element_by_xpath(customer_xpath).get_attribute('href').split('=')[1]

    def get_name(self):
        """Получаем название"""
        name_xpath = '/html/body/form/section[2]/div/div/div[1]/div[3]/div[1]/div/div[1]/div[2]/div[2]/div[2]/a'
        return self.browser.find_element_by_xpath(name_xpath).text

    def get_profile_page(self, gos_id: int):
        """Загружаем страницу профиля закупщика"""
        self.browser.get(f'https://zakupki.gov.ru/epz/organization/view/info.html?organizationId={gos_id}')

    def get_ogrn(self):
        """Получаем ОГРН"""
        ogrn_xpath = '/html/body/div[2]/div/div[1]/div[2]/div[2]/div/div/div/div[1]/div[2]/div[2]/div/div[1]/div[2]'
        return self.browser.find_element_by_xpath(ogrn_xpath).text

    def parse(self, inn: int):
        self.get_page()
        self.user_actions(3)
        self.search_input(inn)
        self.search_button()
        orders_total = self.count_orders()
        gos_id = self.get_gos_id()
        name = self.get_name()

        self.get_profile_page(gos_id)
        self.user_actions(2)
        ogrn = self.get_ogrn()

        self.browser.close()
        customer_update_or_create(
            {
                'name': name,
                'customer_id': gos_id,
                'orders': orders_total,
                'inn': inn,
                'ogrn': ogrn
            })
        return {'status': 'Заказчик обновлен'}


class OrderParser:
    def __init__(self, search_params, save):
        self.search_params = search_params
        self.save = save

    def get_reg_number(self, item):
        """Номер закупки"""
        content = item.find('title').get_text()
        result = re.search(r"\d{10,30}", content)[0]
        return result if result else '-'

    def get_link(self, item):
        """Ссылка на закупку (нет закрывающего тега < link > в response)"""
        pattern = "/(.*?)="
        result = re.search(pattern, item.text)
        return result.group(1) if result else '-'

    def get_description(self, item):
        """Получаем нужный кусок из описания"""
        desc = item.find('description').get_text(strip=True)
        result = strip_tags(desc.split('</strong></a>')[1])
        result = ' '.join(result.split())
        return result

    def get_dates(self, desc):
        """Дата размещения и обновления"""
        result = re.findall(r'\d{2}\.\d{2}\.\d{4}', desc)
        date_start = dt.datetime.strptime(result[0], "%d.%m.%Y")
        date_end = dt.datetime.strptime(result[1], "%d.%m.%Y")
        return [date_start, date_end]

    def get_title(self, desc):
        """Название объекта"""
        pattern = "Наименование объекта закупки: (.*?)Размещение выполняется"
        result = re.search(pattern, desc)
        return result.group(1) if result else '-'

    def get_start_price(self, desc):
        """Начальная цена"""
        pattern = "Начальная цена контракта: (.*?) Валюта:"
        result = re.search(pattern, desc)
        return result.group(1) if result else '-'

    def get_law(self, desc):
        """Закон закупки"""
        pattern = "выполняется по: (.*?)Наименование Заказчика: "
        result = re.search(pattern, desc)
        return result.group(1) if result else '-'

    def get_status(self, desc):
        """Статус закупки"""
        pattern = "Этап размещения: (.*?)Идентификационный код"
        result = re.search(pattern, desc)
        return result.group(1) if result else '-'

    def get_customer(self):
        """Получаем заказчика"""
        if self.save:
            customer = load_customer(inn=self.search_params['customer_inn'])
        else:
            customer = None
        return customer

    def get_orders(self, items):
        """Собираем данные о закупках"""
        orders = []
        for item in items:
            reg_number = self.get_reg_number(item)
            client_search = self.search_params['client_inn']
            keywords_search = self.search_params['keywords']

            if order_check_exists(reg_number):
                order = load_orders(reg_number=reg_number)
                client = order.client if client_search == '' else client_search
                keywords = ''.join(f'{order.keywords} {keywords_search}'.split())
                print(keywords)
            else:
                client = self.search_params['client_inn']
                keywords = self.search_params['keywords']

            desc = self.get_description(item)
            orders.append(
                {
                    'customer': self.get_customer(),
                    'client': client,
                    'reg_number': reg_number,
                    'keywords': keywords,
                    'order_link': HOST + self.get_link(item),
                    'order_published': self.get_dates(desc)[0],
                    'order_update': self.get_dates(desc)[1],
                    'title': self.get_title(desc),
                    'order_price': self.get_start_price(desc),
                    'order_law': self.get_law(desc),
                    'order_status': self.get_status(desc),
                }
            )
        return orders

    def parse(self):
        url = url_generator(self.search_params)
        page = get_page(url)
        soup = BeautifulSoup(page, 'lxml')
        items = soup.find_all('item')
        orders = self.get_orders(items)

        if len(orders) > 0:
            if self.save:
                for order in orders:
                    order_update_or_create(order)
                return orders
            else:
                return orders
        else:
            return {'error': 'Ничего не найдено'}


class ContractParser:
    def get_reestr_number(self, item):
        result = item.find('title').get_text().split(' ')[1]
        return result or '-'

    def get_description(self, item):
        result = item.find('description').get_text(strip=True)
        result = strip_tags(result.split('</a>')[1])
        return result or '-'

    def get_number(self, desc):
        pattern = "Контракт №: (.*?) от"
        result = re.search(pattern, desc)
        return result.group(1) if result else '-'

    def get_price(self, desc):
        pattern = "Цена контракта: (.*?) Валюта:"
        result = re.search(pattern, desc)
        return result.group(1) if result else '-'

    def get_status(self, desc):
        pattern = "Статус контракта: (.*?)Контракт"
        result = re.search(pattern, desc)
        return result.group(1) if result else '-'

    def get_date_signature(self, desc):
        pattern = " от (.*?)Цена контракта: "
        result = re.search(pattern, desc).group(1)
        result = dt.datetime.strptime(result, "%d.%m.%Y")
        return result or '-'

    def parse(self, reg_number):
        url = f'https://zakupki.gov.ru/epz/contract/search/rss?searchString=&orderNumber={reg_number}'
        page = get_page(url)
        soup = BeautifulSoup(page, 'lxml')
        item = soup.find('item')
        if item:
            desc = self.get_description(item)
            data = {
                'reg_number': reg_number,
                'contract_reestr_number': self.get_reestr_number(item),
                'contract_number': self.get_number(desc),
                'contract_price': self.get_price(desc).replace(u'\xa0', u'').replace(',', '.'),
                'contract_status': self.get_status(desc),
                'contract_date_signature': self.get_date_signature(desc),
                'contract_date_start': self.get_date_signature(desc),
                'parser_status': 1
            }
            order_update_or_create(data)
            return {'status': f'{reg_number} - добавлен контракт'}
        else:
            data = {
                'reg_number': reg_number,
                'parser_status': 11
            }
            order_update_or_create(data)
            return {'status': f'{reg_number} - нет контракта'}


class ContractParserFull:
    def __init__(self):
        self.browser = webdriver.Firefox(options=_option)

    def __del__(self):
        self.browser.close()

    def get_page(self, contract_reestr_number):
        """Загружаем страницу поиска закупок"""
        self.browser.get(f'https://zakupki.gov.ru/epz/contract/contractCard/common-info.html?reestrNumber={contract_reestr_number}')

    def user_actions(self, limit: int):
        """Эмуляриуем поведение пользователя"""
        html = self.browser.find_element_by_tag_name('html')
        for i in range(limit):
            html.send_keys(Keys.DOWN)

    def date_start(self):
        """Дата заключения контракта"""
        contract_date_start_xpath = './/span[@class="cardMainInfo__title" and text()="Заключение контракта"]/../span[2]'
        result = self.browser.find_element_by_xpath(contract_date_start_xpath).text
        return result or '01.01.2001'

    def date_work_start(self):
        """Начало исполнения контракта"""
        contract_date_work_start_xpath = './/span[@class="section__title" and text()="Дата начала исполнения контракта"]/parent::section/span[2]'
        try:
            result = self.browser.find_element_by_xpath(contract_date_work_start_xpath).text
        except:
            result = '01.01.2001'
        return result

    def date_work_end(self):
        """Срок исполнения контракта"""
        contract_date_end_xpath = './/span[@class="section__title" and text()="Дата окончания исполнения контракта"]/../span[2]'
        result = self.browser.find_element_by_xpath(contract_date_end_xpath).text
        return result or '01.01.2001'

    def client_inn(self):
        """ИНН поставщика"""
        contract_client_inn_xpath = './/span[@class="grey-main-light" and text()="ИНН:"]/../span[2]'
        result = self.browser.find_element_by_xpath(contract_client_inn_xpath).text
        return result or '-'

    def parse(self, contract_reestr_number):
        self.get_page(contract_reestr_number)
        self.user_actions(3)
        contract_date_start = self.date_start()
        contract_date_end = self.date_work_start()
        contract_date_work_start = self.date_work_end()
        contract_client_inn = self.client_inn()

        order_update({'contract_reestr_number': contract_reestr_number, 'parser_status': 2})
        order_update(
            {
                'contract_reestr_number': contract_reestr_number,
                'contract_date_start': date_format(contract_date_start),
                'contract_date_end': date_format(contract_date_end),
                'contract_date_work_start': date_format(contract_date_work_start),
                'client': contract_client_inn,
                'parser_status': 2
            })
        return {'status': f'Данные контракта {contract_reestr_number} обновлены'}
