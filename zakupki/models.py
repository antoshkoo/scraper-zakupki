from django.db import models
from django.utils import timezone


class Customer(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название', db_index=True, blank=True)
    inn = models.IntegerField(verbose_name='ИНН', unique=True, db_index=True)
    ogrn = models.IntegerField(verbose_name='ОГРН', unique=True, db_index=True, blank=True)
    customer_id = models.IntegerField(unique=True, verbose_name='ID в госзакупках', blank=True)
    orders = models.IntegerField(verbose_name='Закупок', default=0, blank=True)
    is_active = models.BooleanField(default=True, verbose_name='Активный')


class Client(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название', db_index=True)
    inn = models.IntegerField(verbose_name='ИНН', unique=True, db_index=True)
    ogrn = models.IntegerField(verbose_name='ОГРН', unique=True, db_index=True)
    client_id = models.IntegerField(verbose_name='ID в госзакупках')
    is_active = models.BooleanField(default=True, verbose_name='Активный')


class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, db_index=True)
    client = models.CharField(max_length=15, db_index=True, blank=True, null=True)
    reg_number = models.CharField(max_length=50, verbose_name='Номер закупки', db_index=True, unique=True, blank=True, null=True)
    title = models.TextField(verbose_name='Наименование закупки', db_index=True, blank=True, null=True)
    order_status = models.CharField(max_length=255, verbose_name='Статус', blank=True, null=True)
    order_ikz = models.CharField(max_length=255, verbose_name='ИКЗ', unique=True, blank=True, null=True)
    order_price = models.DecimalField(max_digits=20, decimal_places=2, verbose_name='Начальная цена', blank=True, null=True)
    order_law = models.CharField(max_length=255, verbose_name='ФЗ', blank=True, null=True)
    order_published = models.DateField(verbose_name='Дата размещения', blank=True, null=True)
    order_update = models.DateField(verbose_name='Дата обновления', blank=True, null=True)
    order_link = models.CharField(max_length=250, blank=True, null=True)

    contract_price = models.DecimalField(max_digits=20, decimal_places=2, verbose_name='Сумма закупки', blank=True,
                                         null=True)
    contract_date_signature = models.DateField(verbose_name='Дата заключения', blank=True, null=True)
    contract_date_start = models.DateField(verbose_name='Начало исполнения', blank=True, null=True)
    contract_date_end = models.DateField(verbose_name='Конец исполнения', blank=True, null=True)
    contract_reestr_number = models.CharField(max_length=255, verbose_name='Реестровый номер', db_index=True, blank=True, null=True)
    contract_status = models.CharField(max_length=100, verbose_name='Статус контракта', blank=True, null=True)
    contract_number = models.CharField(max_length=15, verbose_name='Номер контракта', blank=True, null=True)
    files_order = models.TextField(verbose_name='Файлы закупки', blank=True, null=True)
    files_contract = models.TextField(verbose_name='Файлы контракта', blank=True, null=True)
    keywords = models.TextField(verbose_name='Поиск по ключевым словам', blank=True, null=True)

    created_at = models.DateField(default=timezone.now)
    updated_at = models.DateField(auto_now=True)
    parser_status = models.IntegerField(verbose_name='Уровень парсинга', default=0)
