# Generated by Django 5.1.6 on 2025-03-13 18:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sacco_management_app', '0004_remove_transaction_member_transaction_account_number_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='insurance',
            name='account_number',
            field=models.CharField(default='00000000', max_length=8, unique=True),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='account_number',
            field=models.CharField(default='00000000', max_length=8, unique=True),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='receipt_number',
            field=models.CharField(default='invalid', max_length=10, unique=True),
        ),
    ]
