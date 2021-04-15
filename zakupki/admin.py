from django.contrib import admin

# Register your models here.
from zakupki.models import Customer, Client, Order


@admin.register(Customer, Client, Order)
class AdminZakupki(admin.ModelAdmin):
    pass
