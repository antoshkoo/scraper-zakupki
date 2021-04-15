# Generated by Django 3.1.7 on 2021-03-25 13:50

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('zakupki', '0004_auto_20210321_0000'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='amount',
            new_name='end_price',
        ),
        migrations.RemoveField(
            model_name='order',
            name='number',
        ),
        migrations.AddField(
            model_name='order',
            name='created_at',
            field=models.DateField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='order',
            name='date_update',
            field=models.DateField(blank=True, null=True, verbose_name='Дата обновления'),
        ),
        migrations.AddField(
            model_name='order',
            name='hash',
            field=models.TextField(blank=True, max_length=150, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='ikz',
            field=models.PositiveBigIntegerField(blank=True, null=True, unique=True, verbose_name='ИКЗ'),
        ),
        migrations.AddField(
            model_name='order',
            name='law',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='ФЗ'),
        ),
        migrations.AddField(
            model_name='order',
            name='link',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='reg_number',
            field=models.PositiveBigIntegerField(blank=True, db_index=True, null=True, unique=True, verbose_name='Номер закупки'),
        ),
        migrations.AddField(
            model_name='order',
            name='start_price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True, verbose_name='Начальная цена'),
        ),
        migrations.AddField(
            model_name='order',
            name='updated_at',
            field=models.DateField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='client',
            field=models.CharField(blank=True, db_index=True, max_length=15, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='title',
            field=models.TextField(blank=True, db_index=True, null=True, verbose_name='Наименование закупки'),
        ),
    ]
