# Generated by Django 3.1 on 2021-05-21 19:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant_beta_02', '0014_dataticket_ticket_restaurant_count'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dataprint',
            name='print_content',
            field=models.TextField(max_length=65535, verbose_name='打印内容'),
        ),
    ]
