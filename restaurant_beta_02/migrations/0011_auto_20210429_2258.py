# Generated by Django 3.1 on 2021-04-29 20:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant_beta_02', '0010_dataprint'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dataprint',
            name='print_type',
            field=models.IntegerField(verbose_name='打印类型'),
        ),
    ]