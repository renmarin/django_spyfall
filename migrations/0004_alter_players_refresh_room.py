# Generated by Django 3.2.6 on 2021-09-22 17:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spyfall', '0003_players_refresh_room'),
    ]

    operations = [
        migrations.AlterField(
            model_name='players',
            name='refresh_room',
            field=models.BooleanField(default=False),
        ),
    ]
