# Generated by Django 4.2.16 on 2024-10-31 12:46
# pylint: skip-file
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('financeapp', '0004_budget_alert_sent'),
    ]

    operations = [
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254)),
                ('subject', models.CharField(max_length=200)),
                ('message', models.TextField(validators=[django.core.validators.MaxLengthValidator(1000)])),
                ('date_submitted', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]