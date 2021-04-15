from django import forms
from datetime import datetime as dt


class CustomerCreateForm(forms.Form):
    inn = forms.IntegerField(label='ИНН', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ИНН'}))


class OrderSearchForm(forms.Form):
    input = forms.TextInput(attrs={'class': 'form-control'})
    checkbox = forms.CheckboxInput(attrs={'class': 'form-check-input'})
    date = forms.DateInput(attrs={
        'class': 'form-control',
        'type': 'date',
        'min': "2014-01-01",
        'max': dt.today().date(),
        'pattern': "[0-9]{4}-[0-9]{2}-[0-9]{2}",
    })

    customer_inn = forms.IntegerField(label='ИНН заказчика', required=False, widget=input)
    client_inn = forms.IntegerField(label='ИНН поставщика', required=False, widget=input)
    keywords = forms.CharField(label='Ключевые слова', required=False, widget=input)

    af = forms.BooleanField(help_text='Подача заявок', initial=True, required=False, widget=checkbox)
    ca = forms.BooleanField(help_text='Работа комиссии', initial=True, required=False, widget=checkbox)
    pc = forms.BooleanField(help_text='Закупка завершена', initial=True, required=False, widget=checkbox)
    pa = forms.BooleanField(help_text='Закупка отменена', initial=True, required=False, widget=checkbox)

    fz44 = forms.BooleanField(help_text='44-ФЗ', initial=True, required=False, widget=checkbox)
    fz223 = forms.BooleanField(help_text='223-ФЗ', required=False, widget=checkbox, disabled=True)
    ppRf615 = forms.BooleanField(help_text='ПП РФ 615', required=False, widget=checkbox, disabled=True)
    fz94 = forms.BooleanField(help_text='94-ФЗ', required=False, widget=checkbox, disabled=True)

    price_start = forms.CharField(help_text='Стоимость от:', required=False, widget=input)
    price_end = forms.CharField(help_text='Стоимость до:', required=False, widget=input)

    date_start = forms.DateField(help_text='Дата создания от:', required=False, widget=date)
    date_update = forms.DateField(help_text='Дата обновления до:', required=False, widget=date)
    date_end = forms.DateField(help_text='Дата завершения до:', required=False, widget=date)
