# Generated by Django 3.2.6 on 2021-09-15 12:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spyfall', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Players',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('room_id', models.CharField(max_length=200)),
                ('players', models.CharField(max_length=200)),
                ('names', models.CharField(max_length=200)),
            ],
        ),
    ]
