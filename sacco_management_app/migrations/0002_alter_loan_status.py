# Generated by Django 5.1.6 on 2025-03-13 15:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sacco_management_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='loan',
            name='status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('Approved', 'approved'), ('Paid', 'Paid')], default='Pending', max_length=15),
        ),
    ]
