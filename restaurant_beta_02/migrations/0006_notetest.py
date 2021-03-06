# Generated by Django 3.1 on 2020-08-19 21:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant_beta_02', '0005_datanotebase_max'),
    ]

    operations = [
        migrations.CreateModel(
            name='NoteTest',
            fields=[
                ('note_id', models.IntegerField(primary_key=True, serialize=False)),
                ('note', models.CharField(max_length=250, verbose_name='备注内容')),
                ('component', models.CharField(max_length=250, verbose_name='编号明细')),
            ],
            options={
                'verbose_name': '测试',
                'db_table': 'note_test',
                'managed': True,
            },
        ),
    ]
