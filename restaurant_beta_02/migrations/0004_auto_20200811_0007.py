# Generated by Django 3.1 on 2020-08-10 22:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant_beta_02', '0003_auto_20200808_0054'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dataorder',
            name='code',
            field=models.ForeignKey(db_column='code', on_delete=django.db.models.deletion.CASCADE, related_name='orders', to='restaurant_beta_02.datadish', to_field='dcode'),
        ),
    ]
