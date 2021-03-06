# Generated by Django 3.1.7 on 2021-03-30 11:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('zakupki', '0006_auto_20210330_1346'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='date_end',
            new_name='contract_date_end',
        ),
        migrations.RenameField(
            model_name='order',
            old_name='date_signature',
            new_name='contract_date_signature',
        ),
        migrations.RenameField(
            model_name='order',
            old_name='date_start',
            new_name='contract_date_start',
        ),
        migrations.RenameField(
            model_name='order',
            old_name='end_price',
            new_name='contract_price',
        ),
        migrations.RenameField(
            model_name='order',
            old_name='ikz',
            new_name='order_ikz',
        ),
        migrations.RenameField(
            model_name='order',
            old_name='law',
            new_name='order_law',
        ),
        migrations.RenameField(
            model_name='order',
            old_name='link',
            new_name='order_link',
        ),
        migrations.RenameField(
            model_name='order',
            old_name='start_price',
            new_name='order_price',
        ),
        migrations.RenameField(
            model_name='order',
            old_name='date_published',
            new_name='order_published',
        ),
        migrations.RenameField(
            model_name='order',
            old_name='status',
            new_name='order_status',
        ),
        migrations.RenameField(
            model_name='order',
            old_name='date_update',
            new_name='order_update',
        ),
        migrations.RemoveField(
            model_name='order',
            name='hash',
        ),
    ]
