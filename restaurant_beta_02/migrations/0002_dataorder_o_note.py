# Generated by Django 3.1 on 2020-08-07 22:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant_beta_02', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='dataorder',
            name='o_note',
            field=models.ForeignKey(db_column='o_note', default=1, on_delete=django.db.models.deletion.CASCADE, to='restaurant_beta_02.dataspecialnote'),
        ),
    ]
